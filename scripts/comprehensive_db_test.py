#!/usr/bin/env python3
"""
Comprehensive Database Connectivity Test
Tests multiple authentication methods and configurations for Azure SQL
"""

import pyodbc
import os
import socket
import time
from datetime import datetime
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseConnectivityTest:
    """Comprehensive database connectivity testing"""
    
    def __init__(self):
        self.test_results = {}
        self.successful_connections = []
        
    def test_network_connectivity(self, server, port=1433):
        """Test basic network connectivity to SQL server"""
        logger.info(f"🌐 Testing network connectivity to {server}:{port}...")
        
        try:
            socket.setdefaulttimeout(10)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((server, port))
            sock.close()
            
            if result == 0:
                logger.info(f"   ✅ Network connectivity OK to {server}:{port}")
                return True
            else:
                logger.error(f"   ❌ Network connectivity FAILED to {server}:{port}")
                return False
        except Exception as e:
            logger.error(f"   ❌ Network test error: {e}")
            return False
    
    def verify_environment_variables(self):
        """Check for all possible environment variables"""
        logger.info("🔍 Verifying environment variables...")
        
        env_vars = {
            # Database servers
            'CHOICE_DB_SERVER': os.getenv('CHOICE_DB_SERVER'),
            'AGENCY_DB_SERVER': os.getenv('AGENCY_DB_SERVER'),
            
            # Database names
            'CHOICE_DB_NAME': os.getenv('CHOICE_DB_NAME'),
            'AGENCY_DB_NAME': os.getenv('AGENCY_DB_NAME'),
            
            # Authentication
            'DB_AUTH_METHOD': os.getenv('DB_AUTH_METHOD'),
            'DB_USERNAME': os.getenv('DB_USERNAME'),
            'DB_PASSWORD': os.getenv('DB_PASSWORD'),
            
            # Alternative naming conventions
            'AZURE_SQL_SERVER': os.getenv('AZURE_SQL_SERVER'),
            'AZURE_SQL_DATABASE': os.getenv('AZURE_SQL_DATABASE'),
            'AZURE_SQL_USERNAME': os.getenv('AZURE_SQL_USERNAME'),
            'AZURE_SQL_PASSWORD': os.getenv('AZURE_SQL_PASSWORD'),
        }
        
        logger.info("   Environment variables found:")
        for key, value in env_vars.items():
            if value:
                if 'PASSWORD' in key.upper():
                    logger.info(f"     ✅ {key}: ****** (hidden)")
                else:
                    logger.info(f"     ✅ {key}: {value}")
            else:
                logger.info(f"     ❌ {key}: Not set")
        
        return env_vars
    
    def test_multiple_auth_methods(self, server, database):
        """Test different authentication methods"""
        logger.info(f"🔐 Testing authentication methods for {server}/{database}...")
        
        auth_methods = [
            {
                'name': 'ActiveDirectoryDefault',
                'conn_str': f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Authentication=ActiveDirectoryDefault;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
            },
            {
                'name': 'ActiveDirectoryIntegrated', 
                'conn_str': f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
            },
            {
                'name': 'ActiveDirectoryManagedIdentity',
                'conn_str': f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Authentication=ActiveDirectoryMsi;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
            }
        ]
        
        # Add SQL Server authentication if credentials available
        username = os.getenv('DB_USERNAME') or os.getenv('AZURE_SQL_USERNAME')
        password = os.getenv('DB_PASSWORD') or os.getenv('AZURE_SQL_PASSWORD')
        
        if username and password:
            auth_methods.append({
                'name': 'SqlServerAuthentication',
                'conn_str': f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
            })
        
        results = {}
        
        for method in auth_methods:
            logger.info(f"   🔑 Testing {method['name']}...")
            
            try:
                conn = pyodbc.connect(method['conn_str'])
                cursor = conn.cursor()
                
                # Test basic query
                cursor.execute("SELECT 1 as test_value")
                result = cursor.fetchone()
                
                if result and result[0] == 1:
                    logger.info(f"     ✅ {method['name']} - SUCCESS!")
                    results[method['name']] = {
                        'status': 'SUCCESS',
                        'connection_string': method['conn_str'],
                        'test_time': datetime.now().isoformat()
                    }
                    self.successful_connections.append(method)
                else:
                    logger.error(f"     ❌ {method['name']} - Query failed")
                    results[method['name']] = {'status': 'QUERY_FAILED'}
                
                conn.close()
                
            except Exception as e:
                logger.error(f"     ❌ {method['name']} - FAILED: {str(e)}")
                results[method['name']] = {
                    'status': 'FAILED',
                    'error': str(e)
                }
        
        return results
    
    def test_table_access(self, connection_info):
        """Test access to key tables"""
        logger.info("📋 Testing table access...")
        
        try:
            conn = pyodbc.connect(connection_info['connection_string'])
            cursor = conn.cursor()
            
            # Test table listing
            tables_query = """
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
            """
            
            cursor.execute(tables_query)
            tables = cursor.fetchall()
            
            logger.info(f"   ✅ Found {len(tables)} tables")
            
            # Test sample from first table if any exist
            if tables:
                first_table = tables[0]
                schema = first_table[0]
                table_name = first_table[1]
                
                sample_query = f"SELECT TOP 1 * FROM [{schema}].[{table_name}]"
                cursor.execute(sample_query)
                sample = cursor.fetchone()
                
                if sample:
                    logger.info(f"   ✅ Successfully sampled from {schema}.{table_name}")
                else:
                    logger.warning(f"   ⚠️ Table {schema}.{table_name} appears empty")
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Table access failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all connectivity tests"""
        logger.info("🚀 Starting comprehensive database connectivity test...")
        
        # Step 1: Verify environment
        env_vars = self.verify_environment_variables()
        
        # Get server configurations
        choice_server = env_vars.get('CHOICE_DB_SERVER') or 'choice-sql-server.database.windows.net'
        choice_db = env_vars.get('CHOICE_DB_NAME') or 'Choice'
        agency_server = env_vars.get('AGENCY_DB_SERVER') or 'agencyexpress-sql-server.database.windows.net' 
        agency_db = env_vars.get('AGENCY_DB_NAME') or 'AgencyExpress'
        
        # Step 2: Test network connectivity
        choice_network = self.test_network_connectivity(choice_server)
        agency_network = self.test_network_connectivity(agency_server)
        
        self.test_results['network_tests'] = {
            'choice_server': choice_network,
            'agency_server': agency_network
        }
        
        # Step 3: Test authentication methods
        if choice_network:
            logger.info(f"\n🔍 TESTING CHOICE DATABASE ({choice_server}/{choice_db})")
            choice_auth_results = self.test_multiple_auth_methods(choice_server, choice_db)
            self.test_results['choice_auth'] = choice_auth_results
            
            # Test table access if we have successful connection
            choice_success = [method for method in self.successful_connections if 'choice' in method.get('conn_str', '').lower()]
            if choice_success:
                self.test_table_access(choice_success[0])
        
        if agency_network:
            logger.info(f"\n🔍 TESTING AGENCYEXPRESS DATABASE ({agency_server}/{agency_db})")
            agency_auth_results = self.test_multiple_auth_methods(agency_server, agency_db)
            self.test_results['agency_auth'] = agency_auth_results
            
            # Test table access if we have successful connection
            agency_success = [method for method in self.successful_connections if 'agency' in method.get('conn_str', '').lower()]
            if agency_success:
                self.test_table_access(agency_success[0])
        
        # Step 4: Generate summary report
        self.generate_test_report()
        
        return self.test_results
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "="*60)
        logger.info("📊 COMPREHENSIVE DATABASE TEST RESULTS")
        logger.info("="*60)
        
        # Network connectivity summary
        logger.info("\n🌐 NETWORK CONNECTIVITY:")
        for db, status in self.test_results.get('network_tests', {}).items():
            status_icon = "✅" if status else "❌"
            logger.info(f"   {status_icon} {db}: {'PASS' if status else 'FAIL'}")
        
        # Authentication summary
        logger.info("\n🔐 AUTHENTICATION RESULTS:")
        
        total_methods = 0
        successful_methods = 0
        
        for db_name in ['choice_auth', 'agency_auth']:
            if db_name in self.test_results:
                logger.info(f"\n   {db_name.upper().replace('_AUTH', '')} DATABASE:")
                for method, result in self.test_results[db_name].items():
                    total_methods += 1
                    status = result.get('status', 'UNKNOWN')
                    if status == 'SUCCESS':
                        successful_methods += 1
                        logger.info(f"     ✅ {method}: SUCCESS")
                    else:
                        logger.info(f"     ❌ {method}: {status}")
        
        # Overall status
        logger.info(f"\n🎯 OVERALL STATUS:")
        logger.info(f"   • Successful connections: {successful_methods}/{total_methods}")
        logger.info(f"   • Working methods: {len(self.successful_connections)}")
        
        if self.successful_connections:
            logger.info(f"   • Status: ✅ DATABASE CONNECTIVITY ESTABLISHED")
            logger.info(f"   • Recommended method: {self.successful_connections[0]['name']}")
        else:
            logger.info(f"   • Status: ❌ NO WORKING CONNECTIONS FOUND")
        
        logger.info("="*60)
        
        # Save detailed results to file
        os.makedirs('logs', exist_ok=True)
        with open('logs/database_connectivity_test.json', 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        logger.info("📄 Detailed results saved to: logs/database_connectivity_test.json")

if __name__ == "__main__":
    # Load environment variables from .env if it exists
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Run comprehensive test
    tester = DatabaseConnectivityTest()
    results = tester.run_comprehensive_test()
