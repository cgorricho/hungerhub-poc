#!/usr/bin/env python3
"""
HungerHub Dashboard - Comprehensive Test Suite
Tests all dashboard components and functionality
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.dirname(__file__))

def test_data_availability():
    """Test that required data files exist and are valid"""
    print("🔍 Testing data availability...")
    
    required_files = [
        'data/processed/unified/people.csv',
        'data/processed/unified/services.csv'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path} - Found")
            
            # Test file can be loaded
            try:
                df = pd.read_csv(file_path)
                print(f"     📊 Shape: {df.shape}")
                print(f"     📝 Columns: {list(df.columns)}")
            except Exception as e:
                print(f"     ❌ Error loading: {e}")
                all_exist = False
        else:
            print(f"  ❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist

def test_dashboard_modules():
    """Test that all dashboard modules can be imported"""
    print("\n🧩 Testing dashboard module imports...")
    
    modules_to_test = [
        ('dashboard.pages.executive_summary', 'render_executive_summary'),
        ('dashboard.pages.service_analytics', 'render_service_analytics'),
        ('dashboard.pages.vulnerability_assessment', 'render_vulnerability_assessment'),
        ('dashboard.pages.resource_optimization', 'render_resource_optimization')
    ]
    
    all_imported = True
    for module_name, function_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[function_name])
            func = getattr(module, function_name)
            print(f"  ✅ {module_name}.{function_name} - OK")
        except Exception as e:
            print(f"  ❌ {module_name}.{function_name} - Error: {e}")
            all_imported = False
    
    return all_imported

def test_vulnerability_scoring():
    """Test vulnerability scoring algorithm"""
    print("\n⚠️ Testing vulnerability assessment logic...")
    
    try:
        from dashboard.pages.vulnerability_assessment import calculate_vulnerability_score
        
        # Test cases
        test_cases = [
            # High risk case
            {
                'householdsize': 8,
                'income_level_numeric': 1,
                'service_frequency': 6,
                'age': 70,
                'expected_range': (7, 10)
            },
            # Low risk case
            {
                'householdsize': 2,
                'income_level_numeric': 4,
                'service_frequency': 1,
                'age': 35,
                'expected_range': (0, 3)
            },
            # Moderate risk case
            {
                'householdsize': 5,
                'income_level_numeric': 2,
                'service_frequency': 3,
                'age': 25,
                'expected_range': (3, 7)
            }
        ]
        
        for i, case in enumerate(test_cases):
            expected_range = case.pop('expected_range')
            score = calculate_vulnerability_score(case)
            
            if expected_range[0] <= score <= expected_range[1]:
                print(f"  ✅ Test case {i+1}: Score {score:.1f} in range {expected_range}")
            else:
                print(f"  ❌ Test case {i+1}: Score {score:.1f} NOT in range {expected_range}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Vulnerability scoring test failed: {e}")
        return False

def test_resource_optimization():
    """Test resource optimization calculations"""
    print("\n⚡ Testing resource optimization logic...")
    
    try:
        from dashboard.pages.resource_optimization import calculate_resource_metrics
        
        # Create test data
        test_services = pd.DataFrame({
            'person_id': [1, 1, 2, 2, 2, 3],
            'service_location': ['Location A', 'Location A', 'Location B', 'Location B', 'Location A', 'Location C'],
            'service_date': pd.date_range('2024-01-01', periods=6, freq='D')
        })
        
        metrics = calculate_resource_metrics(test_services)
        
        # Validate metrics
        expected_values = {
            'total_services': 6,
            'unique_people': 3,
            'avg_services_per_person': 2.0
        }
        
        all_correct = True
        for metric, expected in expected_values.items():
            actual = metrics.get(metric)
            if actual == expected:
                print(f"  ✅ {metric}: {actual} (expected {expected})")
            else:
                print(f"  ❌ {metric}: {actual} (expected {expected})")
                all_correct = False
        
        return all_correct
        
    except Exception as e:
        print(f"  ❌ Resource optimization test failed: {e}")
        return False

def test_analytics_calculations():
    """Test analytics calculations"""
    print("\n📈 Testing service analytics calculations...")
    
    try:
        # Create test data
        people_data = pd.DataFrame({
            'person_id': [1, 2, 3, 4, 5],
            'age': [25, 65, 15, 45, 75],
            'householdsize': [3, 1, 5, 2, 4],
            'state': ['CA', 'CA', 'TX', 'TX', 'FL']
        })
        
        services_data = pd.DataFrame({
            'person_id': [1, 1, 2, 3, 3, 3, 4, 5],
            'service_location': ['Food Bank A', 'Food Bank A', 'Food Bank B', 'Food Bank A', 'Food Bank A', 'Food Bank B', 'Food Bank C', 'Food Bank A'],
            'service_date': pd.date_range('2024-01-01', periods=8, freq='D')
        })
        
        # Test basic calculations
        total_people = len(people_data)
        total_services = len(services_data)
        unique_locations = services_data['service_location'].nunique()
        
        print(f"  📊 Test data: {total_people} people, {total_services} services, {unique_locations} locations")
        
        # Test age categorization
        def categorize_age(age):
            if age < 18:
                return 'Children'
            elif age >= 65:
                return 'Seniors'
            else:
                return 'Adults'
        
        age_dist = people_data['age'].apply(categorize_age).value_counts()
        print(f"  👥 Age distribution: {age_dist.to_dict()}")
        
        # Test service frequency
        service_freq = services_data['person_id'].value_counts()
        avg_services = service_freq.mean()
        print(f"  🎯 Average services per person: {avg_services:.1f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Analytics calculations test failed: {e}")
        return False

def generate_dashboard_test_report():
    """Generate comprehensive test report"""
    print("📋 Generating Dashboard Test Report...")
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Run all tests
    tests = [
        ('Data Availability', test_data_availability),
        ('Module Imports', test_dashboard_modules),
        ('Vulnerability Scoring', test_vulnerability_scoring),
        ('Resource Optimization', test_resource_optimization),
        ('Analytics Calculations', test_analytics_calculations)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results['tests'][test_name] = {
                'status': 'PASS' if result else 'FAIL',
                'passed': result
            }
            if not result:
                all_passed = False
        except Exception as e:
            test_results['tests'][test_name] = {
                'status': 'ERROR',
                'error': str(e),
                'passed': False
            }
            all_passed = False
    
    test_results['overall_status'] = 'PASS' if all_passed else 'FAIL'
    
    # Save test report
    import json
    os.makedirs('logs', exist_ok=True)
    with open('logs/dashboard_test_report.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("📋 DASHBOARD TEST SUMMARY")
    print(f"{'='*60}")
    
    for test_name, result in test_results['tests'].items():
        status_icon = "✅" if result['passed'] else "❌"
        print(f"{status_icon} {test_name}: {result['status']}")
    
    print(f"\n🎯 Overall Status: {test_results['overall_status']}")
    print(f"📄 Detailed report saved to: logs/dashboard_test_report.json")
    
    return all_passed

if __name__ == "__main__":
    print("🍽️ HungerHub Dashboard Test Suite")
    print("="*50)
    
    success = generate_dashboard_test_report()
    
    if success:
        print("\n🎉 All tests passed! Dashboard is ready for deployment.")
        exit(0)
    else:
        print("\n⚠️ Some tests failed. Check logs for details.")
        exit(1)
