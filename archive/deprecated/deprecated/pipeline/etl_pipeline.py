#!/usr/bin/env python3
"""
HungerHub POC - ETL Pipeline Foundation
Extracts, transforms, and loads data from Choice and AgencyExpress databases
"""

import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import os
from typing import Dict, List, Optional, Tuple
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HungerHubETL:
    """Main ETL pipeline for HungerHub POC"""
    
    def __init__(self, config_path: str = 'config/etl_config.json'):
        self.config_path = config_path
        self.config = self.load_config()
        self.schema_info = self.load_schema_info()
        
        # Create output directories
        self.setup_directories()
        
    def load_config(self) -> Dict:
        """Load ETL configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"✅ Loaded config from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"⚠️ Config file not found, creating default config")
            return self.create_default_config()
    
    def create_default_config(self) -> Dict:
        """Create default ETL configuration"""
        default_config = {
            "databases": {
                "choice": {
                    "name": "Choice",
                    "priority_tables": ["dbo.Clients", "dbo.Services", "dbo.FoodInventory"]
                },
                "agency_express": {
                    "name": "AgencyExpress", 
                    "priority_tables": ["dbo.Participants", "dbo.ProgramAssistance", "dbo.Agencies"]
                }
            },
            "etl_settings": {
                "batch_size": 1000,
                "data_retention_days": 90,
                "enable_data_validation": True,
                "output_formats": ["csv", "parquet"],
                "enable_incremental_load": True
            },
            "transformation_rules": {
                "standardize_names": True,
                "normalize_addresses": True,
                "calculate_demographics": True,
                "generate_food_metrics": True
            },
            "data_quality": {
                "required_fields": {
                    "client_data": ["id", "first_name", "last_name"],
                    "service_data": ["id", "client_id", "service_date", "service_type"],
                    "participant_data": ["id", "first_name", "last_name", "enrollment_date"]
                },
                "data_types": {
                    "dates": ["service_date", "enrollment_date", "dob", "created_date"],
                    "numeric": ["household_size", "food_pounds", "benefit_amount"],
                    "categorical": ["service_type", "program_type", "gender", "state"]
                }
            }
        }
        
        # Save default config
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"📄 Created default config at {self.config_path}")
        return default_config
    
    def load_schema_info(self) -> Dict:
        """Load database schema information"""
        schema_path = 'data/schemas/database_exploration_report.json'
        try:
            with open(schema_path, 'r') as f:
                schema_info = json.load(f)
            logger.info(f"✅ Loaded schema info from {schema_path}")
            return schema_info
        except FileNotFoundError:
            logger.error(f"❌ Schema file not found at {schema_path}")
            raise
    
    def setup_directories(self):
        """Create necessary output directories"""
        directories = [
            'data/processed/choice',
            'data/processed/agency_express',
            'data/processed/unified',
            'data/output/dashboard',
            'data/output/reports',
            'logs'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        logger.info("📁 Created output directories")
    
    def extract_choice_data(self) -> Dict[str, pd.DataFrame]:
        """Extract data from Choice database (using mock data for now)"""
        logger.info("📥 Extracting Choice database data...")
        
        extracted_data = {}
        
        # For now, load from sample files
        try:
            # Load Clients data
            clients_df = pd.read_csv('data/samples/Choice_dbo_Clients_sample.csv')
            extracted_data['clients'] = clients_df
            logger.info(f"   • Extracted {len(clients_df)} client records")
            
            # Create mock Services data based on clients
            services_data = []
            service_types = ['Food Pantry', 'Meal Service', 'Emergency Food', 'Nutrition Education']
            
            for _, client in clients_df.iterrows():
                # Generate 2-5 service records per client
                num_services = np.random.randint(2, 6)
                for i in range(num_services):
                    service_date = datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 90))
                    services_data.append({
                        'ServiceID': len(services_data) + 1,
                        'ClientID': client['ClientID'],
                        'ServiceType': np.random.choice(service_types),
                        'ServiceDate': service_date.date(),
                        'Location': 'Main Pantry',
                        'FoodPounds': np.random.uniform(10, 50),
                        'MealCount': np.random.randint(1, 10),
                        'Notes': f'Service for household of {client["HouseholdSize"]}'
                    })
            
            services_df = pd.DataFrame(services_data)
            extracted_data['services'] = services_df
            logger.info(f"   • Generated {len(services_df)} service records")
            
        except Exception as e:
            logger.error(f"❌ Error extracting Choice data: {e}")
            raise
        
        return extracted_data
    
    def extract_agency_data(self) -> Dict[str, pd.DataFrame]:
        """Extract data from AgencyExpress database (using mock data for now)"""
        logger.info("📥 Extracting AgencyExpress database data...")
        
        extracted_data = {}
        
        try:
            # Load Participants data
            participants_df = pd.read_csv('data/samples/AgencyExpress_dbo_Participants_sample.csv')
            extracted_data['participants'] = participants_df
            logger.info(f"   • Extracted {len(participants_df)} participant records")
            
            # Create mock Program Assistance data
            assistance_data = []
            program_types = ['SNAP', 'WIC', 'Food Bank', 'Senior Meals', 'Backpack Program']
            
            for _, participant in participants_df.iterrows():
                # Generate 3-8 assistance records per participant
                num_assistance = np.random.randint(3, 9)
                for i in range(num_assistance):
                    assistance_date = datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 90))
                    assistance_data.append({
                        'AssistanceID': len(assistance_data) + 1,
                        'ParticipantID': participant['ParticipantID'],
                        'ProgramType': np.random.choice(program_types),
                        'AssistanceDate': assistance_date.date(),
                        'BenefitAmount': np.random.uniform(50, 500),
                        'FoodValue': np.random.uniform(25, 200),
                        'ServingSize': participant['HouseholdSize'],
                        'AgencyLocation': 'Downtown Center',
                        'Status': 'Completed'
                    })
            
            assistance_df = pd.DataFrame(assistance_data)
            extracted_data['assistance'] = assistance_df
            logger.info(f"   • Generated {len(assistance_df)} assistance records")
            
        except Exception as e:
            logger.error(f"❌ Error extracting AgencyExpress data: {e}")
            raise
        
        return extracted_data
    
    def transform_choice_data(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Transform Choice database data"""
        logger.info("🔄 Transforming Choice data...")
        
        transformed_data = {}
        
        try:
            # Transform Clients data
            clients_df = raw_data['clients'].copy()
            
            # Standardize column names
            clients_df.columns = [col.lower().replace(' ', '_') for col in clients_df.columns]
            
            # Parse dates
            clients_df['dateofbirth'] = pd.to_datetime(clients_df['dateofbirth'])
            clients_df['createddate'] = pd.to_datetime(clients_df['createddate'])
            
            # Calculate age
            clients_df['age'] = (datetime.now() - clients_df['dateofbirth']).dt.days / 365.25
            clients_df['age'] = clients_df['age'].astype(int)
            
            # Create full name
            clients_df['full_name'] = clients_df['firstname'] + ' ' + clients_df['lastname']
            
            # Standardize phone numbers
            clients_df['phone'] = clients_df['phone'].str.replace(r'[^\d]', '', regex=True)
            
            # Add data source
            clients_df['data_source'] = 'Choice'
            clients_df['record_type'] = 'client'
            
            transformed_data['clients'] = clients_df
            logger.info(f"   • Transformed {len(clients_df)} client records")
            
            # Transform Services data
            services_df = raw_data['services'].copy()
            services_df.columns = [col.lower().replace(' ', '_') for col in services_df.columns]
            
            # Parse dates
            services_df['servicedate'] = pd.to_datetime(services_df['servicedate'])
            
            # Add derived fields
            services_df['year'] = services_df['servicedate'].dt.year
            services_df['month'] = services_df['servicedate'].dt.month
            services_df['quarter'] = services_df['servicedate'].dt.quarter
            services_df['day_of_week'] = services_df['servicedate'].dt.day_name()
            
            # Calculate per-person metrics
            client_household_map = dict(zip(clients_df['clientid'], clients_df['householdsize']))
            services_df['household_size'] = services_df['clientid'].map(client_household_map)
            services_df['food_pounds_per_person'] = services_df['foodpounds'] / services_df['household_size']
            services_df['meals_per_person'] = services_df['mealcount'] / services_df['household_size']
            
            # Add data source
            services_df['data_source'] = 'Choice'
            services_df['record_type'] = 'service'
            
            transformed_data['services'] = services_df
            logger.info(f"   • Transformed {len(services_df)} service records")
            
        except Exception as e:
            logger.error(f"❌ Error transforming Choice data: {e}")
            raise
        
        return transformed_data
    
    def transform_agency_data(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Transform AgencyExpress database data"""
        logger.info("🔄 Transforming AgencyExpress data...")
        
        transformed_data = {}
        
        try:
            # Transform Participants data
            participants_df = raw_data['participants'].copy()
            participants_df.columns = [col.lower().replace(' ', '_') for col in participants_df.columns]
            
            # Parse dates
            participants_df['dob'] = pd.to_datetime(participants_df['dob'])
            participants_df['enrollmentdate'] = pd.to_datetime(participants_df['enrollmentdate'])
            
            # Calculate age
            participants_df['age'] = (datetime.now() - participants_df['dob']).dt.days / 365.25
            participants_df['age'] = participants_df['age'].astype(int)
            
            # Create full name
            participants_df['full_name'] = participants_df['firstname'] + ' ' + participants_df['lastname']
            
            # Standardize phone numbers
            participants_df['phone'] = participants_df['phone'].str.replace(r'[^\d]', '', regex=True)
            
            # Map income levels to numeric values
            income_mapping = {'Very Low': 1, 'Low': 2, 'Moderate': 3, 'High': 4}
            participants_df['income_level_numeric'] = participants_df['incomelevel'].map(income_mapping)
            
            # Add data source
            participants_df['data_source'] = 'AgencyExpress'
            participants_df['record_type'] = 'participant'
            
            transformed_data['participants'] = participants_df
            logger.info(f"   • Transformed {len(participants_df)} participant records")
            
            # Transform Assistance data
            assistance_df = raw_data['assistance'].copy()
            assistance_df.columns = [col.lower().replace(' ', '_') for col in assistance_df.columns]
            
            # Parse dates
            assistance_df['assistancedate'] = pd.to_datetime(assistance_df['assistancedate'])
            
            # Add derived fields
            assistance_df['year'] = assistance_df['assistancedate'].dt.year
            assistance_df['month'] = assistance_df['assistancedate'].dt.month
            assistance_df['quarter'] = assistance_df['assistancedate'].dt.quarter
            assistance_df['day_of_week'] = assistance_df['assistancedate'].dt.day_name()
            
            # Calculate per-person metrics
            assistance_df['benefit_per_person'] = assistance_df['benefitamount'] / assistance_df['servingsize']
            assistance_df['food_value_per_person'] = assistance_df['foodvalue'] / assistance_df['servingsize']
            
            # Add data source
            assistance_df['data_source'] = 'AgencyExpress'
            assistance_df['record_type'] = 'assistance'
            
            transformed_data['assistance'] = assistance_df
            logger.info(f"   • Transformed {len(assistance_df)} assistance records")
            
        except Exception as e:
            logger.error(f"❌ Error transforming AgencyExpress data: {e}")
            raise
        
        return transformed_data
    
    def create_unified_dataset(self, choice_data: Dict[str, pd.DataFrame], 
                             agency_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Create unified dataset combining both databases"""
        logger.info("🔗 Creating unified dataset...")
        
        unified_data = {}
        
        try:
            # Unified People dataset (Clients + Participants)
            choice_people = choice_data['clients'][['clientid', 'full_name', 'firstname', 'lastname', 
                                                   'age', 'phone', 'email', 'city', 'state', 
                                                   'zipcode', 'householdsize', 'data_source']].copy()
            choice_people.rename(columns={'clientid': 'person_id'}, inplace=True)
            
            agency_people = agency_data['participants'][['participantid', 'full_name', 'firstname', 'lastname',
                                                       'age', 'phone', 'email', 'city', 'state',
                                                       'zipcode', 'householdsize', 'data_source', 'gender',
                                                       'income_level_numeric']].copy()
            agency_people.rename(columns={'participantid': 'person_id'}, inplace=True)
            
            # Add missing columns with defaults
            choice_people['gender'] = 'Unknown'
            choice_people['income_level_numeric'] = np.nan
            agency_people['gender'] = agency_people.get('gender', 'Unknown')
            
            # Combine people data
            unified_people = pd.concat([choice_people, agency_people], ignore_index=True, sort=False)
            unified_people['unified_person_id'] = range(1, len(unified_people) + 1)
            
            unified_data['people'] = unified_people
            logger.info(f"   • Created unified people dataset with {len(unified_people)} records")
            
            # Unified Services dataset (Services + Assistance)
            choice_services = choice_data['services'][['serviceid', 'clientid', 'servicetype', 'servicedate',
                                                     'year', 'month', 'quarter', 'foodpounds', 'mealcount',
                                                     'food_pounds_per_person', 'data_source']].copy()
            choice_services.rename(columns={'serviceid': 'service_id', 'clientid': 'person_id',
                                          'servicetype': 'service_type', 'servicedate': 'service_date'}, inplace=True)
            choice_services['benefit_amount'] = np.nan
            choice_services['food_value'] = choice_services['foodpounds'] * 2.5  # Estimate food value
            
            agency_services = agency_data['assistance'][['assistanceid', 'participantid', 'programtype', 'assistancedate',
                                                       'year', 'month', 'quarter', 'benefitamount', 'foodvalue',
                                                       'benefit_per_person', 'data_source']].copy()
            agency_services.rename(columns={'assistanceid': 'service_id', 'participantid': 'person_id',
                                          'programtype': 'service_type', 'assistancedate': 'service_date',
                                          'benefitamount': 'benefit_amount', 'foodvalue': 'food_value'}, inplace=True)
            agency_services['foodpounds'] = agency_services['food_value'] / 2.5  # Estimate food pounds
            agency_services['mealcount'] = np.nan
            agency_services['food_pounds_per_person'] = agency_services['foodpounds'] / 1  # Placeholder
            
            # Combine services data
            unified_services = pd.concat([choice_services, agency_services], ignore_index=True, sort=False)
            unified_services['unified_service_id'] = range(1, len(unified_services) + 1)
            
            unified_data['services'] = unified_services
            logger.info(f"   • Created unified services dataset with {len(unified_services)} records")
            
            # Create summary statistics
            summary_stats = self.calculate_summary_statistics(unified_data)
            unified_data['summary'] = summary_stats
            
        except Exception as e:
            logger.error(f"❌ Error creating unified dataset: {e}")
            raise
        
        return unified_data
    
    def calculate_summary_statistics(self, unified_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Calculate summary statistics for the unified dataset"""
        logger.info("📊 Calculating summary statistics...")
        
        people_df = unified_data['people']
        services_df = unified_data['services']
        
        # Overall statistics
        stats = {
            'total_people_served': len(people_df),
            'total_services_provided': len(services_df),
            'unique_service_types': services_df['service_type'].nunique(),
            'average_household_size': people_df['householdsize'].mean(),
            'total_food_distributed_lbs': services_df['foodpounds'].sum(),
            'total_benefit_value': services_df['benefit_amount'].sum(),
            'services_per_person': len(services_df) / len(people_df),
            'date_range': f"{services_df['service_date'].min()} to {services_df['service_date'].max()}"
        }
        
        # Convert to DataFrame for easier handling
        stats_df = pd.DataFrame([stats])
        
        logger.info(f"   • People served: {stats['total_people_served']:,}")
        logger.info(f"   • Services provided: {stats['total_services_provided']:,}")
        logger.info(f"   • Food distributed: {stats['total_food_distributed_lbs']:,.1f} lbs")
        
        return stats_df
    
    def load_data(self, unified_data: Dict[str, pd.DataFrame]):
        """Load processed data to output destinations"""
        logger.info("💾 Loading processed data...")
        
        try:
            # Save to multiple formats
            for dataset_name, df in unified_data.items():
                if dataset_name == 'summary':
                    continue
                    
                # CSV format
                csv_path = f'data/processed/unified/{dataset_name}.csv'
                df.to_csv(csv_path, index=False)
                logger.info(f"   • Saved {dataset_name} to {csv_path}")
                
                # Parquet format for better performance
                parquet_path = f'data/processed/unified/{dataset_name}.parquet'
                df.to_parquet(parquet_path, index=False)
                logger.info(f"   • Saved {dataset_name} to {parquet_path}")
            
            # Save summary statistics
            summary_df = unified_data['summary']
            summary_df.to_csv('data/output/reports/summary_statistics.csv', index=False)
            
            # Create a metadata file
            metadata = {
                'etl_timestamp': datetime.now().isoformat(),
                'datasets_created': list(unified_data.keys()),
                'total_records': {name: len(df) for name, df in unified_data.items() if name != 'summary'},
                'data_sources': ['Choice', 'AgencyExpress'],
                'next_scheduled_run': (datetime.now() + timedelta(days=1)).isoformat()
            }
            
            with open('data/output/etl_metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            logger.info("✅ Data loading completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            raise
    
    def run_full_etl(self):
        """Execute the complete ETL pipeline"""
        logger.info("🚀 Starting HungerHub ETL Pipeline...")
        
        start_time = datetime.now()
        
        try:
            # Extract phase
            logger.info("\n" + "="*50)
            logger.info("📥 EXTRACTION PHASE")
            logger.info("="*50)
            
            choice_raw = self.extract_choice_data()
            agency_raw = self.extract_agency_data()
            
            # Transform phase
            logger.info("\n" + "="*50)
            logger.info("🔄 TRANSFORMATION PHASE")
            logger.info("="*50)
            
            choice_transformed = self.transform_choice_data(choice_raw)
            agency_transformed = self.transform_agency_data(agency_raw)
            
            # Create unified dataset
            unified_data = self.create_unified_dataset(choice_transformed, agency_transformed)
            
            # Load phase
            logger.info("\n" + "="*50)
            logger.info("💾 LOADING PHASE")
            logger.info("="*50)
            
            self.load_data(unified_data)
            
            # Final summary
            duration = datetime.now() - start_time
            
            logger.info("\n" + "="*50)
            logger.info("✅ ETL PIPELINE COMPLETED!")
            logger.info("="*50)
            logger.info(f"📊 Duration: {duration}")
            logger.info(f"📈 People processed: {len(unified_data['people']):,}")
            logger.info(f"📈 Services processed: {len(unified_data['services']):,}")
            logger.info(f"💾 Output location: data/processed/unified/")
            logger.info("="*50)
            
            return unified_data
            
        except Exception as e:
            logger.error(f"💥 ETL Pipeline failed: {e}")
            raise

if __name__ == "__main__":
    # Run the ETL pipeline
    etl = HungerHubETL()
    
    try:
        unified_data = etl.run_full_etl()
        print("\n🎉 ETL Pipeline executed successfully!")
        print("📊 Check data/processed/unified/ for output files")
        
    except Exception as e:
        print(f"\n💥 ETL Pipeline failed: {e}")
        print("📝 Check logs/etl_pipeline.log for detailed error information")
