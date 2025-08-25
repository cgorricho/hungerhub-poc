#!/usr/bin/env python3
"""
Bidding Flow Transformer - Real Oracle Data Processing
Creates unified donation tracking datasets from extracted Oracle tables

Processes:
- Donation headers and lines (AMX_DONATION_HEADER, AMX_DONATION_LINES)
- Bidding data (ACBIDS, ACWINNER, ACSHARES)
- Organization data (RW_ORG) 
- Supporting tables for complete flow tracking

Author: HungerHub POC Team
Date: August 2025
Version: 1.0 - Real Data Processing
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BiddingFlowTransformer:
    """
    Transforms extracted Oracle data into unified donation flow tracking datasets
    """
    
    def __init__(self, data_dir: str = 'data/processed/real'):
        """Initialize transformer with extracted data directory"""
        self.data_dir = Path(data_dir)
        self.output_dir = Path('data/processed/unified_real')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track loaded tables
        self.loaded_tables = {}
        self.processing_stats = {}
        
        logger.info("🔄 BiddingFlowTransformer initialized")
        logger.info(f"📁 Input dir: {self.data_dir}")
        logger.info(f"📁 Output dir: {self.output_dir}")
    
    def list_available_tables(self) -> List[str]:
        """List all available extracted table files"""
        parquet_files = list(self.data_dir.glob("*.parquet"))
        table_names = [f.stem for f in parquet_files]
        
        logger.info(f"📊 Found {len(table_names)} extracted tables:")
        for name in sorted(table_names):
            logger.info(f"   - {name}")
        
        return table_names
    
    def load_table(self, table_name: str, required: bool = True) -> Optional[pd.DataFrame]:
        """Load a table from parquet file"""
        table_path = self.data_dir / f"{table_name}.parquet"
        
        if not table_path.exists():
            if required:
                logger.error(f"❌ Required table not found: {table_name}")
                raise FileNotFoundError(f"Required table file not found: {table_path}")
            else:
                logger.warning(f"⚠️ Optional table not found: {table_name}")
                return None
        
        try:
            df = pd.read_parquet(table_path)
            self.loaded_tables[table_name] = df
            
            logger.info(f"✅ Loaded {table_name}: {len(df):,} rows, {len(df.columns)} columns")
            
            # Store basic stats
            self.processing_stats[table_name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_mb': df.memory_usage(deep=True).sum() / 1024**2,
                'loaded_at': datetime.now().isoformat()
            }
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to load {table_name}: {e}")
            if required:
                raise
            return None
    
    def load_core_tables(self) -> Dict[str, pd.DataFrame]:
        """Load all core tables required for bidding flow transformation"""
        
        logger.info("🔄 Loading core tables for bidding flow analysis...")
        
        # Required tables for complete donation flow
        core_tables = {}
        
        # Critical donation tables
        core_tables['donation_header'] = self.load_table('AMX_DONATION_HEADER', required=True)
        core_tables['donation_lines'] = self.load_table('AMX_DONATION_LINES', required=True)
        
        # Critical bidding tables
        core_tables['bids'] = self.load_table('ACBIDS', required=True)
        core_tables['winners'] = self.load_table('ACWINNER', required=True) 
        core_tables['shares'] = self.load_table('ACSHARES', required=True)
        
        # Organization data for final destination tracking
        core_tables['organizations'] = self.load_table('RW_ORG', required=True)
        
        # Optional supporting tables
        core_tables['bid_actions'] = self.load_table('ACACTION', required=False)
        core_tables['bids_archive'] = self.load_table('ACBIDS_ARCHIVE', required=False)
        core_tables['shares_archive'] = self.load_table('ACSHARES_ARCHIVE', required=False)
        
        # Optional order tracking tables
        core_tables['order_items'] = self.load_table('RW_ORDER_ITEM', required=False)
        core_tables['order_supplier'] = self.load_table('RW_ORDER_SUPPLIER', required=False)
        core_tables['purchase_orders'] = self.load_table('RW_PURCHASE_ORDER', required=False)
        
        # Remove None values (optional tables that weren't found)
        core_tables = {k: v for k, v in core_tables.items() if v is not None}
        
        logger.info(f"✅ Loaded {len(core_tables)} core tables successfully")
        
        return core_tables
    
    def analyze_table_relationships(self, tables: Dict[str, pd.DataFrame]) -> Dict:
        """Analyze relationships between loaded tables"""
        
        logger.info("🔍 Analyzing table relationships...")
        
        relationships = {}
        
        # Common join keys to look for
        common_keys = [
            'DONATIONNUMBER', 'DONATIONLINENUMBER',
            'BIDID', 'WINNERID', 'SHAREID',
            'ORGANIZATIONID', 'ORGID', 'ORG_ID',
            'ORDERID', 'ORDER_ID', 'SUPPLIERID',
            'USERID', 'USER_ID'
        ]
        
        for table_name, df in tables.items():
            table_info = {
                'columns': list(df.columns),
                'matching_keys': [],
                'sample_data': {}
            }
            
            # Find matching keys
            for key in common_keys:
                if key in df.columns:
                    table_info['matching_keys'].append(key)
                    # Get sample non-null values
                    sample_vals = df[key].dropna().head(3).tolist()
                    table_info['sample_data'][key] = sample_vals
            
            relationships[table_name] = table_info
            
            logger.info(f"📋 {table_name}:")
            logger.info(f"   - Columns: {len(df.columns)}")
            logger.info(f"   - Join keys: {table_info['matching_keys']}")
        
        return relationships
    
    def create_donation_flow_dataset(self, tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Create unified donation flow tracking dataset"""
        
        logger.info("🔄 Creating unified donation flow dataset...")
        
        # Start with donation headers as the base
        donation_base = tables['donation_header'].copy()
        logger.info(f"📊 Base donation headers: {len(donation_base):,} records")
        
        # Add donation line items
        if 'donation_lines' in tables:
            # Merge with line items
            lines_summary = tables['donation_lines'].groupby('DONATIONNUMBER').agg({
                'DONATIONLINENUMBER': 'count',  # Count of line items
                'QUANTITY': ['sum', 'mean'],    # Quantity totals and averages
                'UNITPRICE': ['mean', 'max', 'min'],  # Price statistics
                'TOTALVALUE': ['sum', 'mean']   # Value totals and averages
            }).round(2)
            
            # Flatten column names
            lines_summary.columns = [
                'line_item_count', 
                'total_quantity', 'avg_quantity',
                'avg_unit_price', 'max_unit_price', 'min_unit_price',
                'total_line_value', 'avg_line_value'
            ]
            
            donation_flow = donation_base.merge(
                lines_summary, 
                left_on='DONATIONNUMBER', 
                right_index=True, 
                how='left'
            )
            logger.info(f"✅ Added line item summaries: {len(donation_flow):,} records")
        else:
            donation_flow = donation_base
        
        # Add bidding information
        if 'bids' in tables:
            # Create bid summary per donation
            bid_summary = tables['bids'].groupby('DONATIONNUMBER').agg({
                'BIDID': 'count',               # Number of bids
                'BIDAMOUNT': ['sum', 'mean', 'max'],  # Bid amounts
                'BIDSTATUS': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None,  # Most common status
                'BIDDATE': ['min', 'max']       # Bid date range
            }).round(2)
            
            # Flatten column names
            bid_summary.columns = [
                'total_bids', 
                'total_bid_amount', 'avg_bid_amount', 'max_bid_amount',
                'most_common_bid_status',
                'first_bid_date', 'last_bid_date'
            ]
            
            donation_flow = donation_flow.merge(
                bid_summary,
                left_on='DONATIONNUMBER',
                right_index=True,
                how='left'
            )
            logger.info(f"✅ Added bidding summaries: {len(donation_flow):,} records")
        
        # Add winner information
        if 'winners' in tables:
            # Create winner summary per donation
            winner_summary = tables['winners'].groupby('DONATIONNUMBER').agg({
                'WINNERID': 'count',            # Number of winners
                'ORGANIZATIONID': 'first',      # Winning organization
                'WINNINGAMOUNT': 'sum',         # Total winning amount
                'WINNERSTATUS': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None,
                'WINDATE': 'max'                # Latest win date
            }).round(2)
            
            # Flatten column names
            winner_summary.columns = [
                'winner_count',
                'winning_organization_id', 
                'total_winning_amount',
                'winner_status',
                'win_date'
            ]
            
            donation_flow = donation_flow.merge(
                winner_summary,
                left_on='DONATIONNUMBER',
                right_index=True,
                how='left'
            )
            logger.info(f"✅ Added winner information: {len(donation_flow):,} records")
        
        # Add share allocation information
        if 'shares' in tables:
            # Create share summary per donation
            share_summary = tables['shares'].groupby('DONATIONNUMBER').agg({
                'SHAREID': 'count',             # Number of shares
                'SHAREPERCENTAGE': ['sum', 'mean'],  # Share percentages
                'SHAREAMOUNT': ['sum', 'mean'], # Share amounts
                'ORGANIZATIONID': 'nunique'     # Number of orgs with shares
            }).round(2)
            
            # Flatten column names  
            share_summary.columns = [
                'share_count',
                'total_share_percentage', 'avg_share_percentage',
                'total_share_amount', 'avg_share_amount',
                'organizations_with_shares'
            ]
            
            donation_flow = donation_flow.merge(
                share_summary,
                left_on='DONATIONNUMBER',
                right_index=True,
                how='left'
            )
            logger.info(f"✅ Added share allocation data: {len(donation_flow):,} records")
        
        # Add organization details for final destinations
        if 'organizations' in tables and 'winning_organization_id' in donation_flow.columns:
            org_details = tables['organizations'][['ORGANIZATIONID', 'ORGANIZATIONNAME', 'ORGANIZATIONTYPE', 'CITY', 'STATE']].copy()
            org_details.columns = ['winning_organization_id', 'winning_org_name', 'winning_org_type', 'winning_org_city', 'winning_org_state']
            
            donation_flow = donation_flow.merge(
                org_details,
                on='winning_organization_id',
                how='left'
            )
            logger.info(f"✅ Added organization details: {len(donation_flow):,} records")
        
        # Add computed flow tracking fields
        donation_flow['flow_stage'] = donation_flow.apply(self._determine_flow_stage, axis=1)
        donation_flow['completion_percentage'] = donation_flow.apply(self._calculate_completion_percentage, axis=1)
        donation_flow['processing_date'] = datetime.now()
        
        logger.info(f"🎉 Unified donation flow dataset created: {len(donation_flow):,} records")
        logger.info(f"📊 Columns: {len(donation_flow.columns)}")
        
        return donation_flow
    
    def _determine_flow_stage(self, row) -> str:
        """Determine the current stage of the donation flow"""
        
        # Check completion stages in order
        if pd.notna(row.get('total_share_amount', pd.NA)) and row.get('total_share_amount', 0) > 0:
            return 'Allocated'
        elif pd.notna(row.get('total_winning_amount', pd.NA)) and row.get('total_winning_amount', 0) > 0:
            return 'Won'
        elif pd.notna(row.get('total_bids', pd.NA)) and row.get('total_bids', 0) > 0:
            return 'Bidding'
        elif pd.notna(row.get('line_item_count', pd.NA)) and row.get('line_item_count', 0) > 0:
            return 'Listed'
        else:
            return 'Draft'
    
    def _calculate_completion_percentage(self, row) -> float:
        """Calculate completion percentage based on flow stage"""
        
        stage = self._determine_flow_stage(row)
        
        stage_percentages = {
            'Draft': 10,
            'Listed': 30, 
            'Bidding': 60,
            'Won': 85,
            'Allocated': 100
        }
        
        return stage_percentages.get(stage, 0)
    
    def create_analysis_views(self, donation_flow: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create specialized analysis views from unified dataset"""
        
        logger.info("🔄 Creating analysis views...")
        
        views = {}
        
        # Flow stage summary
        stage_summary = donation_flow.groupby('flow_stage').agg({
            'DONATIONNUMBER': 'count',
            'total_quantity': ['sum', 'mean'],
            'total_line_value': ['sum', 'mean'],
            'total_winning_amount': ['sum', 'mean'],
            'completion_percentage': 'mean'
        }).round(2)
        
        stage_summary.columns = [
            'donation_count', 
            'total_qty', 'avg_qty',
            'total_value', 'avg_value',
            'total_winning', 'avg_winning',
            'avg_completion_pct'
        ]
        
        views['flow_stage_summary'] = stage_summary
        logger.info(f"✅ Flow stage summary: {len(stage_summary)} stages")
        
        # Organization performance (if org data available)
        if 'winning_org_name' in donation_flow.columns:
            org_performance = donation_flow[
                donation_flow['winning_org_name'].notna()
            ].groupby(['winning_org_name', 'winning_org_type']).agg({
                'DONATIONNUMBER': 'count',
                'total_winning_amount': ['sum', 'mean'],
                'total_share_amount': ['sum', 'mean'],
                'completion_percentage': 'mean'
            }).round(2)
            
            org_performance.columns = [
                'donations_won',
                'total_won_amount', 'avg_won_amount',
                'total_allocated', 'avg_allocated', 
                'avg_completion_pct'
            ]
            
            views['organization_performance'] = org_performance
            logger.info(f"✅ Organization performance: {len(org_performance)} organizations")
        
        # Bidding competition analysis
        if 'total_bids' in donation_flow.columns:
            bidding_analysis = donation_flow[
                donation_flow['total_bids'].notna() & (donation_flow['total_bids'] > 0)
            ].copy()
            
            # Categorize competition level
            bidding_analysis['competition_level'] = pd.cut(
                bidding_analysis['total_bids'],
                bins=[0, 1, 3, 5, float('inf')],
                labels=['Low', 'Medium', 'High', 'Very High']
            )
            
            competition_summary = bidding_analysis.groupby('competition_level').agg({
                'DONATIONNUMBER': 'count',
                'total_bid_amount': ['sum', 'mean'],
                'total_winning_amount': ['sum', 'mean'],
                'avg_bid_amount': 'mean'
            }).round(2)
            
            competition_summary.columns = [
                'donation_count',
                'total_bid_value', 'avg_bid_value',
                'total_won_value', 'avg_won_value',
                'avg_individual_bid'
            ]
            
            views['bidding_competition'] = competition_summary
            logger.info(f"✅ Bidding competition analysis: {len(competition_summary)} competition levels")
        
        # Time-based flow analysis (if date fields available)
        date_cols = [col for col in donation_flow.columns if 'DATE' in col.upper() or 'date' in col]
        if date_cols:
            logger.info(f"📅 Found date columns for time analysis: {date_cols}")
            # Could add time-based analysis here
        
        logger.info(f"🎉 Created {len(views)} analysis views")
        
        return views
    
    def save_datasets(self, donation_flow: pd.DataFrame, analysis_views: Dict[str, pd.DataFrame]):
        """Save all datasets to files"""
        
        logger.info("💾 Saving datasets...")
        
        # Save main unified dataset
        main_file = self.output_dir / 'unified_donation_flow.parquet'
        donation_flow.to_parquet(main_file, index=False)
        logger.info(f"✅ Saved unified dataset: {main_file} ({len(donation_flow):,} records)")
        
        # Save analysis views
        for view_name, view_df in analysis_views.items():
            view_file = self.output_dir / f'view_{view_name}.parquet'
            view_df.to_parquet(view_file)
            logger.info(f"✅ Saved {view_name}: {view_file} ({len(view_df):,} records)")
        
        # Save processing metadata
        metadata = {
            'processing_date': datetime.now().isoformat(),
            'input_tables': list(self.loaded_tables.keys()),
            'table_stats': self.processing_stats,
            'output_files': {
                'unified_dataset': str(main_file),
                'analysis_views': {name: str(self.output_dir / f'view_{name}.parquet') 
                                 for name in analysis_views.keys()}
            },
            'unified_dataset_stats': {
                'rows': len(donation_flow),
                'columns': len(donation_flow.columns),
                'memory_mb': donation_flow.memory_usage(deep=True).sum() / 1024**2
            }
        }
        
        metadata_file = self.output_dir / 'transformation_metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"✅ Saved metadata: {metadata_file}")
        
        return metadata
    
    def run_full_transformation(self) -> Dict:
        """Run complete bidding flow transformation pipeline"""
        
        logger.info("🚀 Starting full bidding flow transformation...")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # Step 1: List and load tables
            available_tables = self.list_available_tables()
            core_tables = self.load_core_tables()
            
            # Step 2: Analyze relationships
            relationships = self.analyze_table_relationships(core_tables)
            
            # Step 3: Create unified dataset
            donation_flow = self.create_donation_flow_dataset(core_tables)
            
            # Step 4: Create analysis views
            analysis_views = self.create_analysis_views(donation_flow)
            
            # Step 5: Save everything
            metadata = self.save_datasets(donation_flow, analysis_views)
            
            # Final summary
            duration = datetime.now() - start_time
            
            logger.info("=" * 80)
            logger.info("🎉 TRANSFORMATION COMPLETED SUCCESSFULLY!")
            logger.info("=" * 80)
            logger.info(f"⏱️  Duration: {duration}")
            logger.info(f"📊 Input tables processed: {len(core_tables)}")
            logger.info(f"📊 Unified dataset: {len(donation_flow):,} donation records")
            logger.info(f"📊 Analysis views: {len(analysis_views)}")
            logger.info(f"📁 Output directory: {self.output_dir}")
            
            # Add summary to metadata
            metadata['transformation_summary'] = {
                'status': 'success',
                'duration_seconds': duration.total_seconds(),
                'input_tables_count': len(core_tables),
                'unified_records': len(donation_flow),
                'analysis_views_count': len(analysis_views)
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"💥 Transformation failed: {e}")
            logger.error(f"⏱️  Failed after: {datetime.now() - start_time}")
            
            error_metadata = {
                'transformation_summary': {
                    'status': 'failed',
                    'error': str(e),
                    'duration_seconds': (datetime.now() - start_time).total_seconds()
                }
            }
            
            return error_metadata

def main():
    """Main transformation entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HungerHub Bidding Flow Transformer')
    parser.add_argument('--data-dir', 
                       default='data/processed/real',
                       help='Directory containing extracted Oracle data')
    parser.add_argument('--list-tables', action='store_true',
                       help='List available tables only')
    
    args = parser.parse_args()
    
    # Initialize transformer
    transformer = BiddingFlowTransformer(data_dir=args.data_dir)
    
    # List tables if requested
    if args.list_tables:
        transformer.list_available_tables()
        return 0
    
    # Run full transformation
    try:
        results = transformer.run_full_transformation()
        
        if results.get('transformation_summary', {}).get('status') == 'success':
            logger.info("🚀 Ready for visualization and analysis!")
            return 0
        else:
            logger.error("🛑 Transformation failed")
            return 1
            
    except Exception as e:
        logger.error(f"💥 Pipeline failed: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
