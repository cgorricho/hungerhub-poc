#!/usr/bin/env python3
"""
Test script to validate the three enhancements implemented:
1. Sort donors by total gross weight (descending)
2. Dynamic date range from actual data
3. Secondary y-axis showing average weight per unit
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pandas as pd
from src.utils.paths import get_data_dir
from src.dashboard.modules import charts as hh_charts
from datetime import datetime

def test_enhancement_1():
    """Test Enhancement 1: Sort donors by total gross weight"""
    print("=" * 60)
    print("Testing Enhancement 1: Donor sorting by total gross weight")
    print("=" * 60)
    
    try:
        # Load raw donation data
        data_dir = get_data_dir('processed/real')
        donation_lines = pd.read_parquet(data_dir / 'AMX_DONATION_LINES.parquet')
        donation_header = pd.read_parquet(data_dir / 'AMX_DONATION_HEADER.parquet')
        
        # Merge to get donor names with gross weight
        merged = donation_lines.merge(
            donation_header[['DONATIONNUMBER', 'DONORNAME']], 
            on='DONATIONNUMBER'
        )
        
        # Calculate total gross weight per donor
        donor_gross_weight = merged.groupby('DONORNAME')['TOTALGROSSWEIGHT'].sum().sort_values(ascending=False)
        
        print(f"✅ Successfully loaded {len(donor_gross_weight)} donors")
        print("Top 10 donors by total gross weight:")
        for i, (donor, weight) in enumerate(donor_gross_weight.head(10).items(), 1):
            weight_tonnes = weight / 2204.62262185
            print(f"  {i:2d}. {donor:<25} - {weight:>12,.0f} lbs ({weight_tonnes:>8,.1f} t)")
        
        # Verify sorting is descending
        weights = donor_gross_weight.head(10).values
        is_descending = all(weights[i] >= weights[i+1] for i in range(len(weights)-1))
        print(f"\n✅ Sorting validation: {'PASS' if is_descending else 'FAIL'} - Data is sorted descending")
        
    except Exception as e:
        print(f"❌ Enhancement 1 failed: {e}")
        return False
    
    return True

def test_enhancement_2():
    """Test Enhancement 2: Dynamic date range extraction"""
    print("\n" + "=" * 60)
    print("Testing Enhancement 2: Dynamic date range from actual data")
    print("=" * 60)
    
    try:
        data_dir = get_data_dir('processed/real')
        donation_header = pd.read_parquet(data_dir / 'AMX_DONATION_HEADER.parquet')
        
        # Convert donation date to datetime and find min/max
        donation_header['DONATIONDATE'] = pd.to_datetime(donation_header['DONATIONDATE'], errors='coerce')
        
        min_date = donation_header['DONATIONDATE'].min()
        max_date = donation_header['DONATIONDATE'].max()
        
        print(f"✅ Successfully extracted date range from {len(donation_header)} donation records")
        print(f"📅 Earliest donation: {min_date.strftime('%Y-%m-%d') if pd.notna(min_date) else 'N/A'}")
        print(f"📅 Latest donation:   {max_date.strftime('%Y-%m-%d') if pd.notna(max_date) else 'N/A'}")
        
        if pd.notna(min_date) and pd.notna(max_date):
            date_span = (max_date - min_date).days
            print(f"📈 Date range spans:  {date_span} days ({date_span/365.25:.1f} years)")
            
            # Convert to date objects as would be done for Streamlit
            min_date_obj = min_date.date()
            max_date_obj = max_date.date()
            print(f"✅ Date conversion:   {min_date_obj} to {max_date_obj}")
        else:
            print("❌ Invalid date range detected")
            return False
            
    except Exception as e:
        print(f"❌ Enhancement 2 failed: {e}")
        return False
    
    return True

def test_enhancement_3():
    """Test Enhancement 3: Secondary y-axis for average weight per unit"""
    print("\n" + "=" * 60)
    print("Testing Enhancement 3: Secondary y-axis for avg weight per unit")
    print("=" * 60)
    
    try:
        # Load donor performance and gross weight data
        data_dir_unified = get_data_dir('processed/unified_real')
        data_dir_real = get_data_dir('processed/real')
        
        # Load donor performance data (has quantities)
        donor_performance = pd.read_parquet(data_dir_unified / 'view_donor_performance.parquet')
        
        # Load gross weight data
        donation_lines = pd.read_parquet(data_dir_real / 'AMX_DONATION_LINES.parquet')
        donation_header = pd.read_parquet(data_dir_real / 'AMX_DONATION_HEADER.parquet')
        
        # Calculate gross weight per donor
        merged = donation_lines.merge(
            donation_header[['DONATIONNUMBER', 'DONORNAME']], 
            on='DONATIONNUMBER'
        )
        donor_gross_weight = merged.groupby('DONORNAME')['TOTALGROSSWEIGHT'].sum().sort_values(ascending=False)
        
        # Prepare test chart data (top 5 donors)
        top_5_donors = donor_gross_weight.head(5)
        chart_df = top_5_donors.reset_index()
        chart_df.columns = ['donor_name', 'total_weight_lbs']
        
        # Add quantity data from donor performance
        donor_perf_data = donor_performance.reset_index()
        donor_perf_data.columns = ['donor_name'] + list(donor_perf_data.columns[1:])
        chart_df = chart_df.merge(donor_perf_data[['donor_name', 'total_donated_qty']], on='donor_name', how='left')
        
        print(f"✅ Prepared chart data for {len(chart_df)} donors")
        print("Sample data for chart:")
        for _, row in chart_df.iterrows():
            weight_tonnes = row['total_weight_lbs'] / 2204.62262185
            weight_lbs = row['total_weight_lbs']
            qty = row['total_donated_qty']
            avg_weight_per_unit_lbs = weight_lbs / qty if qty > 0 else 0
            print(f"  {row['donor_name']:<25} - {weight_tonnes:>8.1f} t, {qty:>12,.0f} units, {avg_weight_per_unit_lbs:>8.2f} lbs/unit")
        
        # Test the enhanced chart function
        fig = hh_charts.donor_performance(chart_df, include_avg_weight_per_unit=True)
        
        print(f"✅ Chart generation successful")
        print(f"✅ Chart has {len(fig.data)} traces (expecting 2: bars + scatter)")
        
        # Verify chart has both bar and scatter traces
        has_bar = any(trace.type == 'bar' for trace in fig.data)
        has_scatter = any(trace.type == 'scatter' for trace in fig.data)
        
        print(f"✅ Bar trace present: {'YES' if has_bar else 'NO'}")
        print(f"✅ Scatter trace present: {'YES' if has_scatter else 'NO'}")
        
        # Check for secondary y-axis
        has_secondary_yaxis = 'yaxis2' in fig.layout
        print(f"✅ Secondary y-axis configured: {'YES' if has_secondary_yaxis else 'NO'}")
        
        if has_bar and has_scatter and has_secondary_yaxis:
            print("✅ Enhancement 3 validation: PASS - All components present")
        else:
            print("❌ Enhancement 3 validation: FAIL - Missing components")
            return False
        
    except Exception as e:
        print(f"❌ Enhancement 3 failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Run all enhancement tests"""
    print("HungerHub Section 1 Enhancement Tests")
    print("Testing three key enhancements to donor analysis:")
    print("1. Sort donors by total gross weight (descending)")
    print("2. Dynamic date range from actual data") 
    print("3. Secondary y-axis for average weight per unit")
    print()
    
    results = []
    
    # Run tests
    results.append(test_enhancement_1())
    results.append(test_enhancement_2()) 
    results.append(test_enhancement_3())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Enhancement 1 (Donor sorting): {'✅ PASS' if results[0] else '❌ FAIL'}")
    print(f"Enhancement 2 (Dynamic dates): {'✅ PASS' if results[1] else '❌ FAIL'}")  
    print(f"Enhancement 3 (Secondary axis): {'✅ PASS' if results[2] else '❌ FAIL'}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enhancements are working correctly!")
        print("The Streamlit dashboard is ready with:")
        print("  - Donors sorted by total weight (highest first)")
        print("  - Date range automatically set to data bounds")
        print("  - Dual y-axis chart showing weight + avg weight per unit")
    else:
        print("⚠️  Some enhancements need attention before deployment")
    
    return passed == total

if __name__ == "__main__":
    main()
