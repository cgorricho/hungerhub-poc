#!/usr/bin/env python3
"""
Database Connectivity Report for HungerHub POC
Addresses Gemini review concerns - focuses on Oracle databases only
"""

import os
import sys
import json
import cx_Oracle
from datetime import datetime
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def generate_connectivity_report():
    """
    Generate comprehensive connectivity report for Gemini CLI review
    Focuses on Oracle databases only (project requirement)
    """
    
    print("🍽️ HungerHub POC - Database Connectivity Report")
    print("=" * 55)
    print("📋 This report addresses Gemini CLI review concerns")
    print("🎯 Project Requirement: Oracle databases only")
    print("=" * 55)
    
    # Load environment variables
    load_dotenv('config/.env')
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'project_requirement': 'Oracle databases only',
        'databases_tested': {},
        'overall_status': 'UNKNOWN',
        'recommendations': []
    }
    
    # Oracle databases configuration
    databases = {
        'Choice Sandbox': {
            'host': os.getenv('CHOICE_ORACLE_HOST'),
            'port': os.getenv('CHOICE_ORACLE_PORT', '1521'),
            'service': os.getenv('CHOICE_ORACLE_SERVICE_NAME'),
            'user': os.getenv('CHOICE_USERNAME'),
            'password': os.getenv('CHOICE_PASSWORD'),
            'purpose': 'Donations, Choice Program data'
        },
        'Agency Sandbox': {
            'host': os.getenv('AGENCY_ORACLE_HOST'),
            'port': os.getenv('AGENCY_ORACLE_PORT', '1521'),
            'service': os.getenv('AGENCY_ORACLE_SERVICE_NAME'),
            'user': os.getenv('AGENCY_USERNAME'),
            'password': os.getenv('AGENCY_PASSWORD'),
            'purpose': 'AgencyExpress operational data'
        }
    }
    
    successful_connections = 0
    total_databases = len(databases)
    
    for db_name, config in databases.items():
        print(f"\n🔍 Testing {db_name}...")
        print("-" * 40)
        
        db_result = {
            'connection_string': f"{config['host']}:{config['port']}/{config['service']}",
            'username': config['user'],
            'purpose': config['purpose'],
            'status': 'UNKNOWN',
            'details': {},
            'issues': []
        }
        
        # Check configuration completeness
        missing_config = [k for k, v in config.items() if not v and k != 'purpose']
        if missing_config:
            db_result['status'] = 'CONFIG_MISSING'
            db_result['issues'].append(f"Missing: {', '.join(missing_config)}")
            print(f"   ❌ Missing configuration: {', '.join(missing_config)}")
            report['databases_tested'][db_name] = db_result
            continue
        
        try:
            # Create connection string
            dsn = cx_Oracle.makedsn(
                config['host'], 
                config['port'], 
                service_name=config['service']
            )
            
            print(f"   📡 Connecting to: {config['host']}:{config['port']}/{config['service']}")
            print(f"   👤 User: {config['user']}")
            
            # Establish connection
            connection = cx_Oracle.connect(
                config['user'], 
                config['password'], 
                dsn
            )
            
            # Get database information
            cursor = connection.cursor()
            
            # Basic connectivity test
            cursor.execute("SELECT USER, SYSDATE FROM DUAL")
            connected_user, server_time = cursor.fetchone()
            
            # Get Oracle version
            cursor.execute("SELECT * FROM v$version WHERE banner LIKE 'Oracle%'")
            oracle_version = cursor.fetchone()[0]
            
            # Count accessible tables
            cursor.execute("SELECT COUNT(*) FROM user_tables")
            table_count = cursor.fetchone()[0]
            
            # Sample table names
            cursor.execute("SELECT table_name FROM user_tables WHERE rownum <= 5 ORDER BY table_name")
            sample_tables = [row[0] for row in cursor.fetchall()]
            
            # Check for specific expected tables (if any)
            cursor.execute("SELECT COUNT(*) FROM user_tables WHERE table_name LIKE '%DONATION%' OR table_name LIKE '%CLIENT%' OR table_name LIKE '%ORDER%'")
            relevant_tables = cursor.fetchone()[0]
            
            db_result['status'] = 'SUCCESS'
            db_result['details'] = {
                'oracle_version': oracle_version,
                'connected_user': connected_user,
                'server_time': str(server_time),
                'total_tables': table_count,
                'sample_tables': sample_tables,
                'potentially_relevant_tables': relevant_tables
            }
            
            cursor.close()
            connection.close()
            
            successful_connections += 1
            print(f"   ✅ Connection successful!")
            print(f"   📊 Tables available: {table_count}")
            print(f"   🎯 Potentially relevant tables: {relevant_tables}")
            print(f"   ⏰ Server time: {server_time}")
            
        except cx_Oracle.Error as e:
            db_result['status'] = 'CONNECTION_FAILED'
            db_result['issues'].append(f"Oracle error: {str(e)}")
            print(f"   ❌ Connection failed: {e}")
            
        except Exception as e:
            db_result['status'] = 'UNKNOWN_ERROR'
            db_result['issues'].append(f"Unexpected error: {str(e)}")
            print(f"   ❌ Unexpected error: {e}")
        
        report['databases_tested'][db_name] = db_result
    
    # Determine overall status
    if successful_connections == total_databases:
        report['overall_status'] = 'ALL_CONNECTED'
        report['recommendations'].append("✅ All required Oracle databases are accessible")
        report['recommendations'].append("🚀 Ready to proceed with data extraction and ETL development")
    elif successful_connections > 0:
        report['overall_status'] = 'PARTIAL_SUCCESS'
        report['recommendations'].append(f"⚠️ {successful_connections}/{total_databases} databases connected")
        report['recommendations'].append("🔧 Review failed connections and resolve configuration issues")
    else:
        report['overall_status'] = 'NO_CONNECTIONS'
        report['recommendations'].append("❌ No database connections successful")
        report['recommendations'].append("🆘 Critical: Verify Oracle configuration and network connectivity")
    
    # Additional project-specific recommendations
    if successful_connections > 0:
        report['recommendations'].append("📋 Next steps: Develop table schema analysis scripts")
        report['recommendations'].append("🔍 Identify key tables for donations, clients, and orders data")
        report['recommendations'].append("⚡ Create ETL pipeline focusing on Oracle-only data sources")
    
    # Note about Azure SQL (addressing Gemini's concern)
    report['azure_sql_note'] = "Azure SQL is NOT required for this project. Original spec calls for Oracle databases only."
    
    # Print summary
    print("\n" + "=" * 55)
    print("📊 CONNECTIVITY REPORT SUMMARY")
    print("=" * 55)
    print(f"🎯 Project Database Requirement: Oracle only")
    print(f"📈 Connection Success Rate: {successful_connections}/{total_databases}")
    print(f"🏁 Overall Status: {report['overall_status']}")
    
    for rec in report['recommendations']:
        print(f"   {rec}")
    
    print(f"\n💡 Note: {report['azure_sql_note']}")
    
    # Save report
    os.makedirs('logs', exist_ok=True)
    report_file = 'logs/database_connectivity_report.json'
    
    # Create clean report for saving (remove passwords)
    clean_report = report.copy()
    for db_name, db_data in clean_report['databases_tested'].items():
        if 'password' in str(db_data):
            # This shouldn't happen, but just in case
            db_data = {k: v for k, v in db_data.items() if 'password' not in k.lower()}
    
    with open(report_file, 'w') as f:
        json.dump(clean_report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved: {report_file}")
    print("🔍 This report can be shared with Gemini CLI for review")
    
    return report

if __name__ == "__main__":
    try:
        report = generate_connectivity_report()
        
        if report['overall_status'] == 'ALL_CONNECTED':
            print("\n🎉 SUCCESS: All Oracle databases connected - ready for development!")
            sys.exit(0)
        elif report['overall_status'] == 'PARTIAL_SUCCESS':
            print("\n⚠️ PARTIAL: Some connections working - review and fix remaining issues")
            sys.exit(1)
        else:
            print("\n❌ FAILED: No database connections - critical configuration needed")
            sys.exit(2)
            
    except Exception as e:
        print(f"\n💥 REPORT GENERATION FAILED: {e}")
        sys.exit(3)
