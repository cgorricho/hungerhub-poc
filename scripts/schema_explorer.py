#!/usr/bin/env python3
"""
HungerHub POC - Database Schema Explorer
Analyzes table structures and extracts samples from Choice and AgencyExpress databases
"""

import pyodbc
import pandas as pd
import json
from datetime import datetime
import logging
import os
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/schema_exploration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseExplorer:
    def __init__(self):
        self.choice_conn = None
        self.agency_conn = None
        self.schema_info = {}
        
    def connect_databases(self):
        """Establish connections to both databases"""
        try:
            # Choice Database Connection
            choice_conn_str = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=choice-sql-server.database.windows.net;"
                "DATABASE=Choice;"
                "Authentication=ActiveDirectoryManagedIdentity;"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
                "Connection Timeout=30;"
            )
            self.choice_conn = pyodbc.connect(choice_conn_str)
            logger.info("✅ Connected to Choice database")
            
            # AgencyExpress Database Connection  
            agency_conn_str = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=agencyexpress-sql-server.database.windows.net;"
                "DATABASE=AgencyExpress;"
                "Authentication=ActiveDirectoryManagedIdentity;"
                "Encrypt=yes;"
                "TrustServerCertificate=no;"
                "Connection Timeout=30;"
            )
            self.agency_conn = pyodbc.connect(agency_conn_str)
            logger.info("✅ Connected to AgencyExpress database")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
            
    def get_table_list(self, connection, db_name):
        """Get list of all tables in the database"""
        query = """
        SELECT 
            TABLE_SCHEMA,
            TABLE_NAME,
            TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        
        df = pd.read_sql(query, connection)
        logger.info(f"📊 Found {len(df)} tables in {db_name} database")
        return df
    
    def get_table_schema(self, connection, schema, table):
        """Get detailed schema information for a specific table"""
        query = f"""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            ORDINAL_POSITION
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}'
        ORDER BY ORDINAL_POSITION
        """
        
        return pd.read_sql(query, connection)
    
    def get_sample_data(self, connection, schema, table, limit=10):
        """Extract sample data from a table"""
        try:
            query = f"SELECT TOP {limit} * FROM [{schema}].[{table}]"
            return pd.read_sql(query, connection)
        except Exception as e:
            logger.warning(f"⚠️ Could not sample from {schema}.{table}: {e}")
            return None
    
    def analyze_database(self, connection, db_name):
        """Comprehensive analysis of a database"""
        logger.info(f"🔍 Analyzing {db_name} database...")
        
        # Get all tables
        tables_df = self.get_table_list(connection, db_name)
        
        database_info = {
            'database_name': db_name,
            'total_tables': len(tables_df),
            'analysis_timestamp': datetime.now().isoformat(),
            'tables': {}
        }
        
        # Analyze each table
        for _, row in tables_df.iterrows():
            schema = row['TABLE_SCHEMA']
            table = row['TABLE_NAME']
            table_key = f"{schema}.{table}"
            
            logger.info(f"  📋 Analyzing table: {table_key}")
            
            # Get schema info
            schema_df = self.get_table_schema(connection, schema, table)
            
            # Get sample data
            sample_df = self.get_sample_data(connection, schema, table)
            
            # Get row count
            try:
                count_query = f"SELECT COUNT(*) as row_count FROM [{schema}].[{table}]"
                row_count = pd.read_sql(count_query, connection).iloc[0]['row_count']
            except:
                row_count = 'Unknown'
            
            database_info['tables'][table_key] = {
                'schema': schema,
                'table_name': table,
                'row_count': row_count,
                'column_count': len(schema_df),
                'columns': schema_df.to_dict('records'),
                'sample_available': sample_df is not None,
                'sample_rows': len(sample_df) if sample_df is not None else 0
            }
            
            # Save sample data if available
            if sample_df is not None:
                sample_file = f"data/samples/{db_name}_{schema}_{table}_sample.csv"
                os.makedirs(os.path.dirname(sample_file), exist_ok=True)
                sample_df.to_csv(sample_file, index=False)
                logger.info(f"    💾 Saved sample to: {sample_file}")
        
        return database_info
    
    def identify_priority_tables(self, database_info):
        """Identify tables that are likely important for hunger/food analysis"""
        priority_keywords = [
            'client', 'customer', 'member', 'participant', 'recipient',
            'food', 'meal', 'nutrition', 'pantry', 'inventory', 'distribution',
            'service', 'program', 'assistance', 'benefit', 'aid',
            'location', 'site', 'agency', 'organization',
            'transaction', 'visit', 'appointment', 'delivery'
        ]
        
        priority_tables = []
        
        for table_key, table_info in database_info['tables'].items():
            table_name_lower = table_info['table_name'].lower()
            
            # Check if table name contains priority keywords
            for keyword in priority_keywords:
                if keyword in table_name_lower:
                    priority_tables.append({
                        'table_key': table_key,
                        'table_info': table_info,
                        'keyword_match': keyword,
                        'priority_score': len([k for k in priority_keywords if k in table_name_lower])
                    })
                    break
        
        # Sort by priority score (descending)
        priority_tables.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priority_tables
    
    def run_exploration(self):
        """Main exploration workflow"""
        logger.info("🚀 Starting database exploration...")
        
        # Create output directories
        os.makedirs('data/samples', exist_ok=True)
        os.makedirs('data/schemas', exist_ok=True)
        
        # Connect to databases
        self.connect_databases()
        
        # Analyze Choice database
        choice_info = self.analyze_database(self.choice_conn, 'Choice')
        
        # Analyze AgencyExpress database  
        agency_info = self.analyze_database(self.agency_conn, 'AgencyExpress')
        
        # Identify priority tables
        choice_priorities = self.identify_priority_tables(choice_info)
        agency_priorities = self.identify_priority_tables(agency_info)
        
        # Save comprehensive schema information
        schema_report = {
            'exploration_timestamp': datetime.now().isoformat(),
            'databases': {
                'choice': choice_info,
                'agency_express': agency_info
            },
            'priority_tables': {
                'choice': choice_priorities,
                'agency_express': agency_priorities
            },
            'summary': {
                'total_choice_tables': choice_info['total_tables'],
                'total_agency_tables': agency_info['total_tables'],
                'priority_choice_tables': len(choice_priorities),
                'priority_agency_tables': len(agency_priorities)
            }
        }
        
        # Save to JSON
        with open('data/schemas/database_exploration_report.json', 'w') as f:
            json.dump(schema_report, f, indent=2, default=str)
        
        logger.info("✅ Schema exploration complete!")
        
        # Print summary
        self.print_summary(schema_report)
        
        return schema_report
    
    def print_summary(self, report):
        """Print exploration summary"""
        print("\n" + "="*60)
        print("📊 DATABASE EXPLORATION SUMMARY")
        print("="*60)
        
        print(f"\n🎯 CHOICE DATABASE:")
        print(f"   • Total Tables: {report['summary']['total_choice_tables']}")
        print(f"   • Priority Tables: {report['summary']['priority_choice_tables']}")
        
        print(f"\n🎯 AGENCYEXPRESS DATABASE:")
        print(f"   • Total Tables: {report['summary']['total_agency_tables']}")
        print(f"   • Priority Tables: {report['summary']['priority_agency_tables']}")
        
        print(f"\n🔥 TOP PRIORITY TABLES:")
        
        print(f"\n  Choice Database:")
        for i, table in enumerate(report['priority_tables']['choice'][:5]):
            print(f"    {i+1}. {table['table_key']} (Score: {table['priority_score']})")
        
        print(f"\n  AgencyExpress Database:")
        for i, table in enumerate(report['priority_tables']['agency_express'][:5]):
            print(f"    {i+1}. {table['table_key']} (Score: {table['priority_score']})")
        
        print(f"\n💾 Output Files:")
        print(f"   • Schema Report: data/schemas/database_exploration_report.json")
        print(f"   • Sample Data: data/samples/")
        print(f"   • Logs: logs/schema_exploration.log")
        
        print("\n" + "="*60)

    def close_connections(self):
        """Close database connections"""
        if self.choice_conn:
            self.choice_conn.close()
        if self.agency_conn:
            self.agency_conn.close()
        logger.info("🔌 Database connections closed")

if __name__ == "__main__":
    explorer = DatabaseExplorer()
    
    try:
        report = explorer.run_exploration()
        print("\n🎉 Exploration completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Exploration failed: {e}")
        raise
        
    finally:
        explorer.close_connections()
