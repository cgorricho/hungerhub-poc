#!/usr/bin/env python3
"""
Oracle Table Discovery for HungerHub POC
Day 3-4 Work: Identify and analyze priority tables in Oracle databases
"""

import os
import sys
import cx_Oracle
import pandas as pd
import json
from datetime import datetime
from dotenv import load_dotenv

def discover_oracle_tables():
    """
    Discover and analyze Oracle tables according to Day 3-4 POC plan
    Priority tables: AMX_DONATION_HEADER/LINES, CHOICE_DOCUMENTHEADER/LINES, RW_ORG
    """
    
    print("🔍 HungerHub POC - Oracle Table Discovery")
    print("=" * 50)
    print("📋 Day 3-4 Task: Identify Priority Tables for Data Extraction")
    print("🎯 Target Tables: Donations, Orders, Organizations")
    print("=" * 50)
    
    # Load environment
    load_dotenv('config/.env')
    
    databases = {
        'Choice Sandbox': {
            'host': os.getenv('CHOICE_ORACLE_HOST'),
            'port': os.getenv('CHOICE_ORACLE_PORT', '1521'),
            'service': os.getenv('CHOICE_ORACLE_SERVICE_NAME'),
            'user': os.getenv('CHOICE_USERNAME'),
            'password': os.getenv('CHOICE_PASSWORD'),
            'purpose': 'Choice Program - Donations and Orders'
        },
        'Agency Sandbox': {
            'host': os.getenv('AGENCY_ORACLE_HOST'),
            'port': os.getenv('AGENCY_ORACLE_PORT', '1521'),
            'service': os.getenv('AGENCY_ORACLE_SERVICE_NAME'),
            'user': os.getenv('AGENCY_USERNAME'),
            'password': os.getenv('AGENCY_PASSWORD'),
            'purpose': 'AgencyExpress - Operations'
        }
    }
    
    # Priority table patterns from POC plan
    priority_patterns = [
        'AMX_DONATION_HEADER',
        'AMX_DONATION_LINES',
        'DONATION',
        'CHOICE_DOCUMENTHEADER',
        'CHOICE_DOCUMENTLINES',
        'DOCUMENTHEADER',
        'DOCUMENTLINES',
        'RW_ORG',
        'ORGANIZATION',
        'ORG',
        'CLIENT',
        'AGENCY',
        'ORDER',
        'PRODUCT',
        'INVENTORY'
    ]
    
    discovery_results = {
        'timestamp': datetime.now().isoformat(),
        'databases_analyzed': {},
        'priority_tables_found': {},
        'recommended_extracts': []
    }
    
    for db_name, config in databases.items():
        print(f"\n🔍 Analyzing {db_name}...")
        print("-" * 40)
        
        try:
            # Connect to database
            dsn = cx_Oracle.makedsn(config['host'], config['port'], service_name=config['service'])
            connection = cx_Oracle.connect(config['user'], config['password'], dsn)
            cursor = connection.cursor()
            
            print(f"✅ Connected to {db_name}")
            
            db_results = {
                'connection_info': f"{config['host']}:{config['port']}/{config['service']}",
                'purpose': config['purpose'],
                'total_tables': 0,
                'priority_tables': [],
                'all_tables_sample': [],
                'table_analysis': {}
            }
            
            # Get all user tables
            cursor.execute("""
                SELECT table_name, num_rows, last_analyzed 
                FROM user_tables 
                ORDER BY table_name
            """)
            
            all_tables = cursor.fetchall()
            db_results['total_tables'] = len(all_tables)
            db_results['all_tables_sample'] = [table[0] for table in all_tables[:20]]
            
            print(f"📊 Total tables found: {len(all_tables)}")
            
            # Find priority tables
            found_priority_tables = []
            for table_name, num_rows, last_analyzed in all_tables:
                for pattern in priority_patterns:
                    if pattern.upper() in table_name.upper():
                        found_priority_tables.append({
                            'table_name': table_name,
                            'pattern_matched': pattern,
                            'estimated_rows': num_rows if num_rows else 'Unknown',
                            'last_analyzed': str(last_analyzed) if last_analyzed else 'Never'
                        })
                        
            db_results['priority_tables'] = found_priority_tables
            print(f"🎯 Priority tables found: {len(found_priority_tables)}")
            
            # Analyze each priority table
            for table_info in found_priority_tables:
                table_name = table_info['table_name']
                print(f"   📋 Analyzing {table_name}...")
                
                try:
                    # Get table structure
                    cursor.execute(f"""
                        SELECT column_name, data_type, nullable, data_default
                        FROM user_tab_columns 
                        WHERE table_name = '{table_name}'
                        ORDER BY column_id
                    """)
                    
                    columns = cursor.fetchall()
                    column_info = []
                    for col_name, data_type, nullable, data_default in columns:
                        column_info.append({
                            'name': col_name,
                            'type': data_type,
                            'nullable': nullable == 'Y',
                            'default': str(data_default) if data_default else None
                        })
                    
                    # Get sample data (first 3 rows)
                    try:
                        cursor.execute(f"SELECT * FROM {table_name} WHERE rownum <= 3")
                        sample_rows = cursor.fetchall()
                        
                        # Convert to readable format
                        if sample_rows and columns:
                            col_names = [col[0] for col in columns]
                            sample_data = []
                            for row in sample_rows:
                                row_dict = {}
                                for i, value in enumerate(row):
                                    if i < len(col_names):
                                        # Convert to string for JSON serialization
                                        row_dict[col_names[i]] = str(value) if value is not None else None
                                sample_data.append(row_dict)
                        else:
                            sample_data = []
                            
                    except Exception as e:
                        sample_data = [f"Error getting sample: {str(e)}"]
                    
                    # Get actual row count
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        actual_count = cursor.fetchone()[0]
                    except:
                        actual_count = 'Error counting rows'
                    
                    table_analysis = {
                        'columns': column_info,
                        'column_count': len(columns),
                        'actual_row_count': actual_count,
                        'sample_data': sample_data[:3],  # Limit to 3 rows for readability
                        'data_types': list(set([col['type'] for col in column_info])),
                        'nullable_columns': len([col for col in column_info if col['nullable']])
                    }
                    
                    db_results['table_analysis'][table_name] = table_analysis
                    
                    print(f"      📊 {len(columns)} columns, {actual_count} rows")
                    
                except Exception as e:
                    print(f"      ❌ Error analyzing {table_name}: {e}")
                    db_results['table_analysis'][table_name] = {'error': str(e)}
            
            cursor.close()
            connection.close()
            
            discovery_results['databases_analyzed'][db_name] = db_results
            
            # Add to global priority tables found
            for table_info in found_priority_tables:
                table_key = f"{db_name}.{table_info['table_name']}"
                discovery_results['priority_tables_found'][table_key] = {
                    'database': db_name,
                    'table_name': table_info['table_name'],
                    'pattern': table_info['pattern_matched'],
                    'rows': table_info['estimated_rows'],
                    'purpose': config['purpose']
                }
            
        except Exception as e:
            print(f"❌ Error connecting to {db_name}: {e}")
            discovery_results['databases_analyzed'][db_name] = {'error': str(e)}
    
    # Generate recommendations for data extraction
    print(f"\n" + "=" * 50)
    print("📋 EXTRACTION RECOMMENDATIONS")
    print("=" * 50)
    
    total_priority_tables = len(discovery_results['priority_tables_found'])
    print(f"🎯 Total Priority Tables Found: {total_priority_tables}")
    
    if total_priority_tables > 0:
        print("\n📊 RECOMMENDED EXTRACTION PLAN:")
        
        # Group by type
        donation_tables = []
        order_tables = []
        org_tables = []
        other_tables = []
        
        for table_key, table_info in discovery_results['priority_tables_found'].items():
            if 'DONATION' in table_info['pattern'].upper():
                donation_tables.append(table_info)
            elif any(x in table_info['pattern'].upper() for x in ['DOCUMENT', 'ORDER']):
                order_tables.append(table_info)
            elif any(x in table_info['pattern'].upper() for x in ['ORG', 'AGENCY', 'CLIENT']):
                org_tables.append(table_info)
            else:
                other_tables.append(table_info)
        
        if donation_tables:
            print(f"\n💰 DONATION TABLES ({len(donation_tables)}):")
            for table in donation_tables:
                print(f"   - {table['database']}.{table['table_name']} ({table['rows']} rows)")
                discovery_results['recommended_extracts'].append({
                    'priority': 1,
                    'category': 'donations',
                    'database': table['database'],
                    'table_name': table['table_name'],
                    'purpose': 'Core donation data for analytics'
                })
        
        if order_tables:
            print(f"\n📋 ORDER/DOCUMENT TABLES ({len(order_tables)}):")
            for table in order_tables:
                print(f"   - {table['database']}.{table['table_name']} ({table['rows']} rows)")
                discovery_results['recommended_extracts'].append({
                    'priority': 2,
                    'category': 'orders',
                    'database': table['database'],
                    'table_name': table['table_name'],
                    'purpose': 'Order and fulfillment tracking'
                })
        
        if org_tables:
            print(f"\n🏢 ORGANIZATION TABLES ({len(org_tables)}):")
            for table in org_tables:
                print(f"   - {table['database']}.{table['table_name']} ({table['rows']} rows)")
                discovery_results['recommended_extracts'].append({
                    'priority': 1,
                    'category': 'organizations',
                    'database': table['database'],
                    'table_name': table['table_name'],
                    'purpose': 'Organization and client master data'
                })
        
        if other_tables:
            print(f"\n📊 OTHER RELEVANT TABLES ({len(other_tables)}):")
            for table in other_tables:
                print(f"   - {table['database']}.{table['table_name']} ({table['rows']} rows)")
                discovery_results['recommended_extracts'].append({
                    'priority': 3,
                    'category': 'other',
                    'database': table['database'],
                    'table_name': table['table_name'],
                    'purpose': 'Additional supporting data'
                })
    
    else:
        print("⚠️ No priority tables found matching expected patterns")
        print("📋 Showing sample of available tables for manual review:")
        for db_name, db_info in discovery_results['databases_analyzed'].items():
            if 'all_tables_sample' in db_info:
                print(f"\n{db_name} - Sample tables:")
                for table in db_info['all_tables_sample'][:10]:
                    print(f"   - {table}")
    
    # Save detailed results
    os.makedirs('data/analysis', exist_ok=True)
    results_file = 'data/analysis/oracle_table_discovery.json'
    
    with open(results_file, 'w') as f:
        json.dump(discovery_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved: {results_file}")
    
    # Next steps
    print(f"\n" + "=" * 50)
    print("🚀 NEXT STEPS (Day 3-4 Continued)")
    print("=" * 50)
    print("1. Review detailed table analysis in saved JSON file")
    print("2. Create extraction scripts for high-priority tables")
    print("3. Extract sample data for validation")
    print("4. Build fact/dimension tables with real data")
    print("5. Update dashboard to use real Oracle data")
    
    return discovery_results

if __name__ == "__main__":
    try:
        results = discover_oracle_tables()
        
        priority_count = len(results['priority_tables_found'])
        if priority_count > 0:
            print(f"\n✅ SUCCESS: Found {priority_count} priority tables for extraction")
            sys.exit(0)
        else:
            print(f"\n⚠️ WARNING: No priority tables found - manual review needed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ DISCOVERY FAILED: {e}")
        sys.exit(2)
