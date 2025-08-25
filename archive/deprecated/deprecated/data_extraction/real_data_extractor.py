#!/usr/bin/env python3
"""
Real Data Extraction for HungerHub POC
Day 3-4 Task: Extract sample data from priority Oracle tables
"""

import os
import sys
import cx_Oracle
import pandas as pd
import json
from datetime import datetime
from dotenv import load_dotenv

class HungerHubDataExtractor:
    """Extract real data from Oracle tables for POC"""
    
    def __init__(self):
        load_dotenv('config/.env')
        
        self.databases = {
            'choice': {
                'host': os.getenv('CHOICE_ORACLE_HOST'),
                'port': os.getenv('CHOICE_ORACLE_PORT', '1521'),
                'service': os.getenv('CHOICE_ORACLE_SERVICE_NAME'),
                'user': os.getenv('CHOICE_USERNAME'),
                'password': os.getenv('CHOICE_PASSWORD'),
                'name': 'Choice Sandbox'
            },
            'agency': {
                'host': os.getenv('AGENCY_ORACLE_HOST'),
                'port': os.getenv('AGENCY_ORACLE_PORT', '1521'),
                'service': os.getenv('AGENCY_ORACLE_SERVICE_NAME'),
                'user': os.getenv('AGENCY_USERNAME'),
                'password': os.getenv('AGENCY_PASSWORD'),
                'name': 'Agency Sandbox'
            }
        }
        
        # Priority tables based on discovery results and POC plan
        self.priority_extracts = {
            'donations': {
                'choice.AMX_DONATION_HEADER': {
                    'table': 'AMX_DONATION_HEADER',
                    'purpose': 'Donation header records',
                    'sample_size': 1000
                },
                'choice.AMX_DONATION_LINES': {
                    'table': 'AMX_DONATION_LINES',
                    'purpose': 'Donation line items',
                    'sample_size': 5000
                }
            },
            'orders': {
                'choice.DOCUMENTHEADER': {
                    'table': 'DOCUMENTHEADER',
                    'purpose': 'Choice document headers',
                    'sample_size': 1000
                },
                'choice.DOCUMENTLINES': {
                    'table': 'DOCUMENTLINES',
                    'purpose': 'Choice document line items',
                    'sample_size': 5000
                },
                'agency.DOCUMENTHEADER': {
                    'table': 'DOCUMENTHEADER',
                    'purpose': 'Agency document headers',
                    'sample_size': 2000
                },
                'agency.DOCUMENTLINES': {
                    'table': 'DOCUMENTLINES',
                    'purpose': 'Agency document line items',
                    'sample_size': 10000
                }
            },
            'organizations': {
                'choice.RW_ORG': {
                    'table': 'RW_ORG',
                    'purpose': 'Choice organizations',
                    'sample_size': 500
                },
                'agency.RW_ORG': {
                    'table': 'RW_ORG',
                    'purpose': 'Agency organizations',
                    'sample_size': 2000
                }
            }
        }
        
    def connect_to_database(self, db_key):
        """Connect to specified database"""
        config = self.databases[db_key]
        dsn = cx_Oracle.makedsn(config['host'], config['port'], service_name=config['service'])
        return cx_Oracle.connect(config['user'], config['password'], dsn)
    
    def extract_table_sample(self, db_key, table_name, sample_size=1000, where_clause=None):
        """Extract sample data from a table (backward compatibility)"""
        
        print(f"   📊 Extracting from {db_key.upper()}.{table_name} (max {sample_size} rows)...")
        
        try:
            connection = self.connect_to_database(db_key)
            
            # Build query with optional where clause and row limit
            base_query = f"SELECT * FROM {table_name}"
            if where_clause:
                base_query += f" WHERE {where_clause}"
            
            # Add row limit - Oracle uses ROWNUM
            query = f"SELECT * FROM ({base_query}) WHERE rownum <= {sample_size}"
            
            # Execute query and get results
            df = pd.read_sql_query(query, connection)
            
            connection.close()
            
            print(f"      ✅ Extracted {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            print(f"      ❌ Error extracting {db_key}.{table_name}: {e}")
            return None
    
    def extract_table_full(self, db_key, table_name, full_table_name=None):
        """Extract complete table using proven sequential method from notebook research
        
        Args:
            db_key: Database connection key ('choice' or 'agency')
            table_name: Simple table name for file naming
            full_table_name: Complete Oracle table name (e.g., 'RWTXN_46.AMX_DONATION_LINES')
        
        Returns:
            DataFrame with complete table data (no sampling limits)
        """
        
        # Use full table name if provided, otherwise construct it
        oracle_table = full_table_name if full_table_name else table_name
        
        print(f"   🚀 Full extraction from {db_key.upper()}.{oracle_table}...")
        
        try:
            connection = self.connect_to_database(db_key)
            
            # Optimal query based on notebook research - NO SAMPLING
            query = f"SELECT * FROM {oracle_table} ORDER BY ROWID"
            
            # Direct pandas extraction (proven method: 1,100+ rows/sec)
            start_time = datetime.now()
            df = pd.read_sql_query(query, connection)
            duration = (datetime.now() - start_time).total_seconds()
            
            connection.close()
            
            # Calculate performance metrics
            throughput = len(df) / duration if duration > 0 else 0
            
            print(f"      ✅ Extracted {len(df):,} rows, {len(df.columns)} columns")
            print(f"      🚀 Performance: {throughput:.1f} rows/sec in {duration:.2f}s")
            print(f"      📊 Using proven sequential method from optimization research")
            
            return df
            
        except Exception as e:
            print(f"      ❌ Error extracting {db_key}.{oracle_table}: {e}")
            return None
    
    def run_priority_extraction(self):
        """Extract all priority tables according to POC plan"""
        
        print("🍽️ HungerHub POC - Real Data Extraction")
        print("=" * 50)
        print("📋 Day 3-4 Task: Extract Priority Tables from Oracle")
        print("🎯 Focus: Donations, Orders, Organizations")
        print("=" * 50)
        
        extraction_results = {
            'timestamp': datetime.now().isoformat(),
            'total_records_extracted': 0,
            'successful_extracts': 0,
            'failed_extracts': 0,
            'categories': {}
        }
        
        os.makedirs('data/raw/oracle', exist_ok=True)
        os.makedirs('data/processed/real', exist_ok=True)
        
        for category, tables in self.priority_extracts.items():
            print(f"\n💼 EXTRACTING {category.upper()} DATA:")
            print("-" * 30)
            
            category_results = {
                'tables_extracted': 0,
                'total_rows': 0,
                'files_created': []
            }
            
            for table_key, config in tables.items():
                db_key, table_name = table_key.split('.')
                
                # Extract data
                df = self.extract_table_sample(
                    db_key, 
                    config['table'], 
                    config['sample_size']
                )
                
                if df is not None and len(df) > 0:
                    # Save raw data
                    raw_filename = f"data/raw/oracle/{db_key}_{table_name}_sample.csv"
                    df.to_csv(raw_filename, index=False)
                    
                    # Save as parquet for fast loading
                    parquet_filename = f"data/processed/real/{db_key}_{table_name}_sample.parquet"
                    df.to_parquet(parquet_filename, index=False)
                    
                    category_results['tables_extracted'] += 1
                    category_results['total_rows'] += len(df)
                    category_results['files_created'].extend([raw_filename, parquet_filename])
                    
                    extraction_results['total_records_extracted'] += len(df)
                    extraction_results['successful_extracts'] += 1
                    
                    print(f"      💾 Saved: {raw_filename}")
                    print(f"      💾 Saved: {parquet_filename}")
                    
                else:
                    extraction_results['failed_extracts'] += 1
                    print(f"      ❌ Failed to extract data")
            
            extraction_results['categories'][category] = category_results
            
            print(f"   📊 {category.capitalize()} Summary: {category_results['tables_extracted']} tables, {category_results['total_rows']} total rows")
        
        # Generate summary report
        print(f"\n" + "=" * 50)
        print("📋 EXTRACTION SUMMARY")
        print("=" * 50)
        
        print(f"✅ Successful extracts: {extraction_results['successful_extracts']}")
        print(f"❌ Failed extracts: {extraction_results['failed_extracts']}")
        print(f"📊 Total records: {extraction_results['total_records_extracted']:,}")
        
        for category, results in extraction_results['categories'].items():
            print(f"   {category.capitalize()}: {results['tables_extracted']} tables, {results['total_rows']:,} rows")
        
        # Save extraction metadata
        metadata_file = 'data/analysis/real_data_extraction_results.json'
        with open(metadata_file, 'w') as f:
            json.dump(extraction_results, f, indent=2, default=str)
        
        print(f"\n📄 Extraction metadata saved: {metadata_file}")
        
        return extraction_results
    
    def create_unified_datasets(self):
        """Create unified datasets for dashboard use"""
        
        print(f"\n🔄 Creating unified datasets for dashboard...")
        
        try:
            # Load extracted data
            donations_header = pd.read_parquet('data/processed/real/choice_AMX_DONATION_HEADER_sample.parquet')
            donations_lines = pd.read_parquet('data/processed/real/choice_AMX_DONATION_LINES_sample.parquet')
            
            choice_orgs = pd.read_parquet('data/processed/real/choice_RW_ORG_sample.parquet')
            agency_orgs = pd.read_parquet('data/processed/real/agency_RW_ORG_sample.parquet')
            
            # Create unified organizations dataset
            choice_orgs['data_source'] = 'Choice'
            agency_orgs['data_source'] = 'Agency'
            
            # Align column names (take intersection of common columns)
            common_org_cols = list(set(choice_orgs.columns) & set(agency_orgs.columns))
            
            unified_orgs = pd.concat([
                choice_orgs[common_org_cols],
                agency_orgs[common_org_cols]
            ], ignore_index=True)
            
            # Create unified donations dataset (merge header and lines)
            donations_merged = donations_header.merge(
                donations_lines,
                left_on='ID',  # Assuming ID is the key field
                right_on='DONATION_HEADER_ID',  # Assuming this links to header
                how='left',
                suffixes=('_header', '_line')
            )
            
            # Save unified datasets
            unified_orgs.to_csv('data/processed/real/unified_organizations.csv', index=False)
            unified_orgs.to_parquet('data/processed/real/unified_organizations.parquet', index=False)
            
            donations_merged.to_csv('data/processed/real/unified_donations.csv', index=False)
            donations_merged.to_parquet('data/processed/real/unified_donations.parquet', index=False)
            
            print(f"   ✅ Unified organizations: {len(unified_orgs)} records")
            print(f"   ✅ Unified donations: {len(donations_merged)} records")
            print(f"   💾 Saved unified datasets in data/processed/real/")
            
            return {
                'organizations_count': len(unified_orgs),
                'donations_count': len(donations_merged),
                'organizations_columns': list(unified_orgs.columns),
                'donations_columns': list(donations_merged.columns)
            }
            
        except Exception as e:
            print(f"   ❌ Error creating unified datasets: {e}")
            return None

def main():
    """Main extraction process"""
    
    extractor = HungerHubDataExtractor()
    
    # Run priority data extraction
    extraction_results = extractor.run_priority_extraction()
    
    # Create unified datasets if extraction was successful
    if extraction_results['successful_extracts'] > 0:
        unified_results = extractor.create_unified_datasets()
        
        if unified_results:
            print(f"\n🎉 SUCCESS: Real data extraction completed!")
            print(f"📊 Ready for dashboard integration with real Oracle data")
            return 0
        else:
            print(f"\n⚠️ PARTIAL SUCCESS: Data extracted but unification failed")
            return 1
    else:
        print(f"\n❌ FAILURE: No data could be extracted")
        return 2

if __name__ == "__main__":
    sys.exit(main())
