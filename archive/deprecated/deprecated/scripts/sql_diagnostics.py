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
    
    if not all([host, service, user, password]):
        print(f"Missing vars - Host: {host}, Service: {service}, User: {user}, Password: {'***' if password else None}")
        raise ValueError("Missing required Oracle environment variables")
    
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
    print("=== Oracle Database Diagnostics ===")
    
    # Test 1: Check Resource Limits (Session/Process limits)
    print("\n--- Test 1: Oracle Resource Limits ---")
    limits_query = """
    SELECT resource_name, current_utilization, max_utilization, limit_value
    FROM v$resource_limit
    WHERE resource_name IN ('sessions', 'processes', 'db_files', 'cursors')
    ORDER BY resource_name
    """
    limits_df = run_oracle_query(limits_query, "Resource Limits Check")
    if not limits_df.empty and 'ERROR' not in limits_df.columns:
        print(limits_df.to_string(index=False))
    
    # Test 2: Check Current User Sessions
    print("\n\n--- Test 2: Current User Active Sessions ---")
    user = os.getenv('CHOICE_USERNAME', '').upper()
    sessions_query = f"""
    SELECT sid, serial#, status, blocking_session, wait_class, event, 
           seconds_in_wait, logon_time, last_call_et
    FROM v$session 
    WHERE username = '{user}'
    ORDER BY logon_time DESC
    """
    sessions_df = run_oracle_query(sessions_query, "User Sessions Check")
    if not sessions_df.empty and 'ERROR' not in sessions_df.columns:
        print(sessions_df.to_string(index=False))
    else:
        print(f"No active sessions found for user: {user}")
    
    # Test 3: Check System Wait Events (blocking issues)
    print("\n\n--- Test 3: Current System Wait Events ---")
    waits_query = """
    SELECT event, total_waits, total_timeouts, time_waited, average_wait
    FROM v$system_event
    WHERE event IN (
        'enq: TX - row lock contention',
        'buffer busy waits',
        'db file sequential read',
        'db file scattered read',
        'library cache lock',
        'shared pool latch'
    )
    AND total_waits > 0
    ORDER BY time_waited DESC
    """
    waits_df = run_oracle_query(waits_query, "System Wait Events")
    if not waits_df.empty and 'ERROR' not in waits_df.columns:
        print(waits_df.to_string(index=False))
    
    # Test 4: Check Database Performance Metrics
    print("\n\n--- Test 4: Database Performance Metrics ---")
    perf_query = """
    SELECT metric_name, value, metric_unit
    FROM v$sysmetric
    WHERE metric_name IN (
        'Database CPU Time Ratio',
        'Database Wait Time Ratio', 
        'Buffer Cache Hit Ratio',
        'Cursor Cache Hit Ratio',
        'Session Count'
    )
    AND intsize_csec = (SELECT MAX(intsize_csec) FROM v$sysmetric)
    ORDER BY metric_name
    """
    perf_df = run_oracle_query(perf_query, "Performance Metrics")
    if not perf_df.empty and 'ERROR' not in perf_df.columns:
        print(perf_df.to_string(index=False))

