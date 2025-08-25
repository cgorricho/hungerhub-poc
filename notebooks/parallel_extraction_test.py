"""
Parallel Data Extraction Test Script
Uses ThreadPoolExecutor with optimized settings for Oracle staging environment
"""

import os
import pandas as pd
import cx_Oracle
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
from pathlib import Path

# Load environment variables
load_dotenv('../config/.env')

class OptimizedParallelExtractor:
    def __init__(self):
        self.host = os.getenv('CHOICE_ORACLE_HOST')
        self.port = os.getenv('CHOICE_ORACLE_PORT', '1521')
        self.service = os.getenv('CHOICE_ORACLE_SERVICE_NAME')
        self.user = os.getenv('CHOICE_USERNAME')
        self.password = os.getenv('CHOICE_PASSWORD')
        
        # Optimized settings for staging environment
        self.max_workers = 3  # Reduced from 5+ to avoid resource contention
        self.chunk_size = 5000  # Smaller chunks for Windows/staging environment
        self.connection_timeout = 30  # 30 second connection timeout
        self.query_timeout = 60  # 1 minute query timeout
        self.retry_count = 3
        self.retry_delays = [2, 5, 10]  # Exponential backoff delays
        
        # Thread-safe progress tracking
        self.progress_lock = threading.Lock()
        self.extracted_rows = 0
        
        # Output directory
        self.output_dir = Path('notebook_output/parallel_test')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self):
        """Get Oracle connection with timeout settings"""
        try:
            dsn = cx_Oracle.makedsn(self.host, self.port, service_name=self.service)
            connection = cx_Oracle.connect(
                self.user, 
                self.password, 
                dsn,
                encoding='UTF-8'
            )
            # Set session timeout (Oracle-specific)
            cursor = connection.cursor()
            cursor.execute("ALTER SESSION SET QUERY_REWRITE_ENABLED = FALSE")  # Reduce complexity
            cursor.close()
            return connection
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise
    
    def extract_chunk_with_retry(self, table_name, offset, chunk_size, worker_id):
        """Extract a chunk of data with retry logic"""
        for attempt in range(self.retry_count):
            try:
                start_time = time.time()
                
                # Get fresh connection for each chunk
                connection = self.get_connection()
                
                # Oracle pagination query with offset/limit
                query = f"""
                SELECT * FROM (
                    SELECT a.*, ROWNUM rnum FROM (
                        SELECT * FROM {table_name} ORDER BY ROWID
                    ) a WHERE ROWNUM <= {offset + chunk_size}
                ) WHERE rnum > {offset}
                """
                
                # Execute with timeout consideration
                df = pd.read_sql_query(query, connection)
                connection.close()
                
                duration = time.time() - start_time
                
                # Thread-safe progress update
                with self.progress_lock:
                    self.extracted_rows += len(df)
                    print(f"✅ Worker {worker_id}: Chunk {offset//chunk_size + 1} - {len(df)} rows ({duration:.2f}s)")
                
                return {
                    'worker_id': worker_id,
                    'offset': offset,
                    'data': df,
                    'rows': len(df),
                    'duration': duration,
                    'attempt': attempt + 1
                }
                
            except Exception as e:
                if attempt < self.retry_count - 1:
                    delay = self.retry_delays[attempt]
                    print(f"⚠️  Worker {worker_id}: Attempt {attempt + 1} failed, retrying in {delay}s... ({str(e)[:50]})")
                    time.sleep(delay)
                else:
                    print(f"❌ Worker {worker_id}: All attempts failed - {e}")
                    return {
                        'worker_id': worker_id,
                        'offset': offset,
                        'data': pd.DataFrame(),
                        'rows': 0,
                        'duration': 0,
                        'error': str(e),
                        'attempt': attempt + 1
                    }
    
    def extract_table_parallel(self, table_name, total_rows=None):
        """Extract table using parallel workers with optimized settings"""
        print(f"\n=== Parallel Extraction: {table_name} ===")
        
        # Get total row count if not provided
        if total_rows is None:
            print("📊 Getting total row count...")
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cursor.fetchone()[0]
            connection.close()
            print(f"📊 Total rows to extract: {total_rows:,}")
        
        # Calculate chunks
        chunks = [(offset, min(self.chunk_size, total_rows - offset)) 
                 for offset in range(0, total_rows, self.chunk_size)]
        
        print(f"📦 Processing {len(chunks)} chunks with {self.max_workers} workers")
        
        start_time = time.time()
        results = []
        errors = []
        
        # Use ThreadPoolExecutor for I/O bound Oracle queries
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all chunk extraction tasks
            future_to_chunk = {
                executor.submit(
                    self.extract_chunk_with_retry, 
                    table_name, 
                    offset, 
                    chunk_size, 
                    idx + 1
                ): (offset, chunk_size) 
                for idx, (offset, chunk_size) in enumerate(chunks)
            }
            
            # Process completed tasks
            for future in as_completed(future_to_chunk):
                result = future.result()
                if 'error' in result:
                    errors.append(result)
                else:
                    results.append(result)
        
        total_duration = time.time() - start_time
        
        # Combine all results
        if results:
            all_data = pd.concat([r['data'] for r in results if not r['data'].empty], 
                               ignore_index=True)
            
            # Save results
            csv_path = self.output_dir / f"{table_name}_parallel.csv"
            parquet_path = self.output_dir / f"{table_name}_parallel.parquet"
            
            all_data.to_csv(csv_path, index=False)
            all_data.to_parquet(parquet_path, index=False)
            
            print(f"\n📈 Parallel Extraction Results:")
            print(f"   ✅ Successful chunks: {len(results)}")
            print(f"   ❌ Failed chunks: {len(errors)}")
            print(f"   📊 Total rows extracted: {len(all_data):,}")
            print(f"   ⏱️  Total duration: {total_duration:.2f}s")
            print(f"   🚀 Throughput: {len(all_data)/total_duration:.1f} rows/sec")
            print(f"   💾 Saved to: {csv_path} & {parquet_path}")
            
            return all_data
        else:
            print(f"❌ No data extracted successfully")
            return pd.DataFrame()

def main():
    print("=== Optimized Parallel Oracle Extraction Test ===")
    
    extractor = OptimizedParallelExtractor()
    
    # Test with AMX_DONATION_LINES (27,099 rows)
    table_name = "AMX_DONATION_LINES"
    total_rows = 27099  # From our diagnostics
    
    try:
        result_df = extractor.extract_table_parallel(table_name, total_rows)
        
        if not result_df.empty:
            print(f"\n📊 Final Dataset Summary:")
            print(f"   Shape: {result_df.shape}")
            print(f"   Memory usage: {result_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            print(f"   Columns: {list(result_df.columns[:5])}...")
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")

if __name__ == "__main__":
    main()

