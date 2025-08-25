import os
import pandas as pd
import cx_Oracle
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/home/tagazureuser/cgorr/2week_poc_execution/hungerhub_poc/config/.env')

def get_oracle_connection():
    host = os.getenv('CHOICE_ORACLE_HOST')
    port = os.getenv('CHOICE_ORACLE_PORT', '1521')
    service = os.getenv('CHOICE_ORACLE_SERVICE_NAME')
    user = os.getenv('CHOICE_USERNAME')
    password = os.getenv('CHOICE_PASSWORD')
    
    dsn = cx_Oracle.makedsn(host, port, service_name=service)
    return cx_Oracle.connect(user, password, dsn)

if __name__ == "__main__":
    print("=== Simple Oracle Diagnostics ===")
    
    try:
        # Test 1: Simple count
        print("\n--- Test 1: AMX_DONATION_LINES Row Count ---")
        connection = get_oracle_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM AMX_DONATION_LINES")
        count = cursor.fetchone()[0]
        print(f"✅ Total rows: {count}")
        connection.close()
        
        # Test 2: Sample data
        print("\n--- Test 2: Sample Data ---")
        connection = get_oracle_connection()
        df = pd.read_sql_query("SELECT * FROM AMX_DONATION_LINES WHERE rownum <= 3", connection)
        print(f"✅ Sample data shape: {df.shape}")
        print(f"✅ Columns: {list(df.columns)}")
        connection.close()
        
        # Test 3: Multiple concurrent connections (simplified)
        print("\n--- Test 3: Concurrent Connection Test ---")
        connections = []
        for i in range(5):
            try:
                conn = get_oracle_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM dual")
                result = cursor.fetchone()
                connections.append(conn)
                print(f"✅ Connection {i+1}: SUCCESS")
            except Exception as e:
                print(f"❌ Connection {i+1}: {str(e)}")
                break
        
        # Close all connections
        for conn in connections:
            conn.close()
        print(f"✅ Successfully created and closed {len(connections)} connections")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

