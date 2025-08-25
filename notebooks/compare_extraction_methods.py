"""
Comparison script to test and compare different Oracle extraction methods
"""

import os
import pandas as pd
import cx_Oracle
from dotenv import load_dotenv
import time
from pathlib import Path
import subprocess
import sys

# Load environment variables
load_dotenv('../config/.env')

class ExtractionComparator:
    def __init__(self):
        self.host = os.getenv('CHOICE_ORACLE_HOST')
        self.port = os.getenv('CHOICE_ORACLE_PORT', '1521')
        self.service = os.getenv('CHOICE_ORACLE_SERVICE_NAME')
        self.user = os.getenv('CHOICE_USERNAME')
        self.password = os.getenv('CHOICE_PASSWORD')
        
        # Test parameters
        self.test_table = "AMX_DONATION_LINES"
        self.test_rows = 27099  # Known row count
        self.sample_size = 10000  # Test with 10K rows for speed
        
        # Output directory
        self.output_dir = Path('notebook_output/comparison_test')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self):
        """Get Oracle connection"""
        dsn = cx_Oracle.makedsn(self.host, self.port, service_name=self.service)
        return cx_Oracle.connect(self.user, self.password, dsn, encoding='UTF-8')
    
    def test_sequential_extraction(self):
        """Test traditional sequential extraction"""
        print("\n=== Testing Sequential Extraction ===")
        
        start_time = time.time()
        
        try:
            connection = self.get_connection()
            
            # Simple sequential query with ROWNUM limit
            query = f"""
            SELECT * FROM (
                SELECT * FROM {self.test_table} ORDER BY ROWID
            ) WHERE ROWNUM <= {self.sample_size}
            """
            
            df = pd.read_sql_query(query, connection)
            connection.close()
            
            duration = time.time() - start_time
            
            # Save result
            output_path = self.output_dir / f"{self.test_table}_sequential.csv"
            df.to_csv(output_path, index=False)
            
            print(f"✅ Sequential extraction completed:")
            print(f"   📊 Rows extracted: {len(df):,}")
            print(f"   ⏱️  Duration: {duration:.2f}s")
            print(f"   🚀 Throughput: {len(df)/duration:.1f} rows/sec")
            print(f"   💾 Saved to: {output_path}")
            
            return {
                'method': 'Sequential',
                'rows': len(df),
                'duration': duration,
                'throughput': len(df)/duration,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Sequential extraction failed: {e}")
            return {
                'method': 'Sequential',
                'rows': 0,
                'duration': 0,
                'throughput': 0,
                'success': False,
                'error': str(e)
            }
    
    def test_chunked_extraction(self):
        """Test chunked sequential extraction"""
        print("\n=== Testing Chunked Sequential Extraction ===")
        
        start_time = time.time()
        chunk_size = 2000
        chunks = []
        
        try:
            for offset in range(0, self.sample_size, chunk_size):
                current_chunk_size = min(chunk_size, self.sample_size - offset)
                
                connection = self.get_connection()
                
                query = f"""
                SELECT * FROM (
                    SELECT a.*, ROWNUM rnum FROM (
                        SELECT * FROM {self.test_table} ORDER BY ROWID
                    ) a WHERE ROWNUM <= {offset + current_chunk_size}
                ) WHERE rnum > {offset}
                """
                
                chunk_df = pd.read_sql_query(query, connection)
                connection.close()
                
                chunks.append(chunk_df)
                print(f"   📦 Chunk {len(chunks)}: {len(chunk_df)} rows")
            
            # Combine chunks
            df = pd.concat(chunks, ignore_index=True)
            duration = time.time() - start_time
            
            # Save result
            output_path = self.output_dir / f"{self.test_table}_chunked.csv"
            df.to_csv(output_path, index=False)
            
            print(f"✅ Chunked extraction completed:")
            print(f"   📊 Rows extracted: {len(df):,}")
            print(f"   📦 Total chunks: {len(chunks)}")
            print(f"   ⏱️  Duration: {duration:.2f}s")
            print(f"   🚀 Throughput: {len(df)/duration:.1f} rows/sec")
            print(f"   💾 Saved to: {output_path}")
            
            return {
                'method': 'Chunked Sequential',
                'rows': len(df),
                'duration': duration,
                'throughput': len(df)/duration,
                'chunks': len(chunks),
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Chunked extraction failed: {e}")
            return {
                'method': 'Chunked Sequential',
                'rows': 0,
                'duration': 0,
                'throughput': 0,
                'success': False,
                'error': str(e)
            }
    
    def run_external_script(self, script_name):
        """Run external Python script and capture output"""
        try:
            script_path = f"notebooks/{script_name}"
            result = subprocess.run([
                sys.executable, script_path
            ], capture_output=True, text=True, timeout=300)  # 5 min timeout
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Script timed out after 5 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def compare_all_methods(self):
        """Compare all extraction methods"""
        print("=== Oracle Extraction Method Comparison ===")
        print(f"Testing with {self.sample_size:,} rows from {self.test_table}")
        
        results = []
        
        # Test 1: Sequential
        seq_result = self.test_sequential_extraction()
        results.append(seq_result)
        
        # Test 2: Chunked Sequential
        chunked_result = self.test_chunked_extraction()
        results.append(chunked_result)
        
        # Test 3: Parallel (external script)
        print("\n=== Testing Parallel Extraction (External Script) ===")
        parallel_result = self.run_external_script('parallel_extraction_test.py')
        if parallel_result['success']:
            print("✅ Parallel script executed successfully")
            print("📄 Output preview:")
            print(parallel_result['stdout'][-500:])  # Last 500 chars
        else:
            print(f"❌ Parallel script failed: {parallel_result.get('error', 'Unknown error')}")
            if 'stderr' in parallel_result:
                print(f"Error output: {parallel_result['stderr'][-300:]}")
        
        # Test 4: Concurrent (external script)
        print("\n=== Testing Concurrent Extraction (External Script) ===")
        concurrent_result = self.run_external_script('concurrent_extraction_test.py')
        if concurrent_result['success']:
            print("✅ Concurrent script executed successfully")
            print("📄 Output preview:")
            print(concurrent_result['stdout'][-500:])  # Last 500 chars
        else:
            print(f"❌ Concurrent script failed: {concurrent_result.get('error', 'Unknown error')}")
            if 'stderr' in concurrent_result:
                print(f"Error output: {concurrent_result['stderr'][-300:]}")
        
        # Summary
        print("\n" + "="*60)
        print("📊 EXTRACTION METHOD COMPARISON SUMMARY")
        print("="*60)
        
        for result in results:
            if result['success']:
                print(f"\n✅ {result['method']}:")
                print(f"   📊 Rows: {result['rows']:,}")
                print(f"   ⏱️  Duration: {result['duration']:.2f}s")
                print(f"   🚀 Throughput: {result['throughput']:.1f} rows/sec")
            else:
                print(f"\n❌ {result['method']}: FAILED")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
        
        # Check output files
        print(f"\n📁 Output files saved in: {self.output_dir}")
        output_files = list(self.output_dir.glob('*.csv'))
        for file in output_files:
            size_mb = file.stat().st_size / 1024**2
            print(f"   📄 {file.name} ({size_mb:.2f} MB)")

def main():
    comparator = ExtractionComparator()
    comparator.compare_all_methods()

if __name__ == "__main__":
    main()

