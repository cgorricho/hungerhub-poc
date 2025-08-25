#!/usr/bin/env python3
"""
Oracle Connection Test Script for HungerHub POC
Tests connectivity to both Choice and AgencyExpress databases
"""

import os
import sys
import cx_Oracle
from dotenv import load_dotenv

def test_oracle_connection():
    """Test Oracle database connectivity for both databases"""
    
    # Load environment variables
    load_dotenv('config/.env')
    
    print("🔍 Oracle Connection Test - HungerHub POC")
    print("=" * 50)
    
    databases = {
        'Choice Sandbox': {
            'host': os.getenv('CHOICE_ORACLE_HOST'),
            'port': os.getenv('CHOICE_ORACLE_PORT'),
            'service': os.getenv('CHOICE_ORACLE_SERVICE_NAME'),
            'user': os.getenv('CHOICE_USERNAME'),
            'password': os.getenv('CHOICE_PASSWORD')
        },
        'Agency Sandbox': {
            'host': os.getenv('AGENCY_ORACLE_HOST'),
            'port': os.getenv('AGENCY_ORACLE_PORT'),
            'service': os.getenv('AGENCY_ORACLE_SERVICE_NAME'),
            'user': os.getenv('AGENCY_USERNAME'),
            'password': os.getenv('AGENCY_PASSWORD')
        }
    }
    
    results = {}
    
    for db_name, config in databases.items():
        print(f"\n📊 Testing {db_name} Database:")
        print("-" * 30)
        
        # Check if all required config is present
        missing_config = [k for k, v in config.items() if not v]
        if missing_config:
            print(f"❌ Missing configuration: {', '.join(missing_config)}")
            results[db_name] = False
            continue
        
        try:
            # Create DSN connection string
            dsn = cx_Oracle.makedsn(
                config['host'], 
                config['port'], 
                service_name=config['service']
            )
            
            print(f"🔗 Connecting to: {config['host']}:{config['port']}/{config['service']}")
            print(f"👤 User: {config['user']}")
            
            # Establish connection
            connection = cx_Oracle.connect(
                config['user'], 
                config['password'], 
                dsn
            )
            
            print(f"✅ Connected successfully!")
            print(f"📋 Oracle Version: {connection.version}")
            
            # Test basic query
            cursor = connection.cursor()
            cursor.execute("SELECT USER, SYSDATE FROM DUAL")
            user, sysdate = cursor.fetchone()
            
            print(f"🔍 Connected as: {user}")
            print(f"⏰ Server time: {sysdate}")
            
            # Test table access (basic check)
            try:
                cursor.execute("SELECT COUNT(*) FROM user_tables")
                table_count = cursor.fetchone()[0]
                print(f"📊 Accessible tables: {table_count}")
            except Exception as e:
                print(f"⚠️  Table query warning: {e}")
            
            cursor.close()
            connection.close()
            print(f"✅ {db_name} connection test PASSED")
            results[db_name] = True
            
        except cx_Oracle.Error as error:
            print(f"❌ Oracle connection failed: {error}")
            results[db_name] = False
        except Exception as error:
            print(f"❌ Unexpected error: {error}")
            results[db_name] = False
    
    # Summary
    print(f"\n🏁 CONNECTION TEST SUMMARY")
    print("=" * 30)
    
    success_count = sum(results.values())
    total_count = len(results)
    
    for db_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{db_name}: {status}")
    
    print(f"\nOverall: {success_count}/{total_count} databases connected successfully")
    
    if success_count == total_count:
        print("🎉 ALL DATABASE CONNECTIONS SUCCESSFUL!")
        print("Ready to proceed with data extraction.")
        return True
    else:
        print("⚠️  Some database connections failed.")
        print("Please check configuration and network connectivity.")
        return False

if __name__ == "__main__":
    success = test_oracle_connection()
    sys.exit(0 if success else 1)
