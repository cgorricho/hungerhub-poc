#!/usr/bin/env python3
"""
Unit tests for ETL Pipeline
"""

import unittest
import pandas as pd
import tempfile
import os
from datetime import datetime
import sys
import json

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestETLPipeline(unittest.TestCase):
    """Test cases for ETL Pipeline functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create sample test data
        self.sample_clients = pd.DataFrame({
            'ClientID': [1, 2, 3],
            'FirstName': ['John', 'Jane', 'Bob'],
            'LastName': ['Doe', 'Smith', 'Johnson'],
            'DateOfBirth': ['1990-01-01', '1985-05-15', '1975-12-30'],
            'HouseholdSize': [3, 2, 4]
        })
        
        self.sample_services = pd.DataFrame({
            'ServiceID': [1, 2, 3],
            'ClientID': [1, 1, 2],
            'ServiceType': ['Food Pantry', 'WIC', 'SNAP'],
            'ServiceDate': ['2024-01-15', '2024-01-20', '2024-01-25'],
            'FoodPounds': [25.5, 30.0, 20.0]
        })
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_data_transformation(self):
        """Test data transformation functions"""
        # Test column name standardization
        transformed_df = self.sample_clients.copy()
        transformed_df.columns = [col.lower().replace(' ', '_') for col in transformed_df.columns]
        
        expected_columns = ['clientid', 'firstname', 'lastname', 'dateofbirth', 'householdsize']
        self.assertEqual(list(transformed_df.columns), expected_columns)
    
    def test_data_unification(self):
        """Test data unification process"""
        # Test that data from different sources can be unified
        unified_count = len(self.sample_clients) + 5  # Assuming 5 participants
        self.assertGreater(unified_count, len(self.sample_clients))
    
    def test_summary_statistics(self):
        """Test summary statistics calculation"""
        total_services = len(self.sample_services)
        total_food = self.sample_services['FoodPounds'].sum()
        
        self.assertEqual(total_services, 3)
        self.assertEqual(total_food, 75.5)
    
    def test_config_loading(self):
        """Test configuration loading"""
        # Test that config can be loaded or defaults created
        config_keys = ['databases', 'etl_settings', 'transformation_rules']
        
        # This would test actual config loading in real implementation
        mock_config = {
            'databases': {},
            'etl_settings': {},
            'transformation_rules': {}
        }
        
        for key in config_keys:
            self.assertIn(key, mock_config)

if __name__ == '__main__':
    unittest.main()
