import os
import pandas as pd
import cx_Oracle
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('/home/tagazureuser/cgorr/2week_poc_execution/hungerhub_poc/config/.env')

def get_oracle_connection():
    """Get Oracle connection using environment variables"""
    host = os.getenv('CHOICE_ORACLE_HOST')
    port = os.getenv('CHOICE_ORACLE_PORT', '1521')
    service = os.getenv('CHOICE_ORACLE_SERVICE_NAME')
    user = os.getenv('CHOICE_USERNAME')
    password = os.getenv('CHOICE_PASSWORD')
    
    dsn = cx_Oracle.makedsn(host, port, service_name=service)
    return cx_Oracle.connect(user, password, dsn)

def run_oracle_query(query, description="Query"):
    """Run a query against Oracle and return DataFrame"""
    try:
        connection = get_oracle_connection()
        df = pd.read_sql_query(query, connection)
        connection.close()
        print(f"\n✅ {description} - Success:")
        return df
    except Exception as e:
        print(f"\n❌ {description} - Error: {str(e)}")
        return pd.DataFrame([{'ERROR': str(e)}])

def test_table_accessibility():
    """Test if we can query the problematic table"""
    print("\n--- Testing AMX_DONATION_LINES Table Access ---")
    
    # Test 1: Simple count
    count_query = "SELECT COUNT(*) as row_count FROM AMX_DONATION_LINES"
    count_df = run_oracle_query(count_query, "Table Row Count")
    if not count_df.empty and 'ERROR' not in count_df.columns:
        print(f"Total rows: {count_df.iloc[0]['row_count']}")
    
    # Test 2: First few rows
    sample_query = "SELECT * FROM AMX_DONATION_LINES WHERE rownum <= 5"
    sample_df = run_oracle_query(sample_query, "Sample Data")
    if not sample_df.empty and 'ERROR' not in sample_df.columns:
        print(f"Sample data shape: {sample_df.shape}")
        print(f"Columns: {list(sample_df.columns)}")
    
    # Test 3: Chunked query like the extraction script
    chunk_query = """
    SELECT * FROM AMX_DONATION_LINES 
    WHERE rownum > 0 AND rownum <= 1000
    """
    chunk_df = run_oracle_query(chunk_query, "Chunked Query Test")
    if not chunk_df.empty and 'ERROR' not in chunk_df.columns:
        print(f"Chunk query successful: {chunk_df.shape[0]} rows")

def test_concurrent_queries():
    """Test multiple concurrent queries to same table"""
    print("\n--- Testing Concurrent Access to AMX_DONATION_LINES ---")
    
    import threading
    import time
    
    results = []
    errors = []
    
    def worker_query(worker_id):
        try:
            start_time = time.time()
            connection = get_oracle_connection()
            cursor = connection.cursor()
            
            # Run a chunked query
            query = f"""
            SELECT COUNT(*) 
            FROM AMX_DONATION_LINES 
            WHERE rownum <= 1000
            """
            cursor.execute(query)
            result = cursor.fetchone()
            
            connection.close()
            duration = time.time() - start_time
            
            results.append({
                'worker_id': worker_id,
                'count': result[0] if result else None,
                'duration': duration,
                'status': 'SUCCESS'
            })
            print(f"   Worker {worker_id}: ✅ ({duration:.2f}s)")
            
        except Exception as e:
            errors.append({
                'worker_id': worker_id,
                'error': str(e),
                'status': 'ERROR'
            })
            print(f"   Worker {worker_id}: ❌ - {str(e)}")
    
    # Start 5 concurrent workers
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker_query, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    # Wait for all to complete
    for thread in threads:
        thread.join()
    
    print(f"\nConcurrent test results:")
    print(f"  Successful queries: {len(results)}")
    print(f"  Failed queries: {len(errors)}")
    
    if errors:
        print("  Error details:")
        for error in errors:
            print(f"    Worker {error['worker_id']}: {error['error']}")

if __name__ == "__main__":
    print("=== Oracle Table Access Diagnostics ===")
    test_table_accessibility()
    test_concurrent_queries()

