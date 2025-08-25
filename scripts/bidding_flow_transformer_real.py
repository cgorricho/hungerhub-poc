#!/usr/bin/env python3
"""
Bidding Flow Transformer - Real Oracle Data (Corrected)
Creates unified donation tracking datasets from extracted Oracle tables

Processes:
- Donation headers and lines (AMX_DONATION_HEADER, AMX_DONATION_LINES)
- Bidding data (ACBIDS_ARCHIVE with real bidding records)
- Share allocations (ACSHARES - organizational share data)
- Organization data (RW_ORG) 
- Supporting tables for complete flow tracking

Author: HungerHub POC Team
Date: August 2025
Version: 2.0 - Real Oracle Data with Correct Column Names
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
        
        logger.info("🔄 BiddingFlowTransformer (Real Oracle Data v2.0) initialized")
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
        
        logger.info("🔄 Loading core tables for real bidding flow analysis...")
        
        # Required tables for complete donation flow
        core_tables = {}
        
        # Critical donation tables
        core_tables['donation_header'] = self.load_table('AMX_DONATION_HEADER', required=True)
        core_tables['donation_lines'] = self.load_table('AMX_DONATION_LINES', required=True)
        
        # Real bidding tables (with actual data)
        core_tables['bids_archive'] = self.load_table('ACBIDS_ARCHIVE', required=True)  # Real bidding data
        core_tables['shares'] = self.load_table('ACSHARES', required=True)  # Share allocations
        core_tables['shares_archive'] = self.load_table('ACSHARES_ARCHIVE', required=False)  # Historical shares
        
        # Organization data for final destination tracking
        core_tables['organizations'] = self.load_table('RW_ORG', required=True)
        
        # Optional supporting tables
        core_tables['order_items'] = self.load_table('RW_ORDER_ITEM', required=False)
        core_tables['order_supplier'] = self.load_table('RW_ORDER_SUPPLIER', required=False)
        core_tables['purchase_orders'] = self.load_table('RW_PURCHASE_ORDER', required=False)
        
        # Optional offer tables
        core_tables['offer_header'] = self.load_table('AMX_OFFER_HEADER', required=False)
        core_tables['offer_lines'] = self.load_table('AMX_OFFER_LINES', required=False)
        
        # Remove None values (optional tables that weren't found)
        core_tables = {k: v for k, v in core_tables.items() if v is not None}
        
        logger.info(f"✅ Loaded {len(core_tables)} core tables successfully")
        
        return core_tables
    
    def analyze_table_relationships(self, tables: Dict[str, pd.DataFrame]) -> Dict:
        """Analyze relationships between loaded tables"""
        
        logger.info("🔍 Analyzing table relationships...")
        
        relationships = {}
        
        # Common join keys to look for (using actual column names from Oracle)
        common_keys = [
            'DONATIONNUMBER', 'DOCUMENTID',
            'ORG_ID', 'ORGNAME', 'AFFILIATEWEBID',
            'ITEMNUMBER', 'ITEMDESCRIPTION'
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
        
        logger.info("🔄 Creating unified donation flow dataset from real Oracle data...")
        
        # Start with donation headers as the base
        donation_base = tables['donation_header'].copy()
        logger.info(f"📊 Base donation headers: {len(donation_base):,} records")
        
        # Add donation line items using actual column names
        if 'donation_lines' in tables:
            logger.info("🔗 Adding donation line item summaries...")
            
            # Use actual column names from Oracle
            lines_summary = tables['donation_lines'].groupby('DONATIONNUMBER').agg({
                'ITEMNUMBER': ['count', 'nunique'],  # Count of line items and unique items
                'QUANTITY': ['sum', 'mean', 'max', 'min'],  # Quantity statistics  
                'TOTALPALLETS': ['sum', 'mean'],    # Pallet information
                'GROSSWEIGHT': ['mean'],           # Average gross weight per item
                'TOTALGROSSWEIGHT': ['sum', 'mean'], # Total/avg weight per donation
                'CUBE': ['sum', 'mean'],            # Volume/cube data
                'ITEMDESCRIPTION': lambda x: '; '.join(x.dropna().astype(str).head(3)),  # Sample descriptions
                'DONATIONREASON': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None,  # Most common reason
                'STATUS': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None,  # Most common status
                'STORAGEREQUIREMENT': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None,  # Storage type
                'EXPIRATIONDATE': ['count'],    # Count of items with expiration dates
                'MANUFACTUREDATE': ['count']    # Count of items with manufacture dates
            }).round(2)
            
            # Flatten column names
            lines_summary.columns = [
                'line_item_count', 'unique_items',
                'total_quantity', 'avg_quantity', 'max_quantity', 'min_quantity',
                'total_pallets', 'avg_pallets',
                'avg_item_gross_weight',
                'total_donation_weight', 'avg_donation_weight',
                'total_cube', 'avg_cube',
                'sample_descriptions',
                'primary_donation_reason',
                'primary_status',
                'primary_storage_requirement', 
                'items_with_expiration',
                'items_with_manufacture_date'
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
        
        # Add bidding information from archived bidding data
        if 'bids_archive' in tables:
            logger.info("🔗 Adding bidding information from archive...")
            
            # Create bid summary per document (DOCUMENTID maps to donations)
            bid_summary = tables['bids_archive'].groupby('DOCUMENTID').agg({
                'BIDAMOUNT': ['count', 'sum', 'mean', 'max', 'min'],  # Bid statistics
                'AFFILIATEWEBID': 'nunique',        # Number of unique bidders
                'WINNINGBID': ['sum', 'mean'],      # Winning bid amounts
                'WONLOAD': 'sum',                   # Total loads won
                'STATUS': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None,  # Most common status
                'BIDDATE': ['min', 'max', 'count'], # Bid date range and count
                'SHARES': ['sum', 'mean'],          # Share information
                'GROSSWEIGHT': ['sum', 'mean']      # Weight information
            }).round(2)
            
            # Flatten column names
            bid_summary.columns = [
                'total_bids', 'total_bid_amount', 'avg_bid_amount', 'max_bid_amount', 'min_bid_amount',
                'unique_bidders',
                'total_winning_amount', 'avg_winning_amount',
                'total_loads_won',
                'most_common_bid_status',
                'first_bid_date', 'last_bid_date', 'bid_events',
                'total_bid_shares', 'avg_bid_shares',
                'total_bid_weight', 'avg_bid_weight'
            ]
            
            # Try to join bidding data (DOCUMENTID might correspond to donation references)
            # First, let's see if there's any overlap
            bid_docs = set(tables['bids_archive']['DOCUMENTID'].dropna())
            donation_nums = set(donation_flow['DONATIONNUMBER'].dropna())
            
            logger.info(f"   📊 Bidding documents: {len(bid_docs)}, Donation numbers: {len(donation_nums)}")
            
            # Try different join strategies
            join_success = False
            
            # Strategy 1: Direct match on DONATIONNUMBER = DOCUMENTID
            if bid_docs.intersection(donation_nums):
                logger.info("   🔗 Direct join: DONATIONNUMBER = DOCUMENTID")
                donation_flow = donation_flow.merge(
                    bid_summary,
                    left_on='DONATIONNUMBER',
                    right_index=True,
                    how='left'
                )
                join_success = True
            else:
                logger.info("   📊 No direct match between DONATIONNUMBER and DOCUMENTID")
                logger.info(f"   📊 Sample bid documents: {list(bid_docs)[:5]}")
                logger.info(f"   📊 Sample donation numbers: {list(donation_nums)[:5]}")
                
                # Add bidding summary as separate context data
                total_bidding_activity = {
                    'total_bidding_documents': len(bid_docs),
                    'total_bids_placed': tables['bids_archive']['BIDAMOUNT'].count(),
                    'total_bid_value': tables['bids_archive']['BIDAMOUNT'].sum(),
                    'avg_bid_value': tables['bids_archive']['BIDAMOUNT'].mean(),
                    'unique_bidders': tables['bids_archive']['AFFILIATEWEBID'].nunique(),
                    'total_winning_bids': tables['bids_archive']['WINNINGBID'].sum(),
                    'bidding_date_range': f"{tables['bids_archive']['BIDDATE'].min()} to {tables['bids_archive']['BIDDATE'].max()}"
                }
                
                # Add as metadata columns
                for key, value in total_bidding_activity.items():
                    donation_flow[f'context_{key}'] = value
                
                logger.info("   📊 Added bidding context as metadata")
                
            logger.info(f"✅ Processed bidding data: {len(donation_flow):,} records")
        
        # Add share allocation information
        if 'shares' in tables:
            logger.info("🔗 Adding share allocation information...")
            
            # ACSHARES contains organization-level share data, not per-donation
            # Add as organizational context
            share_context = {
                'total_organizations_with_shares': tables['shares']['ORGNAME'].nunique(),
                'total_current_shares': tables['shares']['CURRENTSHARES'].sum(),
                'total_initial_shares': tables['shares']['INITIALSHARES'].sum(),
                'avg_shares_per_org': tables['shares']['CURRENTSHARES'].mean(),
                'organizations_by_state': tables['shares']['STATE'].value_counts().to_dict()
            }
            
            for key, value in share_context.items():
                donation_flow[f'share_context_{key}'] = str(value) if isinstance(value, dict) else value
            
            logger.info(f"✅ Added share allocation context: {len(donation_flow):,} records")
        
        # Add organization details for reference
        if 'organizations' in tables:
            logger.info("🔗 Adding organization reference data...")
            
            org_context = {
                'total_organizations': len(tables['organizations']),
                'active_organizations': len(tables['organizations'][tables['organizations']['STATUS_FLAG'] == 'A']),
                'organization_types': tables['organizations']['ORG_TYPE'].value_counts().to_dict()
            }
            
            for key, value in org_context.items():
                donation_flow[f'org_context_{key}'] = str(value) if isinstance(value, dict) else value
            
            logger.info(f"✅ Added organization context: {len(donation_flow):,} records")
        
        # Add computed flow tracking fields
        donation_flow['flow_stage'] = donation_flow.apply(self._determine_flow_stage, axis=1)
        donation_flow['completion_percentage'] = donation_flow.apply(self._calculate_completion_percentage, axis=1)
        donation_flow['data_richness_score'] = donation_flow.apply(self._calculate_data_richness, axis=1)
        donation_flow['processing_date'] = datetime.now()
        
        # Add derived fields for analysis
        if 'RELEASEDATE' in donation_flow.columns and 'DONATIONDATE' in donation_flow.columns:
            donation_flow['days_to_release'] = pd.to_datetime(donation_flow['RELEASEDATE'], errors='coerce') - pd.to_datetime(donation_flow['DONATIONDATE'], errors='coerce')
            donation_flow['days_to_release'] = donation_flow['days_to_release'].dt.days
        
        # Categorize by shipment method
        if 'SHIPMENTMETHOD' in donation_flow.columns:
            donation_flow['shipment_category'] = donation_flow['SHIPMENTMETHOD'].fillna('Unknown')
        
        # Categorize by donor
        if 'DONORNAME' in donation_flow.columns:
            donation_flow['donor_category'] = donation_flow['DONORNAME'].fillna('Unknown')
        
        logger.info(f"🎉 Unified donation flow dataset created: {len(donation_flow):,} records")
        logger.info(f"📊 Columns: {len(donation_flow.columns)}")
        
        return donation_flow
    
    def _determine_flow_stage(self, row) -> str:
        """Determine the current stage of the donation flow"""
        
        # Check completion stages in order based on available data
        if pd.notna(row.get('total_loads_won')) and row.get('total_loads_won', 0) > 0:
            return 'Won_Delivery'
        elif pd.notna(row.get('total_winning_amount')) and row.get('total_winning_amount', 0) > 0:
            return 'Won_Bidding'
        elif pd.notna(row.get('total_bids')) and row.get('total_bids', 0) > 0:
            return 'Active_Bidding'
        elif pd.notna(row.get('STATUS')) and row.get('STATUS') in ['Acknowledged', 'Released']:
            return 'Released'
        elif pd.notna(row.get('line_item_count')) and row.get('line_item_count', 0) > 0:
            return 'Detailed'
        elif pd.notna(row.get('DONATIONDATE')):
            return 'Created'
        else:
            return 'Draft'
    
    def _calculate_completion_percentage(self, row) -> float:
        """Calculate completion percentage based on flow stage"""
        
        stage = self._determine_flow_stage(row)
        
        stage_percentages = {
            'Draft': 5,
            'Created': 20,
            'Detailed': 40,
            'Released': 60,
            'Active_Bidding': 80,
            'Won_Bidding': 90,
            'Won_Delivery': 100
        }
        
        return stage_percentages.get(stage, 0)
    
    def _calculate_data_richness(self, row) -> float:
        """Calculate data richness score based on available fields"""
        
        # Count non-null important fields
        important_fields = [
            'DONATIONNUMBER', 'DONORNAME', 'DONATIONDATE', 'RELEASEDATE',
            'line_item_count', 'total_quantity', 'SHIPMENTMETHOD', 'STATUS'
        ]
        
        available_fields = sum(1 for field in important_fields 
                             if field in row.index and pd.notna(row.get(field)))
        richness_score = (available_fields / len(important_fields)) * 100
        
        return round(richness_score, 1)
    
    def create_analysis_views(self, donation_flow: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create specialized analysis views from unified dataset"""
        
        logger.info("🔄 Creating analysis views...")
        
        views = {}
        
        # Flow stage summary
        stage_summary = donation_flow.groupby('flow_stage').agg({
            'DONATIONNUMBER': 'count',
            'total_quantity': ['sum', 'mean'],
            'line_item_count': ['sum', 'mean'],
            'total_pallets': ['sum', 'mean'],
            'completion_percentage': 'mean',
            'data_richness_score': 'mean'
        }).round(2)
        
        stage_summary.columns = [
            'donation_count', 
            'total_qty', 'avg_qty',
            'total_line_items', 'avg_line_items',
            'total_pallets', 'avg_pallets',
            'avg_completion_pct', 'avg_data_richness'
        ]
        
        views['flow_stage_summary'] = stage_summary
        logger.info(f"✅ Flow stage summary: {len(stage_summary)} stages")
        
        # Donor performance analysis
        if 'DONORNAME' in donation_flow.columns:
            donor_performance = donation_flow.groupby('DONORNAME').agg({
                'DONATIONNUMBER': 'count',
                'total_quantity': ['sum', 'mean'],
                'line_item_count': ['sum', 'mean'], 
                'total_pallets': ['sum', 'mean'],
                'days_to_release': 'mean',
                'completion_percentage': 'mean'
            }).round(2)
            
            donor_performance.columns = [
                'total_donations',
                'total_donated_qty', 'avg_donated_qty',
                'total_line_items', 'avg_line_items',
                'total_pallets', 'avg_pallets',
                'avg_days_to_release',
                'avg_completion_pct'
            ]
            
            # Sort by total donations
            donor_performance = donor_performance.sort_values('total_donations', ascending=False)
            
            views['donor_performance'] = donor_performance
            logger.info(f"✅ Donor performance: {len(donor_performance)} donors")
        
        # Storage requirement analysis
        storage_data = donation_flow[donation_flow['primary_storage_requirement'].notna()]
        if len(storage_data) > 0:
            storage_analysis = storage_data.groupby('primary_storage_requirement').agg({
                'DONATIONNUMBER': 'count',
                'total_quantity': ['sum', 'mean'],
                'unique_items': ['sum', 'mean']
            }).round(2)
            
            storage_analysis.columns = [
                'donation_count',
                'total_qty', 'avg_qty', 
                'total_unique_items', 'avg_unique_items'
            ]
            
            views['storage_requirement_analysis'] = storage_analysis
            logger.info(f"✅ Storage requirement analysis: {len(storage_analysis)} requirements")
        
        # Bidding activity analysis (if bidding data was successfully joined)
        if 'total_bids' in donation_flow.columns:
            bidding_analysis = donation_flow[
                donation_flow['total_bids'].notna() & (donation_flow['total_bids'] > 0)
            ].copy()
            
            if len(bidding_analysis) > 0:
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
                    'unique_bidders': 'mean'
                }).round(2)
                
                competition_summary.columns = [
                    'donation_count',
                    'total_bid_value', 'avg_bid_value',
                    'total_won_value', 'avg_won_value',
                    'avg_unique_bidders'
                ]
                
                views['bidding_competition'] = competition_summary
                logger.info(f"✅ Bidding competition analysis: {len(competition_summary)} competition levels")
        
        # Time-based analysis (monthly trends)
        if 'DONATIONDATE' in donation_flow.columns:
            donation_flow_copy = donation_flow.copy()
            donation_flow_copy['DONATIONDATE'] = pd.to_datetime(donation_flow_copy['DONATIONDATE'], errors='coerce')
            donation_flow_copy['donation_month'] = donation_flow_copy['DONATIONDATE'].dt.to_period('M')
            
            monthly_trends = donation_flow_copy.groupby('donation_month').agg({
                'DONATIONNUMBER': 'count',
                'total_quantity': ['sum', 'mean'],
                'line_item_count': ['sum', 'mean']
            }).round(2)
            
            monthly_trends.columns = [
                'donation_count',
                'total_qty', 'avg_qty',
                'total_line_items', 'avg_line_items'
            ]
            
            views['monthly_donation_trends'] = monthly_trends
            logger.info(f"✅ Monthly trends: {len(monthly_trends)} months")
        
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
            'data_source': 'oracle_database_real',
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
            },
            'notes': [
                'This analysis was created from REAL Oracle database extractions',
                'Includes actual donation data, archived bidding records, and share allocations',
                'Ready for comprehensive dashboard visualization',
                f'Total records processed: {sum(self.processing_stats[table]["rows"] for table in self.processing_stats):,}'
            ]
        }
        
        metadata_file = self.output_dir / 'transformation_metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"✅ Saved metadata: {metadata_file}")
        
        return metadata
    
    def run_full_transformation(self) -> Dict:
        """Run complete bidding flow transformation pipeline"""
        
        logger.info("🚀 Starting bidding flow transformation with REAL Oracle data...")
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
            logger.info("🎯 Data source: REAL Oracle database")
            
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
    
    parser = argparse.ArgumentParser(description='HungerHub Bidding Flow Transformer (Real Oracle Data)')
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
            logger.info("🚀 Ready for dashboard visualization with REAL data!")
            return 0
        else:
            logger.error("🛑 Transformation failed")
            return 1
            
    except Exception as e:
        logger.error(f"💥 Pipeline failed: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
