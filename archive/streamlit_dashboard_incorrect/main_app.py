#!/usr/bin/env python3
"""
HungerHub POC - Main Streamlit Dashboard Application
Comprehensive food security analytics and intervention management
"""

import streamlit as st
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import page modules
from dashboard.pages.executive_summary import render_executive_summary
from dashboard.pages.service_analytics import render_service_analytics
from dashboard.pages.vulnerability_assessment import render_vulnerability_assessment
from dashboard.pages.resource_optimization import render_resource_optimization

def main():
    """Main Streamlit application with multi-page navigation"""
    
    # Page configuration
    st.set_page_config(
        page_title="HungerHub Analytics POC",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        text-align: center;
    }
    .main-header p {
        color: #E8F4FD;
        margin: 0.5rem 0 0 0;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2E86AB;
    }
    .stSelectbox > div > div {
        background-color: #F8F9FA;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Application header
    st.markdown("""
    <div class="main-header">
        <h1>🍽️ HungerHub Analytics POC</h1>
        <p>Comprehensive Food Security Analytics & Intervention Management Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("📊 Navigation")
    st.sidebar.markdown("---")
    
    # Page selection
    page_options = {
        "🏠 Executive Summary": "executive_summary",
        "📈 Service Analytics": "service_analytics", 
        "⚠️ Vulnerability Assessment": "vulnerability_assessment",
        "⚡ Resource Optimization": "resource_optimization"
    }
    
    selected_page = st.sidebar.selectbox(
        "Select Dashboard Page:",
        options=list(page_options.keys()),
        index=0
    )
    
    # System status check
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 System Status")
    
    # Check for data availability
    data_files = [
        'data/processed/unified/people.csv',
        'data/processed/unified/services.csv'
    ]
    
    data_status = all(os.path.exists(file) for file in data_files)
    
    if data_status:
        st.sidebar.success("✅ Data Available")
    else:
        st.sidebar.error("❌ Data Missing")
        st.sidebar.info("Run ETL pipeline first")
    
    # Quick stats in sidebar
    if data_status:
        try:
            import pandas as pd
            people_df = pd.read_csv('data/processed/unified/people.csv')
            services_df = pd.read_csv('data/processed/unified/services.csv')
            
            st.sidebar.markdown("### 📊 Quick Stats")
            st.sidebar.metric("Total People", len(people_df))
            st.sidebar.metric("Total Services", len(services_df))
            st.sidebar.metric("Active Locations", services_df['service_location'].nunique())
            
        except Exception as e:
            st.sidebar.warning(f"Data loading issue: {str(e)[:50]}...")
    
    # Help section
    st.sidebar.markdown("---")
    with st.sidebar.expander("ℹ️ Help & Info"):
        st.markdown("""
        **Dashboard Navigation:**
        - **Executive Summary**: High-level KPIs and alerts
        - **Service Analytics**: Detailed service patterns and demographics
        - **Vulnerability Assessment**: Risk scoring and intervention priorities  
        - **Resource Optimization**: Capacity planning and efficiency analysis
        
        **Data Sources:**
        - Oracle Choice Database
        - Oracle AgencyExpress Database
        - Processed through ETL pipeline
        
        **For Support:**
        - Check logs/ directory for error details
        - Review docs/technical/ for troubleshooting
        """)
    
    # Main content area
    page_key = page_options[selected_page]
    
    # Route to selected page
    if page_key == "executive_summary":
        render_executive_summary()
    elif page_key == "service_analytics":
        render_service_analytics()
    elif page_key == "vulnerability_assessment":
        render_vulnerability_assessment()
    elif page_key == "resource_optimization":
        render_resource_optimization()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown("**HungerHub POC** - Food Security Analytics Platform")
    
    with col2:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.experimental_rerun()
    
    with col3:
        st.markdown(f"*Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*")

if __name__ == "__main__":
    main()
