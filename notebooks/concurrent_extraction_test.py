"""
Concurrent Data Extraction Test Script
Uses asyncio with ThreadPoolExecutor for Oracle staging environment
"""

import os
import pandas as pd
import cx_Oracle
from dotenv import load_dotenv
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from pathlib import Path
import threading

# Load environment variables
load_dotenv('../config/.env')

class OptimizedConcurrentExtractor:
    def __init__(self):
        self.host = os.getenv('CHOICE_ORACLE_HOST')
        self.port = os.getenv('CHOICE_ORACLE_PORT', '1521')
        self.service = os.getenv('CHOICE_ORACLE_SERVICE_NAME')
        self.user = os.getenv('CHOICE_USERNAME')
        self.password = os.getenv('CHOICE_PASSWORD')
        
        # Conservative settings for staging environment
        self.max_concurrent = 4  # Async concurrency limit
        self.chunk_size = 5000   # Conservative chunk size
        self.connection_timeout = 30
        self.query_timeout = 60
        self.retry_count = 3
        self.retry_delays = [2, 5, 10]
        
        # Thread-safe progress tracking
        self.progress_lock = threading.Lock()
        self.extracted_rows = 0
        self.completed_chunks = 0
        
        # Output directory
        self.output_dir = Path('notebook_output/concurrent_test')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self):
        """Get Oracle connection (synchronous for use in thread pool)"""
        try:
            dsn = cx_Oracle.makedsn(self.host, self.port, service_name=self.service)
            connection = cx_Oracle.connect(
                self.user, 
                self.password, 
                dsn,
                encoding='UTF-8'
            )
            # Optimize session settings
            cursor = connection.cursor()
            cursor.execute("ALTER SESSION SET QUERY_REWRITE_ENABLED = FALSE")
            cursor.execute("ALTER SESSION SET OPTIMIZER_MODE = FIRST_ROWS")
            cursor.close()
            return connection
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise
    
    def extract_chunk_sync(self, table_name, offset, chunk_size, worker_id):
        """Synchronous chunk extraction (runs in thread pool)"""
        for attempt in range(self.retry_count):
            try:
                start_time = time.time()
                
                # Get connection
                connection = self.get_connection()
                
                # Optimized Oracle pagination query
                query = f"""
                SELECT * FROM (
                    SELECT a.*, ROWNUM rnum FROM (
                        SELECT /*+ FIRST_ROWS({chunk_size}) */ * 
                        FROM {table_name} 
                        ORDER BY ROWID
                    ) a WHERE ROWNUM <= {offset + chunk_size}
                ) WHERE rnum > {offset}
                """
                
                # Execute query with pandas
                df = pd.read_sql_query(query, connection)
                connection.close()
                
                duration = time.time() - start_time
                
                # Thread-safe progress update
                with self.progress_lock:
                    self.extracted_rows += len(df)
                    self.completed_chunks += 1
                    print(f"✅ Worker {worker_id}: Chunk {self.completed_chunks} - {len(df)} rows ({duration:.2f}s)")
                
                return {
                    'worker_id': worker_id,
                    'offset': offset,
                    'data': df,
                    'rows': len(df),
                    'duration': duration,
                    'success': True
                }
                
            except Exception as e:
                if attempt < self.retry_count - 1:
                    delay = self.retry_delays[attempt]
                    print(f"⚠️  Worker {worker_id}: Retry {attempt + 1} in {delay}s... ({str(e)[:50]})")
                    time.sleep(delay)
                else:
                    print(f"❌ Worker {worker_id}: Failed after {self.retry_count} attempts - {e}")
                    return {
                        'worker_id': worker_id,
                        'offset': offset,
                        'data': pd.DataFrame(),
                        'rows': 0,
                        'duration': 0,
                        'error': str(e),
                        'success': False
                    }
    
    async def extract_chunk_async(self, executor, table_name, offset, chunk_size, worker_id):
        """Async wrapper for chunk extraction"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor, 
            self.extract_chunk_sync, 
            table_name, 
            offset, 
            chunk_size, 
            worker_id
        )
        return result
    
    async def extract_table_concurrent(self, table_name, total_rows=None):
        """Extract table using async concurrency with thread pool"""
        print(f"\n=== Concurrent Extraction: {table_name} ===")
        
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
        
        print(f"📦 Processing {len(chunks)} chunks with {self.max_concurrent} concurrent workers")
        
        start_time = time.time()
        results = []
        
        # Create thread pool executor for sync Oracle operations
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Create semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def process_chunk_with_limit(chunk_data):
                async with semaphore:
                    offset, chunk_size = chunk_data
                    worker_id = chunks.index(chunk_data) + 1
                    return await self.extract_chunk_async(
                        executor, table_name, offset, chunk_size, worker_id
                    )
            
            # Process all chunks concurrently
            tasks = [process_chunk_with_limit(chunk) for chunk in chunks]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_duration = time.time() - start_time
        
        # Process results
        successful_results = [r for r in results if isinstance(r, dict) and r.get('success', False)]
        failed_results = [r for r in results if isinstance(r, dict) and not r.get('success', True)]
        exceptions = [r for r in results if isinstance(r, Exception)]
        
        if successful_results:
            all_data = pd.concat([r['data'] for r in successful_results if not r['data'].empty], 
                               ignore_index=True)
            
            # Save results
            csv_path = self.output_dir / f"{table_name}_concurrent.csv"
            parquet_path = self.output_dir / f"{table_name}_concurrent.parquet"
            
            all_data.to_csv(csv_path, index=False)
            all_data.to_parquet(parquet_path, index=False)
            
            print(f"\n📈 Concurrent Extraction Results:")
            print(f"   ✅ Successful chunks: {len(successful_results)}")
            print(f"   ❌ Failed chunks: {len(failed_results) + len(exceptions)}")
            print(f"   📊 Total rows extracted: {len(all_data):,}")
            print(f"   ⏱️  Total duration: {total_duration:.2f}s")
            print(f"   🚀 Throughput: {len(all_data)/total_duration:.1f} rows/sec")
            print(f"   💾 Saved to: {csv_path} & {parquet_path}")
            
            return all_data
        else:
            print(f"❌ No data extracted successfully")
            return pd.DataFrame()

async def main():
    print("=== Optimized Concurrent Oracle Extraction Test ===")
    
    extractor = OptimizedConcurrentExtractor()
    
    # Test with AMX_DONATION_LINES (27,099 rows)
    table_name = "AMX_DONATION_LINES"
    total_rows = 27099  # From our diagnostics
    
    try:
        result_df = await extractor.extract_table_concurrent(table_name, total_rows)
        
        if not result_df.empty:
            print(f"\n📊 Final Dataset Summary:")
            print(f"   Shape: {result_df.shape}")
            print(f"   Memory usage: {result_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            print(f"   Columns: {list(result_df.columns[:5])}...")
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())

