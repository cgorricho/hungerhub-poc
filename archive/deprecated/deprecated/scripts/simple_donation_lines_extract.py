#!/usr/bin/env python3
"""
Simple extraction script for AMX_DONATION_LINES
"""
import os
import pandas as pd
import cx_Oracle
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('../config/.env')

def get_connection():
    """Get Oracle connection"""
    try:
        # Choice database connection
        choice_user = os.getenv('CHOICE_DB_USER')
        choice_password = os.getenv('CHOICE_DB_PASSWORD')
        choice_dsn = os.getenv('CHOICE_DB_DSN')
        
        dsn = cx_Oracle.makedsn(
            choice_dsn.split(':')[0],
            choice_dsn.split(':')[1], 
            service_name="XE"
        )
        
        connection = cx_Oracle.connect(choice_user, choice_password, dsn)
        return connection
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def extract_table_simple(table_name, limit=1000):
    """Extract table data with limit"""
    conn = get_connection()
    if not conn:
        return None
    
    try:
        print(f"📥 Extracting {limit} rows from {table_name}")
        
        query = f"SELECT * FROM {table_name} WHERE ROWNUM <= {limit}"
        df = pd.read_sql(query, conn)
        
        print(f"✅ Extracted {len(df)} rows")
        return df
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Simple AMX_DONATION_LINES extraction")
    
    df = extract_table_simple("AMX_DONATION_LINES", 2000)
    
    if df is not None:
        # Save to recovery folder
        os.makedirs("../data/extracted_recovery", exist_ok=True)
        df.to_csv("../data/extracted_recovery/AMX_DONATION_LINES_simple.csv", index=False)
        df.to_parquet("../data/extracted_recovery/AMX_DONATION_LINES_simple.parquet", index=False)
        print("✅ Data saved successfully")
        print(f"📊 Shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)[:10]}...")  # First 10 columns
    else:
        print("❌ Extraction failed")
