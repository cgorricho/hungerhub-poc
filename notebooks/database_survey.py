"""
Comprehensive Oracle Database Survey Script
Based on our performance testing, survey all tables for optimal extraction strategy
"""

import os
import pandas as pd
import cx_Oracle
from dotenv import load_dotenv
import time
import json
from pathlib import Path

# Load environment
load_dotenv('../config/.env')

class DatabaseSurveyor:
    def __init__(self):
        self.host = os.getenv('CHOICE_ORACLE_HOST')
        self.port = os.getenv('CHOICE_ORACLE_PORT', '1521')
        self.service = os.getenv('CHOICE_ORACLE_SERVICE_NAME')
        self.user = os.getenv('CHOICE_USERNAME')
        self.password = os.getenv('CHOICE_PASSWORD')
        
        # Output directory
        self.output_dir = Path('notebook_output/database_survey')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self):
        """Get Oracle connection"""
        dsn = cx_Oracle.makedsn(self.host, self.port, service_name=self.service)
        return cx_Oracle.connect(self.user, self.password, dsn, encoding='UTF-8')
    
    def survey_database(self):
        """Complete database survey with table sizes, columns, and data types"""
        print("🔍 === Oracle Database Survey ===")
        
        connection = self.get_connection()
        cursor = connection.cursor()
        
        # Get all accessible tables
        print("\n📊 Discovering accessible tables...")
        cursor.execute("""
            SELECT table_name, owner
            FROM all_tables 
            WHERE owner IN ('CHOICE', 'AGENCY', USER) 
            AND table_name NOT LIKE 'BIN$%'
            ORDER BY owner, table_name
        """)
        
        all_tables = cursor.fetchall()
        print(f"📋 Found {len(all_tables)} accessible tables")
        
        survey_results = []
        total_rows = 0
        total_size_mb = 0
        
        for i, (table_name, owner) in enumerate(all_tables, 1):
            print(f"\n🔍 [{i}/{len(all_tables)}] Analyzing {owner}.{table_name}...")
            
            try:
                start_time = time.time()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {owner}.{table_name}")
                row_count = cursor.fetchone()[0]
                
                # Get table size (approximate)
                cursor.execute("""
                    SELECT 
                        ROUND(SUM(bytes)/1024/1024, 2) as size_mb,
                        COUNT(*) as segment_count
                    FROM user_segments 
                    WHERE segment_name = :table_name
                """, {'table_name': table_name})
                
                size_result = cursor.fetchone()
                size_mb = size_result[0] if size_result and size_result[0] else 0
                
                # Get column information
                cursor.execute("""
                    SELECT 
                        column_name, 
                        data_type, 
                        data_length, 
                        nullable
                    FROM all_tab_columns 
                    WHERE table_name = :table_name 
                    AND owner = :owner
                    ORDER BY column_id
                """, {'table_name': table_name, 'owner': owner})
                
                columns = cursor.fetchall()
                column_count = len(columns)
                
                # Estimate extraction time based on our performance results
                # Base rate: ~950 rows/sec for full extraction
                estimated_seconds = max(1, row_count / 950) if row_count > 0 else 0
                estimated_minutes = estimated_seconds / 60
                
                # Sample a few rows to get actual data characteristics (if table has data)
                sample_data = None
                if row_count > 0:
                    try:
                        cursor.execute(f"""
                            SELECT * FROM (
                                SELECT * FROM {owner}.{table_name} 
                                WHERE ROWNUM <= 3
                            ) ORDER BY ROWID
                        """)
                        sample_rows = cursor.fetchall()
                        sample_data = [list(row) for row in sample_rows]
                    except:
                        sample_data = None
                
                duration = time.time() - start_time
                
                table_info = {
                    'owner': owner,
                    'table_name': table_name,
                    'full_name': f"{owner}.{table_name}",
                    'row_count': row_count,
                    'column_count': column_count,
                    'size_mb': size_mb,
                    'estimated_extraction_seconds': round(estimated_seconds, 1),
                    'estimated_extraction_minutes': round(estimated_minutes, 2),
                    'analysis_duration': round(duration, 2),
                    'columns': [
                        {
                            'name': col[0],
                            'type': col[1], 
                            'length': col[2],
                            'nullable': col[3]
                        } for col in columns
                    ],
                    'sample_data': sample_data[:3] if sample_data else None,
                    'priority': self.calculate_priority(table_name, row_count)
                }
                
                survey_results.append(table_info)
                total_rows += row_count
                total_size_mb += size_mb
                
                # Progress update
                if row_count > 0:
                    print(f"   ✅ {row_count:,} rows, {column_count} cols, ~{size_mb:.1f}MB, ~{estimated_minutes:.1f}min est.")
                else:
                    print(f"   📭 Empty table ({column_count} columns defined)")
                    
            except Exception as e:
                print(f"   ❌ Error analyzing {owner}.{table_name}: {str(e)[:50]}...")
                survey_results.append({
                    'owner': owner,
                    'table_name': table_name,
                    'full_name': f"{owner}.{table_name}",
                    'error': str(e),
                    'row_count': 0,
                    'priority': 'error'
                })
        
        cursor.close()
        connection.close()
        
        # Sort results by priority and row count
        survey_results.sort(key=lambda x: (
            0 if x.get('priority') == 'high' else 1 if x.get('priority') == 'medium' else 2,
            -x.get('row_count', 0)
        ))
        
        # Save detailed results
        results_file = self.output_dir / 'database_survey_detailed.json'
        with open(results_file, 'w') as f:
            json.dump(survey_results, f, indent=2, default=str)
        
        # Generate summary report
        self.generate_summary_report(survey_results, total_rows, total_size_mb)
        
        return survey_results
    
    def calculate_priority(self, table_name, row_count):
        """Calculate extraction priority based on table name and size"""
        high_priority_keywords = [
            'DONATION', 'ORGANIZATION', 'AGENCY', 'ORDER', 'INVENTORY',
            'PRODUCT', 'CLIENT', 'RECIPIENT', 'FOOD', 'MEAL'
        ]
        
        medium_priority_keywords = [
            'USER', 'LOG', 'AUDIT', 'CONFIG', 'LOOKUP', 'STATUS'
        ]
        
        table_upper = table_name.upper()
        
        if any(keyword in table_upper for keyword in high_priority_keywords):
            return 'high'
        elif any(keyword in table_upper for keyword in medium_priority_keywords):
            return 'medium'
        elif row_count < 100:
            return 'low'
        else:
            return 'medium'
    
    def generate_summary_report(self, results, total_rows, total_size_mb):
        """Generate comprehensive summary report"""
        print(f"\n" + "="*80)
        print(f"📊 DATABASE SURVEY SUMMARY REPORT")
        print(f"="*80)
        
        # Overall statistics
        total_tables = len(results)
        tables_with_data = len([r for r in results if r.get('row_count', 0) > 0])
        empty_tables = total_tables - tables_with_data
        error_tables = len([r for r in results if 'error' in r])
        
        print(f"\n📈 Overall Database Statistics:")
        print(f"   🗃️  Total Tables: {total_tables}")
        print(f"   📊 Tables with Data: {tables_with_data}")
        print(f"   📭 Empty Tables: {empty_tables}")
        print(f"   ❌ Error Tables: {error_tables}")
        print(f"   📏 Total Rows: {total_rows:,}")
        print(f"   💾 Total Size: ~{total_size_mb:.1f} MB")
        
        # Extraction time estimates
        total_extraction_time = sum(r.get('estimated_extraction_seconds', 0) for r in results)
        total_minutes = total_extraction_time / 60
        total_hours = total_minutes / 60
        
        print(f"   ⏱️  Total Extraction Time (Sequential): ~{total_minutes:.1f} minutes ({total_hours:.2f} hours)")
        print(f"   🚀 Parallel Extraction Time (3 workers): ~{total_minutes/3:.1f} minutes ({total_hours/3:.2f} hours)")
        
        # Priority breakdown
        high_priority = [r for r in results if r.get('priority') == 'high' and r.get('row_count', 0) > 0]
        medium_priority = [r for r in results if r.get('priority') == 'medium' and r.get('row_count', 0) > 0]
        low_priority = [r for r in results if r.get('priority') == 'low' and r.get('row_count', 0) > 0]
        
        print(f"\n🎯 Priority Breakdown:")
        print(f"   🔴 High Priority: {len(high_priority)} tables")
        print(f"   🟡 Medium Priority: {len(medium_priority)} tables") 
        print(f"   🟢 Low Priority: {len(low_priority)} tables")
        
        # Top 10 largest tables
        print(f"\n📊 Top 10 Largest Tables:")
        largest_tables = sorted([r for r in results if r.get('row_count', 0) > 0], 
                               key=lambda x: x.get('row_count', 0), reverse=True)[:10]
        
        for i, table in enumerate(largest_tables, 1):
            name = table['full_name']
            rows = table.get('row_count', 0)
            est_min = table.get('estimated_extraction_minutes', 0)
            priority = table.get('priority', 'unknown')
            priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '⚪')
            
            print(f"   {i:2}. {priority_icon} {name:<30} {rows:>8,} rows (~{est_min:>4.1f}min)")
        
        # High priority tables detail
        if high_priority:
            print(f"\n🔴 High Priority Tables (Recommended for POC):")
            high_priority_rows = 0
            high_priority_time = 0
            
            for table in high_priority:
                name = table['full_name']
                rows = table.get('row_count', 0)
                cols = table.get('column_count', 0)
                est_min = table.get('estimated_extraction_minutes', 0)
                size_mb = table.get('size_mb', 0)
                
                high_priority_rows += rows
                high_priority_time += est_min
                
                print(f"   📋 {name:<35} {rows:>8,} rows, {cols:>3} cols, {size_mb:>6.1f}MB (~{est_min:>4.1f}min)")
            
            print(f"\n   📊 High Priority Summary:")
            print(f"      Total Rows: {high_priority_rows:,}")
            print(f"      Sequential Time: ~{high_priority_time:.1f} minutes")
            print(f"      Parallel Time (3 workers): ~{high_priority_time/3:.1f} minutes")
        
        # Save summary to file
        summary_file = self.output_dir / 'extraction_strategy_summary.txt'
        with open(summary_file, 'w') as f:
            f.write("HungerHub Oracle Database Survey Summary\n")
            f.write("="*50 + "\n\n")
            f.write(f"Total Tables: {total_tables}\n")
            f.write(f"Tables with Data: {tables_with_data}\n")
            f.write(f"Total Rows: {total_rows:,}\n")
            f.write(f"Total Size: ~{total_size_mb:.1f} MB\n")
            f.write(f"Sequential Extraction Time: ~{total_minutes:.1f} minutes\n")
            f.write(f"Parallel Extraction Time: ~{total_minutes/3:.1f} minutes\n\n")
            
            f.write("Recommended High Priority Tables:\n")
            for table in high_priority:
                f.write(f"  - {table['full_name']} ({table.get('row_count', 0):,} rows)\n")
        
        print(f"\n💾 Detailed results saved to: {self.output_dir}")
        print(f"   📄 {results_file}")
        print(f"   📋 {summary_file}")

def main():
    surveyor = DatabaseSurveyor()
    results = surveyor.survey_database()
    
    print(f"\n✅ Database survey completed successfully!")
    return results

if __name__ == "__main__":
    main()
