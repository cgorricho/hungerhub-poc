#!/usr/bin/env python3
"""
Recovery script for stuck AMX_DONATION_LINES extraction
"""
import os
import sys
import pandas as pd
import cx_Oracle
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from pathlib import Path

# Add the src directory to the path
sys.path.append('/home/tagazureuser/cgorr/2week_poc_execution/hungerhub_poc/src')

from database.oracle_connection import get_oracle_connection
from utils.oracle_utils import get_table_schema, get_table_count, extract_table_data

def extract_table_safely(table_name, chunk_size=1000, max_workers=2):
    """Extract a specific table with better error handling"""
    print(f"\n🔄 Starting safe extraction for {table_name}")
    
    try:
        # Get connection
        conn = get_oracle_connection('choice')
        if not conn:
            print(f"❌ Failed to connect to choice database")
            return False
        
        print(f"✅ Connected to choice database")
        
        # Get table info
        try:
            count = get_table_count(conn, table_name)
            print(f"📊 Table {table_name} has {count:,} rows")
        except Exception as e:
            print(f"⚠️  Could not get count for {table_name}: {e}")
            count = None
        
        # Create output directory
        output_dir = Path("../data/extracted_recovery")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Extract with smaller chunks if it's a large table
        if table_name == 'AMX_DONATION_LINES':
            chunk_size = 500  # Smaller chunks for problematic table
        
        print(f"📥 Extracting {table_name} with chunk size {chunk_size}")
        
        start_time = time.time()
        df = extract_table_data(conn, table_name, chunk_size=chunk_size)
        end_time = time.time()
        
        if df is not None and not df.empty:
            # Save both CSV and Parquet
            csv_path = output_dir / f"{table_name}.csv"
            parquet_path = output_dir / f"{table_name}.parquet"
            
            df.to_csv(csv_path, index=False)
            df.to_parquet(parquet_path, index=False)
            
            print(f"✅ Successfully extracted {len(df):,} rows from {table_name}")
            print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
            print(f"💾 Saved to: {csv_path} and {parquet_path}")
            return True
        else:
            print(f"❌ No data extracted for {table_name}")
            return False
            
    except Exception as e:
        print(f"❌ Error extracting {table_name}: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting recovery extraction for AMX_DONATION_LINES")
    
    # Try to extract the problematic table
    success = extract_table_safely("AMX_DONATION_LINES")
    
    if success:
        print("✅ Recovery extraction completed successfully!")
    else:
        print("❌ Recovery extraction failed")
        sys.exit(1)
