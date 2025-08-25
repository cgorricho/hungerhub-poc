#!/usr/bin/env python3
"""
Full Data Extractor for HungerHub POC - Production Implementation
Based on proven methods from optimization notebook research

Implements sequential extraction strategy that achieved 1,100+ rows/sec performance
Extracts complete tables (no sampling) from Oracle database

Author: HungerHub POC Team
Date: August 2025
Version: 1.0 - Production Implementation
"""

import os
import sys
import time
import gc
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import cx_Oracle
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Initialize Oracle client if explicitly configured via environment
try:
    lib_dir = os.getenv('ORACLE_CLIENT_LIB')
    if lib_dir:
        cx_Oracle.init_oracle_client(lib_dir=lib_dir)
except Exception:
    # Client already initialized or using environment variables (LD_LIBRARY_PATH)
    pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FullDataExtractor:
    """
    Production-grade Oracle data extractor implementing proven sequential strategy
    
    Based on notebook research that achieved:
    - 1,100+ rows/sec throughput
    - 451K+ records extracted in 6.87 minutes
    - 100% success rate on high-priority tables
    """
    
    def __init__(self, config_path: str = 'config/.env'):
        """Initialize extractor with Oracle connection parameters"""
        load_dotenv(config_path)
        
        # Oracle connection configuration with alignment between CHOICE_* and ORACLE_* env vars
        self.host = os.getenv('CHOICE_ORACLE_HOST') or os.getenv('ORACLE_HOST')
        self.port = os.getenv('CHOICE_ORACLE_PORT', os.getenv('ORACLE_PORT', '1521'))
        self.service = os.getenv('CHOICE_ORACLE_SERVICE_NAME') or os.getenv('ORACLE_SERVICE_NAME')
        self.user = os.getenv('CHOICE_USERNAME') or os.getenv('ORACLE_USERNAME')
        self.password = os.getenv('CHOICE_PASSWORD') or os.getenv('ORACLE_PASSWORD')
        
        # Extraction settings (proven optimal from notebook)
        self.extraction_method = 'sequential'  # Proven best performance
        self.connection_timeout = 30
        self.query_timeout = 300  # 5 minutes for large tables
        
        # Progress tracking
        self.extracted_tables = []
        self.failed_tables = []
        self.start_time = None
        self.total_rows_extracted = 0
        
        # Setup output directories
        self.setup_directories()
        
        # Load table catalog if available
        self.table_catalog_path = os.getenv('TABLE_CATALOG_PATH', 'config/table_catalog.json')
        self._table_catalog = self._load_table_catalog(self.table_catalog_path)
        if self._table_catalog:
            logger.info(f"📖 Loaded table catalog from {self.table_catalog_path}")
        else:
            logger.warning("📖 Table catalog not found or invalid; using built-in defaults")
        
        logger.info("✅ FullDataExtractor initialized")
        logger.info(f"🔗 Target: {self.host}:{self.port}/{self.service}")
        logger.info(f"⚡ Method: {self.extraction_method} (proven optimal)")
    
    def setup_directories(self):
        """Create output directory structure"""
        base_dir = Path('data')
        
        self.output_dirs = {
            'raw_csv': base_dir / 'raw' / 'oracle',
            'processed_parquet': base_dir / 'processed' / 'real',
            'unified': base_dir / 'processed' / 'unified_real',
            'metadata': base_dir / 'analysis',
            'logs': Path('logs')
        }
        
        for dir_path in self.output_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 Output directories ready: {list(self.output_dirs.keys())}")
    
    def get_connection(self) -> cx_Oracle.Connection:
        """Get optimized Oracle connection"""
        try:
            dsn = cx_Oracle.makedsn(self.host, self.port, service_name=self.service)
            connection = cx_Oracle.connect(
                self.user,
                self.password,
                dsn,
                encoding='UTF-8'
            )
            
            # Apply Oracle optimizations based on notebook research
            cursor = connection.cursor()
            cursor.execute("ALTER SESSION SET QUERY_REWRITE_ENABLED = FALSE")
            cursor.execute("ALTER SESSION SET OPTIMIZER_MODE = FIRST_ROWS")
            cursor.close()
            
            return connection
        
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Oracle connection and validate access"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Test query on known table
            cursor.execute("SELECT COUNT(*) FROM RWTXN_46.AMX_DONATION_LINES")
            count = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            logger.info(f"✅ Connection successful!")
            logger.info(f"📊 Test query result: AMX_DONATION_LINES has {count:,} rows")
            return True
        
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def get_high_priority_tables(self) -> List[Dict]:
        """Get high priority table definitions from config if available, else defaults"""
        config_tables = self._load_catalog_tier('high_priority')
        if config_tables is not None:
            return config_tables
        return [
            {'name': 'AMX_DONATION_LINES', 'full_name': 'RWTXN_46.AMX_DONATION_LINES', 'business_priority': 'critical', 'description': 'Core donation line items data'},
            {'name': 'AMX_DONATION_HEADER', 'full_name': 'RWTXN_46.AMX_DONATION_HEADER', 'business_priority': 'critical', 'description': 'Donation header/summary data'},
            {'name': 'ACBIDS', 'full_name': 'RWTXN_46.ACBIDS', 'business_priority': 'critical', 'description': 'Bidding sessions and auction data - KEY for donation flow'},
            {'name': 'ACWINNER', 'full_name': 'RWTXN_46.ACWINNER', 'business_priority': 'critical', 'description': 'Winner determination - ESSENTIAL for final destination tracking'},
            {'name': 'ACSHARES', 'full_name': 'RWTXN_46.ACSHARES', 'business_priority': 'critical', 'description': 'Bid share allocations and distribution tracking'},
            {'name': 'RW_ORDER_ITEM', 'full_name': 'RWTXN_46.RW_ORDER_ITEM', 'business_priority': 'high', 'description': 'Order line items and procurement data'},
            {'name': 'RW_ORDER_SUPPLIER', 'full_name': 'RWTXN_46.RW_ORDER_SUPPLIER', 'business_priority': 'high', 'description': 'Order-supplier relationship data'},
            {'name': 'RW_PURCHASE_ORDER', 'full_name': 'RWTXN_46.RW_PURCHASE_ORDER', 'business_priority': 'high', 'description': 'Purchase order header data'}
        ]
    
    def get_medium_priority_tables(self) -> List[Dict]:
        """Get medium priority table definitions from config if available, else defaults"""
        config_tables = self._load_catalog_tier('medium_priority')
        if config_tables is not None:
            return config_tables
        return [
            {'name': 'AMX_OFFER_HEADER', 'full_name': 'RWTXN_46.AMX_OFFER_HEADER', 'business_priority': 'medium', 'description': 'Food offer headers'},
            {'name': 'AMX_OFFER_LINES', 'full_name': 'RWTXN_46.AMX_OFFER_LINES', 'business_priority': 'medium', 'description': 'Food offer line items'},
            {'name': 'RW_ORG', 'full_name': 'RWTXN_46.RW_ORG', 'business_priority': 'medium', 'description': 'Organization master data - ESSENTIAL for final destination tracking'},
            {'name': 'ACACTION', 'full_name': 'RWTXN_46.ACACTION', 'business_priority': 'medium', 'description': 'Bidding actions and events log'},
            {'name': 'ACBIDS_ARCHIVE', 'full_name': 'RWTXN_46.ACBIDS_ARCHIVE', 'business_priority': 'medium', 'description': 'Archived bidding sessions for historical analysis'},
            {'name': 'ACSHARES_ARCHIVE', 'full_name': 'RWTXN_46.ACSHARES_ARCHIVE', 'business_priority': 'medium', 'description': 'Archived bid share allocations'},
            {'name': 'RW_USER', 'full_name': 'RWTXN_46.RW_USER', 'business_priority': 'medium', 'description': 'User management data'}
        ]
    
    def extract_table_full(self, table_info: Dict, save_formats: List[str] = ['csv', 'parquet']) -> Dict:
        """Extract complete table using proven sequential method"""
        
        table_name = table_info['name']
        full_name = table_info['full_name']
        expected_rows = table_info['rows']
        
        logger.info(f"\n🔄 Extracting {table_name}...")
        logger.info(f"   📋 Full name: {full_name}")
        logger.info(f"   📊 Expected rows: {expected_rows:,}")
        
        start_time = time.time()
        
        try:
            # Get connection
            connection = self.get_connection()
            
            # Optimal query based on notebook research (1,100+ rows/sec performance)
            query = f"SELECT * FROM {full_name} ORDER BY ROWID"
            
            # Extract with pandas (most efficient for our environment)
            df = pd.read_sql_query(query, connection)
            connection.close()
            
            duration = time.time() - start_time
            actual_rows = len(df)
            throughput = actual_rows / duration if duration > 0 else 0
            
            # Save in requested formats
            saved_files = []
            
            if 'csv' in save_formats:
                csv_path = self.output_dirs['raw_csv'] / f"{table_name}.csv"
                df.to_csv(csv_path, index=False)
                saved_files.append(str(csv_path))
            
            if 'parquet' in save_formats:
                parquet_path = self.output_dirs['processed_parquet'] / f"{table_name}.parquet"
                df.to_parquet(parquet_path, index=False)
                saved_files.append(str(parquet_path))
            
            # Calculate metrics
            memory_mb = df.memory_usage(deep=True).sum() / 1024**2
            total_size_mb = sum(Path(f).stat().st_size for f in saved_files if Path(f).exists()) / 1024**2
            
            # Create result record
            result = {
                'table_name': table_name,
                'full_name': full_name,
                'rows_extracted': actual_rows,
                'expected_rows': expected_rows,
                'columns': len(df.columns),
                'duration_seconds': round(duration, 2),
                'throughput_rows_per_sec': round(throughput, 1),
                'memory_usage_mb': round(memory_mb, 2),
                'file_size_mb': round(total_size_mb, 2),
                'saved_files': saved_files,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
            # Display results
            logger.info(f"   ✅ Completed: {actual_rows:,} rows in {duration:.2f}s")
            logger.info(f"   🚀 Throughput: {throughput:.1f} rows/sec")
            logger.info(f"   💾 Memory: {memory_mb:.2f}MB, Files: {total_size_mb:.2f}MB")
            logger.info(f"   📁 Saved to: {len(saved_files)} formats")
            
            # Row count validation
            if actual_rows != expected_rows:
                logger.warning(f"   ⚠️  Row count mismatch: expected {expected_rows:,}, got {actual_rows:,}")
            
            self.extracted_tables.append(result)
            self.total_rows_extracted += actual_rows
            
            # Memory cleanup for large tables
            del df
            gc.collect()
            
            return result
        
        except Exception as e:
            duration = time.time() - start_time
            error_result = {
                'table_name': table_name,
                'full_name': full_name,
                'error': str(e),
                'duration_seconds': round(duration, 2),
                'status': 'failed',
                'timestamp': datetime.now().isoformat()
            }
            
            logger.error(f"   ❌ Failed: {e}")
            self.failed_tables.append(error_result)
            
            return error_result
    
    def extract_tier(self, tier: str = 'high_priority') -> Dict:
        """Extract tables by priority tier"""
        
        if tier == 'high_priority':
            tables = self.get_high_priority_tables()
        elif tier == 'medium_priority':
            tables = self.get_medium_priority_tables()
        elif tier == 'all_priority':
            tables = self.get_high_priority_tables() + self.get_medium_priority_tables()
        else:
            raise ValueError(f"Invalid tier: {tier}. Use 'high_priority', 'medium_priority', or 'all_priority'")
        
        logger.info(f"🔴 ===== {tier.upper()} TABLE EXTRACTION =====")
        logger.info(f"📊 Extracting {len(tables)} tables")
        
        total_estimated_time = sum(t.get('estimated_minutes', 0) for t in tables)
        logger.info(f"⏱️  Estimated total time: ~{total_estimated_time:.1f} minutes")
        
        self.start_time = time.time()
        extraction_results = []
        
        # Extract each table sequentially (proven optimal method)
        for i, table_info in enumerate(tables, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 [{i}/{len(tables)}] {table_info['name']}")
            logger.info(f"🎯 Priority: {table_info.get('business_priority', 'unknown').upper()}")
            logger.info(f"📝 Description: {table_info.get('description', 'No description')}")
            
            result = self.extract_table_full(table_info)
            extraction_results.append(result)
            
            # Progress update
            elapsed = time.time() - self.start_time
            remaining_tables = len(tables) - i
            avg_time_per_table = elapsed / i
            eta_minutes = (remaining_tables * avg_time_per_table) / 60
            
            logger.info(f"\n📈 Progress: {i}/{len(tables)} tables completed")
            logger.info(f"⏱️  Elapsed: {elapsed/60:.1f}min, ETA: {eta_minutes:.1f}min")
            logger.info(f"📊 Total rows extracted: {self.total_rows_extracted:,}")
        
        # Final summary
        total_duration = time.time() - self.start_time
        successful_extractions = [r for r in extraction_results if r['status'] == 'success']
        failed_extractions = [r for r in extraction_results if r['status'] == 'failed']
        
        logger.info(f"\n" + "="*80)
        logger.info(f"🏁 {tier.upper()} EXTRACTION COMPLETED")
        logger.info(f"="*80)
        logger.info(f"⏱️  Total Duration: {total_duration/60:.2f} minutes ({total_duration:.1f} seconds)")
        logger.info(f"✅ Successful Tables: {len(successful_extractions)}/{len(tables)}")
        logger.info(f"❌ Failed Tables: {len(failed_extractions)}")
        logger.info(f"📊 Total Rows Extracted: {self.total_rows_extracted:,}")
        
        if successful_extractions:
            avg_throughput = np.mean([r['throughput_rows_per_sec'] for r in successful_extractions])
            total_file_size = sum(r['file_size_mb'] for r in successful_extractions)
            overall_throughput = self.total_rows_extracted / total_duration
            
            logger.info(f"🚀 Overall Throughput: {overall_throughput:.1f} rows/sec")
            logger.info(f"📈 Average Table Throughput: {avg_throughput:.1f} rows/sec")
            logger.info(f"💾 Total Files Size: {total_file_size:.2f} MB")
        
        # Save extraction metadata
        metadata = {
            'extraction_type': tier,
            'extraction_method': 'sequential_optimal',
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_seconds': total_duration,
            'duration_minutes': total_duration / 60,
            'total_rows': self.total_rows_extracted,
            'successful_tables': len(successful_extractions),
            'failed_tables': len(failed_extractions),
            'overall_throughput': self.total_rows_extracted / total_duration if total_duration > 0 else 0,
            'extraction_results': extraction_results
        }
        
        metadata_file = self.output_dirs['metadata'] / f'{tier}_extraction_metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"\n💾 Metadata saved to: {metadata_file}")
        
        return metadata

    def _load_table_catalog(self, path: str) -> Optional[Dict]:
        try:
            p = Path(path)
            if not p.exists():
                return None
            with open(p, 'r') as f:
                data = json.load(f)
            # Basic validation
            if not isinstance(data, dict) or 'tiers' not in data:
                return None
            return data
        except Exception as e:
            logger.warning(f"Failed to load table catalog from {path}: {e}")
            return None

    def _load_catalog_tier(self, tier: str) -> Optional[List[Dict]]:
        if not self._table_catalog:
            return None
        tiers = self._table_catalog.get('tiers', {})
        tables = tiers.get(tier)
        if not tables:
            return None
        # Normalize keys if needed
        norm = []
        for t in tables:
            norm.append({
                'name': t.get('name'),
                'full_name': t.get('full_name') or t.get('qualified_name') or t.get('table'),
                'business_priority': t.get('business_priority'),
                'description': t.get('description', '')
            })
        return norm

def main():
    """Main extraction entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HungerHub Full Data Extractor')
    parser.add_argument('--tier', 
                       choices=['high_priority', 'medium_priority', 'all_priority'],
                       default='high_priority',
                       help='Table priority tier to extract')
    parser.add_argument('--test-connection', action='store_true',
                       help='Test Oracle connection only')
    
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = FullDataExtractor()
    
    # Test connection if requested
    if args.test_connection:
        if extractor.test_connection():
            logger.info("🚀 Connection test successful - ready for extraction!")
            return 0
        else:
            logger.error("🛑 Connection test failed")
            return 1
    
    # Run extraction
    try:
        logger.info(f"🚀 Starting {args.tier} extraction...")
        results = extractor.extract_tier(args.tier)
        
        if results['failed_tables'] == 0:
            logger.info("🎉 SUCCESS: All tables extracted successfully!")
            logger.info(f"📊 Ready for ETL processing with {results['total_rows']:,} records")
            return 0
        else:
            logger.warning(f"⚠️ PARTIAL SUCCESS: {results['failed_tables']} tables failed")
            return 1
            
    except Exception as e:
        logger.error(f"💥 Extraction failed: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
