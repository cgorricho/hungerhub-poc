#!/usr/bin/env python3
"""
Simple extraction script for AMX_DONATION_LINES - Fixed
"""
import os
import pandas as pd
import cx_Oracle
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('../config/.env')

def get_connection():
    """Get Oracle connection using correct env vars"""
    try:
        # Choice database connection
        host = os.getenv('CHOICE_ORACLE_HOST')
        port = os.getenv('CHOICE_ORACLE_PORT')
        service_name = os.getenv('CHOICE_ORACLE_SERVICE_NAME')
        username = os.getenv('CHOICE_USERNAME')
        password = os.getenv('CHOICE_PASSWORD')
        
        print(f"🔌 Connecting to {host}:{port}/{service_name}")
        
        dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        connection = cx_Oracle.connect(username, password, dsn)
        
        print("✅ Connected successfully")
        return connection
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def extract_table_simple(table_name, limit=2000):
    """Extract table data with limit"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        print(f"📥 Extracting up to {limit} rows from {table_name}")
        start_time = time.time()
        
        query = f"SELECT * FROM {table_name} WHERE ROWNUM <= {limit}"
        df = pd.read_sql(query, conn)
        
        end_time = time.time()
        print(f"✅ Extracted {len(df)} rows in {end_time - start_time:.2f} seconds")
        return df
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Simple AMX_DONATION_LINES extraction (Fixed)")
    
    df = extract_table_simple("AMX_DONATION_LINES", 2000)
    
    if df is not None:
        # Save to recovery folder
        os.makedirs("../data/extracted_recovery", exist_ok=True)
        
        csv_path = "../data/extracted_recovery/AMX_DONATION_LINES_recovery.csv"
        parquet_path = "../data/extracted_recovery/AMX_DONATION_LINES_recovery.parquet"
        
        df.to_csv(csv_path, index=False)
        df.to_parquet(parquet_path, index=False)
        
        print(f"✅ Data saved successfully")
        print(f"📊 Shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        print(f"💾 Files saved:")
        print(f"   - {csv_path}")
        print(f"   - {parquet_path}")
    else:
        print("❌ Extraction failed")
