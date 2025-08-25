#!/usr/bin/env python3
"""
Complete Bidding Extraction Pipeline for HungerHub POC
Runs the full pipeline: Extract bidding tables → Transform → Create donation flow analysis

Usage:
    python run_bidding_extraction_pipeline.py [--test-connection] [--tier all_priority]
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_extraction_step(tier='high_priority', test_connection=False):
    """Run the data extraction step"""
    logger.info(f"🔄 STEP 1: Running data extraction (tier: {tier})")
    
    extraction_script = Path('src/data_extraction/full_data_extractor.py')
    
    if not extraction_script.exists():
        logger.error(f"❌ Extraction script not found: {extraction_script}")
        return False
    
    # Build command
    cmd = [sys.executable, str(extraction_script)]
    
    if test_connection:
        cmd.append('--test-connection')
        logger.info("   🧪 Testing connection only...")
    else:
        cmd.extend(['--tier', tier])
        logger.info(f"   📊 Extracting {tier} tables with bidding data...")
    
    try:
        # Run extraction
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
        
        if result.returncode == 0:
            logger.info("   ✅ Data extraction completed successfully!")
            if result.stdout:
                for line in result.stdout.strip().split('\n')[-10:]:  # Last 10 lines
                    logger.info(f"   📄 {line}")
            return True
        else:
            logger.error(f"   ❌ Extraction failed (return code: {result.returncode})")
            if result.stderr:
                logger.error(f"   📄 Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("   ❌ Extraction timed out after 30 minutes")
        return False
    except Exception as e:
        logger.error(f"   ❌ Extraction error: {e}")
        return False

def run_transformation_step():
    """Run the bidding flow transformation step"""
    logger.info("🔄 STEP 2: Running bidding flow transformation")
    
    transformation_script = Path('src/bidding_flow_transformer.py')
    
    if not transformation_script.exists():
        logger.error(f"❌ Transformation script not found: {transformation_script}")
        return False
    
    # Build command
    cmd = [sys.executable, str(transformation_script)]
    
    try:
        # Run transformation
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
        
        if result.returncode == 0:
            logger.info("   ✅ Bidding flow transformation completed successfully!")
            if result.stdout:
                for line in result.stdout.strip().split('\n')[-15:]:  # Last 15 lines
                    logger.info(f"   📄 {line}")
            return True
        else:
            logger.error(f"   ❌ Transformation failed (return code: {result.returncode})")
            if result.stderr:
                logger.error(f"   📄 Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("   ❌ Transformation timed out after 10 minutes")
        return False
    except Exception as e:
        logger.error(f"   ❌ Transformation error: {e}")
        return False

def verify_output_files():
    """Verify that expected output files were created"""
    logger.info("🔍 STEP 3: Verifying output files")
    
    expected_files = [
        'data/processed/unified_real/donation_flow_complete.parquet',
        'data/processed/unified_real/donation_flow_complete.csv',
        'data/processed/unified_real/donor_analysis.parquet',
        'data/processed/unified_real/item_analysis.parquet', 
        'data/processed/unified_real/bidding_analysis.parquet',
        'data/processed/unified_real/destination_analysis.parquet',
        'data/analysis/bidding_flow_transformation_metadata.json'
    ]
    
    files_found = 0
    total_records = 0
    
    for file_path in expected_files:
        path = Path(file_path)
        if path.exists():
            files_found += 1
            size_mb = path.stat().st_size / 1024**2
            
            # Try to count records for data files
            record_count = "N/A"
            if file_path.endswith('.parquet'):
                try:
                    import pandas as pd
                    df = pd.read_parquet(path)
                    record_count = f"{len(df):,}"
                    total_records += len(df)
                except:
                    pass
            
            logger.info(f"   ✅ {path.name}: {size_mb:.2f}MB ({record_count} records)")
        else:
            logger.warning(f"   ❌ Missing: {path}")
    
    logger.info(f"📊 Files created: {files_found}/{len(expected_files)}")
    if total_records > 0:
        logger.info(f"📊 Total records created: {total_records:,}")
    
    return files_found >= len(expected_files) * 0.8  # 80% success rate

def generate_summary_report():
    """Generate final pipeline summary"""
    logger.info("📋 STEP 4: Generating pipeline summary")
    
    summary = {
        'pipeline_completion_time': datetime.now().isoformat(),
        'success': True,
        'ready_for_visualization': True
    }
    
    # Check if key files exist for donation tracking visualization
    key_files = [
        'data/processed/unified_real/donation_flow_complete.parquet',
        'data/processed/unified_real/donor_analysis.parquet',
        'data/processed/unified_real/bidding_analysis.parquet'
    ]
    
    files_ready = all(Path(f).exists() for f in key_files)
    
    if files_ready:
        logger.info("   ✅ All key files ready for donation tracking visualization!")
        logger.info("   🎯 Next step: Update DONATION_TRACKING_VISUALIZATION_PLAN.md")
        logger.info("   📊 Available data flows:")
        logger.info("      1. Donor → Items (AMX_DONATION_* tables)")
        logger.info("      2. Items → Bidding (ACBIDS connections)")
        logger.info("      3. Bidding → Winners (ACWINNER connections)")
        logger.info("      4. Winners → Final Agencies (RW_ORG connections)")
    else:
        logger.warning("   ⚠️ Some key files missing - visualization may be limited")
        summary['success'] = False
        summary['ready_for_visualization'] = False
    
    return summary

def main():
    """Main pipeline orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='HungerHub Bidding Extraction Pipeline')
    parser.add_argument('--tier', 
                       choices=['high_priority', 'medium_priority', 'all_priority'],
                       default='high_priority',
                       help='Table priority tier to extract')
    parser.add_argument('--test-connection', action='store_true',
                       help='Test Oracle connection only')
    parser.add_argument('--skip-extraction', action='store_true',
                       help='Skip extraction and run transformation only')
    
    args = parser.parse_args()
    
    start_time = datetime.now()
    
    logger.info("🚀 ===== HUNGERHUB BIDDING EXTRACTION PIPELINE =====")
    logger.info(f"⏰ Started: {start_time}")
    logger.info(f"🎯 Tier: {args.tier}")
    logger.info(f"📊 Goal: Enable donation flow tracking visualization")
    logger.info("=" * 60)
    
    success = True
    
    # Step 1: Data extraction (unless skipped)
    if not args.skip_extraction:
        if not run_extraction_step(args.tier, args.test_connection):
            logger.error("💥 Pipeline failed at extraction step")
            return 1
        
        if args.test_connection:
            logger.info("🧪 Connection test completed - pipeline stopped")
            return 0
    else:
        logger.info("⏭️ Skipping extraction step as requested")
    
    # Step 2: Bidding flow transformation 
    if not run_transformation_step():
        logger.error("💥 Pipeline failed at transformation step")
        return 1
    
    # Step 3: Verify outputs
    if not verify_output_files():
        logger.warning("⚠️ Pipeline completed with missing files")
        success = False
    
    # Step 4: Generate summary
    summary = generate_summary_report()
    
    # Final results
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=" * 60)
    logger.info("🏁 PIPELINE COMPLETED")
    logger.info(f"⏱️  Duration: {duration.total_seconds()/60:.1f} minutes")
    logger.info(f"✅ Success: {summary['success']}")
    logger.info(f"🎯 Ready for visualization: {summary['ready_for_visualization']}")
    
    if summary['ready_for_visualization']:
        logger.info("")
        logger.info("🎉 SUCCESS: Donation flow tracking data ready!")
        logger.info("📊 You can now implement the donation tracking visualization")
        logger.info("📋 Next steps:")
        logger.info("   1. Review data in data/processed/unified_real/")
        logger.info("   2. Update donation_tracking_plan with actual data sources")
        logger.info("   3. Create donation flow dashboard tab")
        return 0
    else:
        logger.error("❌ Pipeline completed with errors - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
