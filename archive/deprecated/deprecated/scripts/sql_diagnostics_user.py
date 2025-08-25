import os
import pandas as pd
import cx_Oracle
from dotenv import load_dotenv

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

if __name__ == "__main__":
    print("=== Oracle Database Diagnostics (User-Level) ===")
    
    # Test 1: Check user privileges and accessible views
    print("\n--- Test 1: User Privileges Check ---")
    privileges_query = """
    SELECT * FROM user_sys_privs WHERE rownum <= 10
    """
    priv_df = run_oracle_query(privileges_query, "User System Privileges")
    if not priv_df.empty and 'ERROR' not in priv_df.columns:
        print(priv_df.to_string(index=False))
    
    # Test 2: Check accessible tables/views
    print("\n\n--- Test 2: Accessible Views (DBA/System Views) ---")
    views_query = """
    SELECT view_name 
    FROM user_views 
    WHERE view_name LIKE '%RESOURCE%' OR view_name LIKE '%SESSION%'
    ORDER BY view_name
    """
    views_df = run_oracle_query(views_query, "Accessible System Views")
    if not views_df.empty and 'ERROR' not in views_df.columns:
        print(views_df.to_string(index=False))
    
    # Test 3: Try alternative session info queries
    print("\n\n--- Test 3: Current Session Info ---")
    session_query = """
    SELECT sys_context('USERENV', 'SESSIONID') as session_id,
           sys_context('USERENV', 'SERVER_HOST') as server_host,
           sys_context('USERENV', 'DB_NAME') as db_name,
           sys_context('USERENV', 'INSTANCE_NAME') as instance_name,
           sys_context('USERENV', 'SESSION_USER') as session_user
    FROM dual
    """
    session_df = run_oracle_query(session_query, "Current Session Information")
    if not session_df.empty and 'ERROR' not in session_df.columns:
        print(session_df.to_string(index=False))
    
    # Test 4: Test connection with multiple concurrent connections
    print("\n\n--- Test 4: Connection Stress Test ---")
    try:
        connections = []
        max_connections = 10
        
        for i in range(max_connections):
            try:
                conn = get_oracle_connection()
                connections.append(conn)
                print(f"   Connection {i+1}/10: ✅")
            except Exception as e:
                print(f"   Connection {i+1}/10: ❌ - {str(e)}")
                break
        
        print(f"\nSuccessfully created {len(connections)} concurrent connections")
        
        # Close all connections
        for conn in connections:
            conn.close()
        
    except Exception as e:
        print(f"Connection stress test failed: {e}")
    
    # Test 5: Check available tables to query
    print("\n\n--- Test 5: Available Tables for Analysis ---")
    tables_query = """
    SELECT table_name, num_rows 
    FROM user_tables 
    WHERE table_name LIKE '%DONATION%' OR table_name LIKE '%AMX%'
    ORDER BY table_name
    """
    tables_df = run_oracle_query(tables_query, "Available Tables")
    if not tables_df.empty and 'ERROR' not in tables_df.columns:
        print(tables_df.to_string(index=False))

