"""
Quick test of sequential extraction of full AMX_DONATION_LINES dataset
"""
import os
import pandas as pd
import cx_Oracle
from dotenv import load_dotenv
import time
import pytest

# Load environment (ignore if missing)
try:
    load_dotenv('../config/.env')
except Exception:
    pass

def test_full_sequential():
    print("=== Full Sequential Extraction Test ===")
    start_time = time.time()
    
    # Connect to Oracle (skip if env not configured)
    host = os.getenv('CHOICE_ORACLE_HOST') or os.getenv('ORACLE_HOST')
    port = os.getenv('CHOICE_ORACLE_PORT', os.getenv('ORACLE_PORT', '1521'))
    service = os.getenv('CHOICE_ORACLE_SERVICE_NAME') or os.getenv('ORACLE_SERVICE_NAME')
    user = os.getenv('CHOICE_USERNAME') or os.getenv('ORACLE_USERNAME')
    password = os.getenv('CHOICE_PASSWORD') or os.getenv('ORACLE_PASSWORD')

    required = [host, service, user, password]
    if any(v in (None, "") for v in required):
        pytest.skip("Oracle connection env vars not set; skipping full sequential integration test.")
    
    dsn = cx_Oracle.makedsn(host, port, service_name=service)
    connection = cx_Oracle.connect(user, password, dsn, encoding='UTF-8')
    
    # Extract all rows
    query = "SELECT * FROM AMX_DONATION_LINES ORDER BY ROWID"
    df = pd.read_sql_query(query, connection)
    connection.close()
    
    duration = time.time() - start_time
    
    print(f"✅ Full sequential extraction completed:")
    print(f"   📊 Rows extracted: {len(df):,}")
    print(f"   ⏱️  Duration: {duration:.2f}s")
    print(f"   🚀 Throughput: {len(df)/duration:.1f} rows/sec")
    
    return {
        'rows': len(df),
        'duration': duration,
        'throughput': len(df)/duration
    }

if __name__ == "__main__":
    test_full_sequential()
