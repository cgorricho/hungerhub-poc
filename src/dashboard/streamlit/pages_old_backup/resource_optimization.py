#!/usr/bin/env python3
"""
HungerHub Dashboard - Resource Optimization Page
Inventory management and distribution efficiency analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

def calculate_resource_metrics(services_df):
    """Calculate key resource optimization metrics"""
    metrics = {}
    
    # Service efficiency metrics
    metrics['total_services'] = len(services_df)
    metrics['unique_people'] = services_df['person_id'].nunique()
    metrics['avg_services_per_person'] = metrics['total_services'] / metrics['unique_people'] if metrics['unique_people'] > 0 else 0
    
    # Temporal patterns
    services_df['donation_date'] = pd.to_datetime(services_df['donation_date'])
    services_df['day_of_week'] = services_df['donation_date'].dt.day_name()
    services_df['hour'] = services_df['donation_date'].dt.hour
    
    # Geographic distribution
    location_counts = services_df['service_location'].value_counts()
    metrics['busiest_location'] = location_counts.index[0] if len(location_counts) > 0 else 'Unknown'
    metrics['location_utilization'] = location_counts.to_dict()
    
    return metrics

def render_resource_optimization():
    """
    Renders the resource optimization dashboard page
    
    Optimization Features:
    - Service delivery efficiency analysis
    - Location utilization metrics
    - Temporal demand patterns
    - Capacity planning recommendations
    - Resource allocation optimization
    """
    
    st.header("⚡ Resource Optimization")
    st.markdown("*Inventory management and distribution efficiency analysis*")
    
    # Load data
    try:
        people_df = pd.read_csv('data/processed/unified_real/donations.csv')
        services_df = pd.read_csv('data/processed/unified_real/organizations.csv')
        services_df['donation_date'] = pd.to_datetime(services_df['donation_date'])
    except FileNotFoundError:
        st.error("❌ Data not available. Please run the ETL pipeline first.")
        return
    
    # Calculate optimization metrics
    metrics = calculate_resource_metrics(services_df)
    
    # Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 Service Efficiency",
            f"{metrics['avg_services_per_person']:.1f}",
            delta="Avg services per person"
        )
    
    with col2:
        unique_locations = services_df['service_location'].nunique()
        st.metric(
            "📍 Active Locations",
            unique_locations,
            delta=f"Serving {metrics['unique_people']} people"
        )
    
    with col3:
        services_per_day = len(services_df) / services_df['donation_date'].dt.date.nunique()
        st.metric(
            "📊 Daily Service Volume",
            f"{services_per_day:.0f}",
            delta="Average per day"
        )
    
    with col4:
        peak_location_services = max(metrics['location_utilization'].values()) if metrics['location_utilization'] else 0
        st.metric(
            "🔥 Peak Location Load",
            peak_location_services,
            delta=f"At {metrics['busiest_location']}"
        )
    
    st.divider()
    
    # Service Distribution Analysis
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📍 Location Performance Analysis")
        
        # Create location performance dataframe
        location_stats = services_df.groupby('service_location').agg({
            'person_id': ['count', 'nunique'],
            'donation_date': ['min', 'max']
        }).round(2)
        
        location_stats.columns = ['Total Services', 'Unique People', 'First Service', 'Last Service']
        location_stats['Services per Person'] = (location_stats['Total Services'] / 
                                               location_stats['Unique People']).round(2)
        location_stats['Days Active'] = (pd.to_datetime(location_stats['Last Service']) - 
                                       pd.to_datetime(location_stats['First Service'])).dt.days + 1
        location_stats['Services per Day'] = (location_stats['Total Services'] / 
                                            location_stats['Days Active']).round(2)
        
        location_stats = location_stats.sort_values('Total Services', ascending=False).reset_index()
        
        # Color coding for performance
        def color_performance(val, column):
            if column == 'Services per Day':
                if val >= 10:
                    return 'background-color: #d1f2eb'
                elif val >= 5:
                    return 'background-color: #fff3cd'
                else:
                    return 'background-color: #ffcdd2'
            return ''
        
        styled_df = location_stats.style.applymap(
            lambda x: color_performance(x, 'Services per Day'), 
            subset=['Services per Day']
        )
        st.dataframe(styled_df, use_container_width=True)
    
    with col2:
        st.subheader("🏆 Location Rankings")
        
        # Top performing locations
        st.markdown("**By Total Volume**")
        top_volume = location_stats.head(3)[['service_location', 'Total Services']]
        for idx, row in top_volume.iterrows():
            st.metric(f"#{idx+1}", row['service_location'], f"{row['Total Services']} services")
        
        st.markdown("**By Efficiency (Services/Day)**")
        top_efficiency = location_stats.nlargest(3, 'Services per Day')[['service_location', 'Services per Day']]
        for idx, (_, row) in enumerate(top_efficiency.iterrows()):
            st.metric(f"#{idx+1}", row['service_location'], f"{row['Services per Day']:.1f}/day")
    
    # Temporal Analysis
    st.divider()
    st.subheader("⏰ Temporal Demand Patterns")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Daily Distribution**")
        
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = services_df.groupby('day_of_week').size().reindex(day_order, fill_value=0)
        
        fig = px.bar(
            x=day_counts.index,
            y=day_counts.values,
            title="Services by Day of Week",
            color=day_counts.values,
            color_continuous_scale='viridis'
        )
        fig.update_layout(
            xaxis_title="Day of Week",
            yaxis_title="Number of Services",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Hourly Patterns**")
        
        hour_counts = services_df.groupby('hour').size()
        
        fig = px.line(
            x=hour_counts.index,
            y=hour_counts.values,
            title="Services by Hour of Day",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Hour (24h format)",
            yaxis_title="Number of Services"
        )
        fig.add_hrect(y0=hour_counts.mean()-hour_counts.std(), 
                     y1=hour_counts.mean()+hour_counts.std(),
                     annotation_text="Normal Range", 
                     fillcolor="lightblue", opacity=0.2)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**Monthly Trends**")
        
        services_df['month'] = services_df['donation_date'].dt.to_period('M')
        month_counts = services_df.groupby('month').size()
        
        fig = px.area(
            x=[str(m) for m in month_counts.index],
            y=month_counts.values,
            title="Service Volume by Month"
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Number of Services"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Capacity Planning
    st.divider()
    st.subheader("📈 Capacity Planning & Forecasting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Location Capacity Analysis**")
        
        # Calculate capacity utilization (assuming max capacity)
        max_daily_capacity = st.slider(
            "Assumed Max Daily Capacity per Location", 
            min_value=10, max_value=100, value=50, step=5
        )
        
        location_stats['Capacity Utilization %'] = (
            location_stats['Services per Day'] / max_daily_capacity * 100
        ).round(1)
        
        # Capacity status
        def get_capacity_status(utilization):
            if utilization >= 90:
                return "🔴 Over Capacity"
            elif utilization >= 70:
                return "🟡 High Utilization"
            elif utilization >= 40:
                return "🟢 Optimal"
            else:
                return "⚪ Under Utilized"
        
        location_stats['Status'] = location_stats['Capacity Utilization %'].apply(get_capacity_status)
        
        capacity_display = location_stats[['service_location', 'Services per Day', 
                                         'Capacity Utilization %', 'Status']]
        st.dataframe(capacity_display, use_container_width=True)
    
    with col2:
        st.markdown("**Demand Forecasting**")
        
        # Simple trend analysis
        daily_services = services_df.groupby(services_df['donation_date'].dt.date).size()
        daily_services.index = pd.to_datetime(daily_services.index)
        
        # Calculate trend
        x_days = np.arange(len(daily_services))
        trend_coef = np.polyfit(x_days, daily_services.values, 1)
        trend_line = np.poly1d(trend_coef)(x_days)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_services.index,
            y=daily_services.values,
            mode='lines+markers',
            name='Actual Services',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=daily_services.index,
            y=trend_line,
            mode='lines',
            name='Trend Line',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title="Service Volume Trend Analysis",
            xaxis_title="Date",
            yaxis_title="Daily Services"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend interpretation
        daily_change = trend_coef[0]
        if daily_change > 0.1:
            st.info(f"📈 **Growing Demand:** +{daily_change:.2f} services/day trend")
        elif daily_change < -0.1:
            st.warning(f"📉 **Declining Demand:** {daily_change:.2f} services/day trend")
        else:
            st.success(f"➡️ **Stable Demand:** {abs(daily_change):.2f} services/day variation")
    
    # Resource Allocation Optimization
    st.divider()
    st.subheader("🎯 Resource Allocation Recommendations")
    
    # Generate recommendations based on analysis
    recommendations = []
    
    # Location-based recommendations
    over_capacity = location_stats[location_stats['Capacity Utilization %'] >= 90]
    under_utilized = location_stats[location_stats['Capacity Utilization %'] < 40]
    
    if len(over_capacity) > 0:
        for _, loc in over_capacity.iterrows():
            recommendations.append({
                'Priority': '🔴 High',
                'Category': 'Capacity',
                'Recommendation': f"Expand capacity at {loc['service_location']} - currently at {loc['Capacity Utilization %']:.1f}% utilization",
                'Impact': 'Immediate'
            })
    
    if len(under_utilized) > 0:
        for _, loc in under_utilized.iterrows():
            recommendations.append({
                'Priority': '🟡 Medium',
                'Category': 'Efficiency',
                'Recommendation': f"Optimize resources at {loc['service_location']} - only {loc['Capacity Utilization %']:.1f}% utilized",
                'Impact': 'Cost Savings'
            })
    
    # Temporal recommendations
    peak_day = services_df['day_of_week'].value_counts().index[0]
    peak_hour = services_df['hour'].value_counts().index[0]
    
    recommendations.append({
        'Priority': '🟢 Low',
        'Category': 'Scheduling',
        'Recommendation': f"Peak demand on {peak_day} at {peak_hour}:00 - consider staff scheduling optimization",
        'Impact': 'Service Quality'
    })
    
    # Geographic coverage
    state_coverage = people_df['state'].nunique()
    service_states = services_df.merge(people_df, on='person_id')['state'].nunique()
    
    if service_states < state_coverage:
        recommendations.append({
            'Priority': '🟡 Medium',
            'Category': 'Coverage',
            'Recommendation': f"Expand service coverage - currently serving {service_states}/{state_coverage} states",
            'Impact': 'Reach'
        })
    
    # Display recommendations
    if recommendations:
        rec_df = pd.DataFrame(recommendations)
        
        # Color coding by priority
        def color_priority(val):
            if '🔴' in val:
                return 'background-color: #ffcdd2'
            elif '🟡' in val:
                return 'background-color: #fff3cd'
            else:
                return 'background-color: #d1f2eb'
        
        styled_rec = rec_df.style.applymap(color_priority, subset=['Priority'])
        st.dataframe(styled_rec, use_container_width=True)
    else:
        st.success("✅ All resources appear optimally allocated!")
    
    # Performance Metrics Summary
    st.divider()
    st.subheader("📊 Performance Metrics Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Efficiency Metrics**")
        
        efficiency_metrics = {
            'Average Services per Person': f"{metrics['avg_services_per_person']:.2f}",
            'Location Utilization Rate': f"{(len([l for l in location_stats['Capacity Utilization %'] if l >= 40]) / len(location_stats) * 100):.1f}%",
            'Peak Day Coverage': f"{peak_day} ({services_df[services_df['day_of_week'] == peak_day].shape[0]} services)",
            'Geographic Reach': f"{service_states} states, {services_df['service_location'].nunique()} locations"
        }
        
        for metric, value in efficiency_metrics.items():
            st.metric(metric, value)
    
    with col2:
        st.markdown("**Optimization Opportunities**")
        
        opportunities = {
            'Over-Capacity Locations': len(over_capacity),
            'Under-Utilized Locations': len(under_utilized),
            'High-Priority Actions': len([r for r in recommendations if '🔴' in r.get('Priority', '')]),
            'Potential Cost Savings': f"{len(under_utilized) * 20}% resource reallocation"
        }
        
        for opportunity, value in opportunities.items():
            st.metric(opportunity, value)
    
    # Export functionality
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Optimization Report"):
            optimization_report = {
                'report_date': datetime.now().isoformat(),
                'summary_metrics': metrics,
                'location_performance': location_stats.to_dict('records'),
                'recommendations': recommendations,
                'capacity_analysis': {
                    'over_capacity_locations': len(over_capacity),
                    'under_utilized_locations': len(under_utilized),
                    'average_utilization': location_stats['Capacity Utilization %'].mean()
                }
            }
            st.json(optimization_report)
            st.success("✅ Optimization report generated!")
    
    with col2:
        if st.button("📈 Generate Capacity Planning Report"):
            capacity_report = {
                'current_capacity_analysis': location_stats[['service_location', 'Services per Day', 'Capacity Utilization %']].to_dict('records'),
                'demand_forecast': {
                    'daily_trend': daily_change,
                    'peak_periods': {
                        'day': peak_day,
                        'hour': f"{peak_hour}:00"
                    }
                },
                'expansion_recommendations': [r for r in recommendations if r['Category'] == 'Capacity']
            }
            st.json(capacity_report)
            st.success("✅ Capacity planning report generated!")

if __name__ == "__main__":
    render_resource_optimization()
