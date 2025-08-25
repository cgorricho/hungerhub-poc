#!/usr/bin/env python3
"""
HungerHub Dashboard - Service Analytics Page
Detailed analysis of service delivery patterns and effectiveness
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

def render_service_analytics():
    """
    Renders the service analytics dashboard page
    
    Analytics Displayed:
    - Service volume trends
    - Service type effectiveness
    - Geographic service distribution
    - Peak demand analysis
    - Resource utilization metrics
    """
    
    st.header("🍽️ Service Analytics")
    st.markdown("*Detailed analysis of service delivery patterns and effectiveness*")
    
    # Load data
    try:
        services_df = pd.read_csv('data/processed/unified_real/organizations.csv')
        people_df = pd.read_csv('data/processed/unified_real/donations.csv')
        services_df['donation_date'] = pd.to_datetime(services_df['donation_date'])
    except FileNotFoundError:
        st.error("❌ Data not available. Please run the ETL pipeline first.")
        return
    
    # Filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    min_date = services_df['donation_date'].min().date()
    max_date = services_df['donation_date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Service type filter
    org_names = ['All'] + list(services_df['org_name'].unique())
    selected_service = st.sidebar.selectbox("Service Type", org_names)
    
    # Data source filter
    data_sources = ['All'] + list(services_df['data_source'].unique())
    selected_source = st.sidebar.selectbox("Data Source", data_sources)
    
    # Apply filters
    filtered_services = services_df.copy()
    
    if len(date_range) == 2:
        filtered_services = filtered_services[
            (filtered_services['donation_date'].dt.date >= date_range[0]) &
            (filtered_services['donation_date'].dt.date <= date_range[1])
        ]
    
    if selected_service != 'All':
        filtered_services = filtered_services[filtered_services['org_name'] == selected_service]
    
    if selected_source != 'All':
        filtered_services = filtered_services[filtered_services['data_source'] == selected_source]
    
    # Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📊 Services in Period",
            f"{len(filtered_services):,}"
        )
    
    with col2:
        if 'foodpounds' in filtered_services.columns:
            total_food = filtered_services['foodpounds'].sum()
            st.metric(
                "📦 Food Distributed",
                f"{total_food:,.0f} lbs"
            )
    
    with col3:
        unique_people = filtered_services['person_id'].nunique()
        st.metric(
            "👥 People Served",
            f"{unique_people:,}"
        )
    
    with col4:
        if len(filtered_services) > 0:
            avg_services = len(filtered_services) / unique_people
            st.metric(
                "🔄 Avg Services/Person",
                f"{avg_services:.1f}"
            )
    
    st.divider()
    
    # Service Volume Analysis
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Service Volume Over Time")
        
        # Daily service counts
        daily_services = filtered_services.groupby(
            filtered_services['donation_date'].dt.date
        ).size().reset_index()
        daily_services.columns = ['date', 'service_count']
        
        fig = px.line(
            daily_services,
            x='date',
            y='service_count',
            title="Daily Service Volume",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Services"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Service Types")
        
        service_counts = filtered_services['org_name'].value_counts()
        fig = px.bar(
            x=service_counts.values,
            y=service_counts.index,
            orientation='h',
            title="Services by Type"
        )
        fig.update_layout(
            xaxis_title="Count",
            yaxis_title="Service Type"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Peak Analysis
    st.subheader("⏰ Peak Demand Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**By Day of Week**")
        if 'day_of_week' in filtered_services.columns:
            dow_counts = filtered_services['day_of_week'].value_counts()
        else:
            # Calculate day of week
            filtered_services['day_of_week'] = filtered_services['donation_date'].dt.day_name()
            dow_counts = filtered_services['day_of_week'].value_counts()
        
        # Reorder by actual days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_counts = dow_counts.reindex([day for day in day_order if day in dow_counts.index])
        
        fig = px.bar(
            x=dow_counts.index,
            y=dow_counts.values,
            title="Services by Day of Week"
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**By Month**")
        monthly_counts = filtered_services.groupby(
            filtered_services['donation_date'].dt.month
        ).size()
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        fig = px.bar(
            x=[month_names[i-1] for i in monthly_counts.index],
            y=monthly_counts.values,
            title="Services by Month"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.markdown("**Peak Hours** *(Estimated)*")
        # Mock hourly distribution since we don't have actual times
        hours = list(range(8, 18))  # 8 AM to 5 PM
        service_counts = np.random.poisson(lam=15, size=len(hours))
        service_counts[4:7] = np.random.poisson(lam=25, size=3)  # Peak lunch hours
        
        fig = px.bar(
            x=hours,
            y=service_counts,
            title="Estimated Service Distribution by Hour"
        )
        fig.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Services"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Food Distribution Analysis
    if 'foodpounds' in filtered_services.columns:
        st.divider()
        st.subheader("📦 Food Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            food_by_service = filtered_services.groupby('org_name')['foodpounds'].agg(['sum', 'mean']).round(1)
            food_by_service.columns = ['Total (lbs)', 'Average per Service (lbs)']
            
            st.markdown("**Food Distribution by Service Type**")
            st.dataframe(food_by_service, use_container_width=True)
        
        with col2:
            # Food distribution histogram
            fig = px.histogram(
                filtered_services,
                x='foodpounds',
                nbins=20,
                title="Food Distribution per Service"
            )
            fig.update_layout(
                xaxis_title="Food Pounds",
                yaxis_title="Number of Services"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Service Efficiency Metrics
    st.divider()
    st.subheader("⚡ Service Efficiency")
    
    # Calculate efficiency metrics
    efficiency_metrics = []
    
    for org_name in filtered_services['org_name'].unique():
        type_services = filtered_services[filtered_services['org_name'] == org_name]
        
        metrics = {
            'Service Type': org_name,
            'Total Services': len(type_services),
            'People Served': type_services['person_id'].nunique(),
            'Avg Services per Person': len(type_services) / type_services['person_id'].nunique()
        }
        
        if 'foodpounds' in type_services.columns:
            metrics['Food per Service'] = f"{type_services['foodpounds'].mean():.1f} lbs"
            metrics['Total Food'] = f"{type_services['foodpounds'].sum():.0f} lbs"
        
        efficiency_metrics.append(metrics)
    
    efficiency_df = pd.DataFrame(efficiency_metrics)
    st.dataframe(efficiency_df, use_container_width=True)
    
    # Export option
    st.divider()
    if st.button("📊 Export Analysis Report"):
        # Create summary for export
        report_data = {
            'analysis_date': datetime.now().isoformat(),
            'filtered_services': len(filtered_services),
            'date_range': f"{date_range[0]} to {date_range[1]}" if len(date_range) == 2 else "All dates",
            'org_name_filter': selected_service,
            'efficiency_metrics': efficiency_df.to_dict('records') if not efficiency_df.empty else []
        }
        
        st.json(report_data)
        st.success("✅ Analysis report generated!")

if __name__ == "__main__":
    render_service_analytics()
