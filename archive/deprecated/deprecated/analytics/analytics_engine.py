#!/usr/bin/env python3
"""
HungerHub POC - Analytics Engine
Generates insights and metrics from the unified hunger assistance data
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging
from pathlib import Path
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analytics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HungerHubAnalytics:
    """Analytics engine for hunger assistance data"""
    
    def __init__(self, data_path: str = 'data/processed/unified'):
        self.data_path = data_path
        self.people_df = None
        self.services_df = None
        self.insights = {}
        
        # Load the processed data
        self.load_data()
        
        # Setup matplotlib for headless operation
        plt.switch_backend('Agg')
        sns.set_style("whitegrid")
        
    def load_data(self):
        """Load the unified datasets"""
        try:
            self.people_df = pd.read_csv(f'{self.data_path}/people.csv')
            self.services_df["day_of_week"] = self.services_df["service_date"].dt.day_name()
            
            # Add day_of_week for analysis
            self.services_df["day_of_week"] = self.services_df["service_date"].dt.day_name()
            # Parse dates
            self.services_df['service_date'] = pd.to_datetime(self.services_df['service_date'])
            
            logger.info(f"✅ Loaded {len(self.people_df)} people and {len(self.services_df)} service records")
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            raise
    
    def analyze_demographics(self) -> dict:
        """Analyze demographic patterns"""
        logger.info("👥 Analyzing demographics...")
        
        demographics = {}
        
        # Age distribution
        demographics['age_stats'] = {
            'mean_age': self.people_df['age'].mean(),
            'median_age': self.people_df['age'].median(),
            'age_range': {
                'min': self.people_df['age'].min(),
                'max': self.people_df['age'].max()
            }
        }
        
        # Age groups
        age_bins = [0, 18, 35, 50, 65, 100]
        age_labels = ['Under 18', '18-34', '35-49', '50-64', '65+']
        self.people_df['age_group'] = pd.cut(self.people_df['age'], bins=age_bins, labels=age_labels)
        age_distribution = self.people_df['age_group'].value_counts().to_dict()
        demographics['age_distribution'] = {str(k): v for k, v in age_distribution.items()}
        
        # Household size distribution
        household_stats = self.people_df['householdsize'].value_counts().to_dict()
        demographics['household_size_distribution'] = household_stats
        demographics['avg_household_size'] = self.people_df['householdsize'].mean()
        
        # Geographic distribution
        state_distribution = self.people_df['state'].value_counts().to_dict()
        city_distribution = self.people_df['city'].value_counts().to_dict()
        demographics['geographic_distribution'] = {
            'by_state': state_distribution,
            'by_city': city_distribution
        }
        
        # Data source breakdown
        source_distribution = self.people_df['data_source'].value_counts().to_dict()
        demographics['data_source_distribution'] = source_distribution
        
        logger.info(f"   • Average age: {demographics['age_stats']['mean_age']:.1f} years")
        logger.info(f"   • Average household size: {demographics['avg_household_size']:.1f}")
        logger.info(f"   • States represented: {len(state_distribution)}")
        
        return demographics
    
    def analyze_service_patterns(self) -> dict:
        """Analyze service utilization patterns"""
        logger.info("🍽️ Analyzing service patterns...")
        
        patterns = {}
        
        # Service type analysis
        service_type_counts = self.services_df['service_type'].value_counts().to_dict()
        patterns['service_types'] = service_type_counts
        
        # Temporal patterns
        patterns['temporal_analysis'] = {
            'services_by_month': self.services_df['month'].value_counts().sort_index().to_dict(),
            'services_by_quarter': self.services_df['quarter'].value_counts().sort_index().to_dict(),
            'services_by_day_of_week': self.services_df['day_of_week'].value_counts().to_dict()
        }
        
        # Food distribution analysis
        total_food_distributed = self.services_df['foodpounds'].sum()
        avg_food_per_service = self.services_df['foodpounds'].mean()
        
        patterns['food_distribution'] = {
            'total_pounds_distributed': total_food_distributed,
            'average_pounds_per_service': avg_food_per_service,
            'food_distribution_by_service_type': self.services_df.groupby('service_type')['foodpounds'].sum().to_dict()
        }
        
        # Service frequency per person
        services_per_person = self.services_df.groupby('person_id').size()
        patterns['service_frequency'] = {
            'avg_services_per_person': services_per_person.mean(),
            'median_services_per_person': services_per_person.median(),
            'max_services_per_person': services_per_person.max(),
            'frequency_distribution': services_per_person.value_counts().to_dict()
        }
        
        # Benefit analysis (for AgencyExpress data)
        agency_services = self.services_df[self.services_df['data_source'] == 'AgencyExpress']
        if len(agency_services) > 0:
            patterns['benefit_analysis'] = {
                'total_benefit_value': agency_services['benefit_amount'].sum(),
                'avg_benefit_per_service': agency_services['benefit_amount'].mean(),
                'benefit_by_program_type': agency_services.groupby('service_type')['benefit_amount'].sum().to_dict()
            }
        
        logger.info(f"   • Total food distributed: {total_food_distributed:.1f} lbs")
        logger.info(f"   • Most common service: {max(service_type_counts.keys(), key=service_type_counts.get)}")
        logger.info(f"   • Average services per person: {patterns['service_frequency']['avg_services_per_person']:.1f}")
        
        return patterns
    
    def identify_food_insecurity_indicators(self) -> dict:
        """Identify key food insecurity indicators"""
        logger.info("⚠️ Analyzing food insecurity indicators...")
        
        indicators = {}
        
        # Merge people and services for analysis
        merged_df = self.services_df.merge(self.people_df, on='person_id', how='left')
        
        # High-need households (large families with frequent service use)
        high_need_threshold = merged_df['householdsize'].quantile(0.75)
        frequent_service_threshold = merged_df.groupby('person_id').size().quantile(0.75)
        
        high_need_households = merged_df[
            (merged_df['householdsize'] >= high_need_threshold) |
            (merged_df.groupby('person_id')['person_id'].transform('count') >= frequent_service_threshold)
        ]['person_id'].unique()
        
        indicators['high_need_analysis'] = {
            'high_need_household_count': len(high_need_households),
            'percentage_of_total': (len(high_need_households) / len(self.people_df)) * 100,
            'threshold_criteria': {
                'household_size_threshold': high_need_threshold,
                'service_frequency_threshold': frequent_service_threshold
            }
        }
        
        # Geographic hotspots (areas with high service concentration)
        city_service_density = merged_df.groupby('city').agg({
            'person_id': 'nunique',
            'service_id': 'count',
            'foodpounds': 'sum'
        }).reset_index()
        city_service_density['services_per_person'] = city_service_density['service_id'] / city_service_density['person_id']
        
        indicators['geographic_hotspots'] = {
            'cities_by_service_density': city_service_density.sort_values('services_per_person', ascending=False).to_dict('records'),
            'top_cities_by_food_distribution': city_service_density.nlargest(3, 'foodpounds')[['city', 'foodpounds']].to_dict('records')
        }
        
        # Vulnerability indicators
        vulnerability_scores = []
        for _, person in self.people_df.iterrows():
            score = 0
            
            # Large household size
            if person['householdsize'] >= 4:
                score += 2
            elif person['householdsize'] >= 3:
                score += 1
            
            # Income level (if available)
            if not pd.isna(person.get('income_level_numeric', np.nan)):
                if person['income_level_numeric'] <= 2:  # Very Low or Low
                    score += 3
            
            # Service frequency
            person_services = len(self.services_df[self.services_df['person_id'] == person['person_id']])
            if person_services >= 5:
                score += 2
            elif person_services >= 3:
                score += 1
            
            vulnerability_scores.append({
                'person_id': person['person_id'],
                'vulnerability_score': score,
                'full_name': person['full_name']
            })
        
        vulnerability_df = pd.DataFrame(vulnerability_scores)
        high_vulnerability = vulnerability_df[vulnerability_df['vulnerability_score'] >= 4]
        
        indicators['vulnerability_analysis'] = {
            'high_vulnerability_count': len(high_vulnerability),
            'avg_vulnerability_score': vulnerability_df['vulnerability_score'].mean(),
            'vulnerability_distribution': vulnerability_df['vulnerability_score'].value_counts().to_dict(),
            'most_vulnerable_individuals': high_vulnerability.nlargest(5, 'vulnerability_score')[['full_name', 'vulnerability_score']].to_dict('records')
        }
        
        logger.info(f"   • High-need households: {indicators['high_need_analysis']['high_need_household_count']}")
        logger.info(f"   • High vulnerability individuals: {indicators['vulnerability_analysis']['high_vulnerability_count']}")
        
        return indicators
    
    def generate_recommendations(self) -> dict:
        """Generate actionable recommendations based on analysis"""
        logger.info("💡 Generating recommendations...")
        
        recommendations = {}
        
        # Service optimization recommendations
        service_patterns = self.analyze_service_patterns()
        
        # Peak service times
        peak_months = max(service_patterns['temporal_analysis']['services_by_month'], 
                         key=service_patterns['temporal_analysis']['services_by_month'].get)
        
        recommendations['service_optimization'] = [
            f"Peak service demand occurs in month {peak_months}. Consider increasing staffing and inventory during this period.",
            f"Food Pantry services represent the highest volume. Consider expanding pantry capacity.",
            f"Average of {service_patterns['service_frequency']['avg_services_per_person']:.1f} services per person suggests regular ongoing need.",
            "Implement appointment scheduling for high-traffic periods to reduce wait times."
        ]
        
        # Resource allocation recommendations
        demographics = self.analyze_demographics()
        avg_household = demographics['avg_household_size']
        
        recommendations['resource_allocation'] = [
            f"With average household size of {avg_household:.1f}, consider family-sized food packages as default.",
            "Focus outreach efforts on underrepresented geographic areas.",
            "Develop age-appropriate programs for identified demographic groups.",
            "Consider mobile food services for areas with lower access."
        ]
        
        # Program development recommendations
        indicators = self.identify_food_insecurity_indicators()
        high_vulnerability_pct = (indicators['vulnerability_analysis']['high_vulnerability_count'] / len(self.people_df)) * 100
        
        recommendations['program_development'] = [
            f"Develop targeted support for {indicators['vulnerability_analysis']['high_vulnerability_count']} high-vulnerability individuals ({high_vulnerability_pct:.1f}% of population).",
            "Create case management programs for households with vulnerability scores ≥ 4.",
            "Implement nutrition education programs alongside food distribution.",
            "Establish partnerships with local healthcare providers for holistic support."
        ]
        
        # Data and monitoring recommendations
        recommendations['data_monitoring'] = [
            "Standardize data collection across both database systems for better integration.",
            "Implement real-time dashboard monitoring for service delivery metrics.",
            "Create automated alerts for individuals showing increased service dependency.",
            "Establish monthly reporting cadence for stakeholder updates."
        ]
        
        logger.info(f"   • Generated {sum(len(v) for v in recommendations.values())} recommendations")
        
        return recommendations
    
    def create_visualizations(self):
        """Create key visualizations"""
        logger.info("📊 Creating visualizations...")
        
        os.makedirs('data/output/charts', exist_ok=True)
        
        # 1. Service Distribution by Type
        plt.figure(figsize=(10, 6))
        service_counts = self.services_df['service_type'].value_counts()
        plt.bar(service_counts.index, service_counts.values, color='skyblue')
        plt.title('Distribution of Service Types', fontsize=16, fontweight='bold')
        plt.xlabel('Service Type')
        plt.ylabel('Number of Services')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('data/output/charts/service_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Monthly Service Trends
        plt.figure(figsize=(10, 6))
        monthly_services = self.services_df['month'].value_counts().sort_index()
        plt.plot(monthly_services.index, monthly_services.values, marker='o', linewidth=3, markersize=8, color='green')
        plt.title('Monthly Service Trends', fontsize=16, fontweight='bold')
        plt.xlabel('Month')
        plt.ylabel('Number of Services')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('data/output/charts/monthly_trends.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Household Size Distribution
        plt.figure(figsize=(8, 6))
        household_dist = self.people_df['householdsize'].value_counts().sort_index()
        plt.bar(household_dist.index, household_dist.values, color='lightcoral')
        plt.title('Household Size Distribution', fontsize=16, fontweight='bold')
        plt.xlabel('Household Size')
        plt.ylabel('Number of Households')
        plt.tight_layout()
        plt.savefig('data/output/charts/household_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Food Distribution by Service Type
        plt.figure(figsize=(12, 6))
        food_by_service = self.services_df.groupby('service_type')['foodpounds'].sum().sort_values(ascending=True)
        plt.barh(food_by_service.index, food_by_service.values, color='orange')
        plt.title('Total Food Distribution by Service Type (lbs)', fontsize=16, fontweight='bold')
        plt.xlabel('Total Food Distributed (lbs)')
        plt.ylabel('Service Type')
        plt.tight_layout()
        plt.savefig('data/output/charts/food_by_service.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("   • Created 4 visualization charts")
        logger.info("   • Charts saved to data/output/charts/")
    
    def run_full_analysis(self) -> dict:
        """Execute complete analytics workflow"""
        logger.info("🚀 Starting comprehensive analytics...")
        
        start_time = datetime.now()
        
        # Run all analyses
        self.insights['demographics'] = self.analyze_demographics()
        self.insights['service_patterns'] = self.analyze_service_patterns()
        self.insights['food_insecurity_indicators'] = self.identify_food_insecurity_indicators()
        self.insights['recommendations'] = self.generate_recommendations()
        
        # Create visualizations
        self.create_visualizations()
        
        # Add metadata
        self.insights['analysis_metadata'] = {
            'analysis_timestamp': datetime.now().isoformat(),
            'data_period': f"{self.services_df['service_date'].min()} to {self.services_df['service_date'].max()}",
            'total_people_analyzed': len(self.people_df),
            'total_services_analyzed': len(self.services_df),
            'analysis_duration': str(datetime.now() - start_time)
        }
        
        # Save comprehensive report
        output_file = 'data/output/reports/comprehensive_analysis_report.json'
        with open(output_file, 'w') as f:
            json.dump(self.insights, f, indent=2, default=str)
        
        duration = datetime.now() - start_time
        
        logger.info("="*60)
        logger.info("✅ ANALYTICS COMPLETED!")
        logger.info("="*60)
        logger.info(f"📊 Analysis duration: {duration}")
        logger.info(f"📈 People analyzed: {len(self.people_df):,}")
        logger.info(f"📈 Services analyzed: {len(self.services_df):,}")
        logger.info(f"📄 Report saved to: {output_file}")
        logger.info(f"📊 Charts saved to: data/output/charts/")
        logger.info("="*60)
        
        return self.insights

if __name__ == "__main__":
    # Run comprehensive analytics
    analytics = HungerHubAnalytics()
    
    try:
        insights = analytics.run_full_analysis()
        print("\n🎉 Analytics completed successfully!")
        print("📊 Check data/output/reports/ for detailed analysis")
        print("📈 Check data/output/charts/ for visualizations")
        
    except Exception as e:
        print(f"\n💥 Analytics failed: {e}")
        print("📝 Check logs/analytics.log for detailed error information")
