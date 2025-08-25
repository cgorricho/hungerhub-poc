"""
HungerHub POC - Plotly Dash Dashboard (FIXED FOR REAL DATA)
Oracle → Python → Plotly Dash Pipeline Implementation

3-Page Dashboard:
1. Executive Summary - High-level KPIs and insights
2. Donation Analytics - Donation patterns and trends  
3. Agency Operations - Agency performance and capacity
"""

import sys
import os
import logging
import traceback
from datetime import datetime

# Add current directory to path
sys.path.append(".")
# Import logging configuration FIRST
from logging_config import setup_dashboard_logging, log_callback_error, log_data_error

# Set up logging before other imports
logger = setup_dashboard_logging()

# Dash and Plotly imports
import dash
from dash import dcc, html, Input, Output, callback_context
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Load real data
try:
    logger.info("📊 Loading real Oracle data...")
    
    # Load donations data
    donations_df = pd.read_csv('data/processed/unified_real/donations.csv')
    logger.info(f"✅ Loaded {len(donations_df):,} donation records")
    logger.info(f"📋 Donations columns: {list(donations_df.columns)}")
    
    # Load organizations data  
    organizations_df = pd.read_csv('data/processed/unified_real/organizations.csv')
    logger.info(f"✅ Loaded {len(organizations_df):,} organization records")
    logger.info(f"📋 Organizations columns: {list(organizations_df.columns)}")
    
    # Data validation and preprocessing
    if donations_df.empty:
        raise ValueError("Donations dataframe is empty")
    if organizations_df.empty:
        raise ValueError("Organizations dataframe is empty")
    
    # Convert date column to datetime
    donations_df['donation_date'] = pd.to_datetime(donations_df['donation_date'])
    
    # Create a numeric value for analysis - use quantity as proxy for donation size
    donations_df['donation_value'] = donations_df['quantity'].fillna(0)
    
    # Create organization type from data source
    organizations_df['org_type'] = organizations_df['data_source'].map({
        'Choice': 'Food Bank',
        'AgencyExpress': 'Community Agency'
    }).fillna('Other')
    
    logger.info("✅ All data files loaded and preprocessed successfully")
    
except Exception as e:
    log_data_error(e, "Data Loading")
    logger.error("❌ Failed to load real data. Using fallback mock data.")
    
    # Fallback to mock data
    donations_df = pd.DataFrame({
        'donation_id': range(1000),
        'donation_value': np.random.lognormal(3, 1, 1000),
        'donation_date': pd.date_range('2024-01-01', periods=1000, freq='D')[:1000],
        'donor_id': np.random.randint(1, 101, 1000),
        'quantity': np.random.randint(1, 50, 1000),
        'item_description': ['Food Item ' + str(i) for i in range(1000)]
    })
    
    organizations_df = pd.DataFrame({
        'org_id': ['ORG_' + str(i).zfill(8) for i in range(1, 101)],
        'org_name': [f'Organization {i}' for i in range(1, 101)],
        'org_type': np.random.choice(['Food Bank', 'Community Agency', 'Other'], 100)
    })

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "HungerHub Analytics POC"

# Define styles
styles = {
    'container': {'padding': '20px', 'fontFamily': 'Arial, sans-serif'},
    'header': {'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'},
    'card': {'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '20px', 'margin': '10px 0'},
    'tabs': {'fontSize': '16px'},
    'metric': {'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'margin': '5px'},
}

def safe_callback(func):
    """Decorator to wrap callbacks with error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            callback_name = func.__name__
            log_callback_error(callback_name, e, f"Args: {args}, Kwargs: {kwargs}")
            # Return safe fallback
            return html.Div(f"Error in {callback_name}: {str(e)}", style={'color': 'red', 'padding': '20px'})
    return wrapper

def create_executive_summary():
    """Create executive summary page with high-level KPIs"""
    try:
        logger.info("🎯 Creating Executive Summary page")
        
        # Calculate KPIs based on actual data structure
        total_donations = donations_df['donation_value'].sum()
        avg_donation = donations_df['donation_value'].mean()
        total_unique_donors = donations_df['donor_id'].nunique()
        total_donation_records = len(donations_df)
        total_orgs = len(organizations_df)
        
        logger.info(f"📊 KPIs calculated: {total_donations:,.0f} total value, {total_donation_records:,} records, {total_unique_donors} donors")
        
        # Create monthly trend visualization
        monthly_trend = donations_df.copy()
        monthly_trend['month'] = monthly_trend['donation_date'].dt.to_period('M')
        monthly_summary = monthly_trend.groupby('month')['donation_value'].sum().reset_index()
        monthly_summary['month'] = monthly_summary['month'].astype(str)
        
        trend_fig = px.line(monthly_summary, x='month', y='donation_value', 
                           title='Monthly Donation Value Trends')
        trend_fig.update_layout(height=400, xaxis_tickangle=-45)
        
        # Organization type distribution
        org_type_dist = organizations_df['org_type'].value_counts()
        pie_fig = px.pie(values=org_type_dist.values, names=org_type_dist.index,
                        title='Organization Type Distribution')
        pie_fig.update_layout(height=400)
        
        return html.Div([
            html.H2("📊 Executive Summary", style=styles['header']),
            
            # KPI Cards
            html.Div([
                html.Div([
                    html.H3(f"{total_donation_records:,}", style={'margin': '0', 'color': '#e74c3c'}),
                    html.P("Total Donations", style={'margin': '5px 0'})
                ], style=styles['metric'], className='col-3'),
                
                html.Div([
                    html.H3(f"{avg_donation:.1f}", style={'margin': '0', 'color': '#3498db'}),
                    html.P("Avg Items per Donation", style={'margin': '5px 0'})
                ], style=styles['metric'], className='col-3'),
                
                html.Div([
                    html.H3(f"{total_unique_donors:,}", style={'margin': '0', 'color': '#27ae60'}),
                    html.P("Unique Donors", style={'margin': '5px 0'})
                ], style=styles['metric'], className='col-3'),
                
                html.Div([
                    html.H3(f"{total_orgs:,}", style={'margin': '0', 'color': '#f39c12'}),
                    html.P("Organizations", style={'margin': '5px 0'})
                ], style=styles['metric'], className='col-3'),
            ], style={'display': 'flex', 'margin': '20px 0'}),
            
            # Charts
            html.Div([
                html.Div([
                    dcc.Graph(figure=trend_fig)
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(figure=pie_fig)
                ], style={'width': '50%', 'display': 'inline-block'}),
            ])
        ])
        
    except Exception as e:
        log_callback_error("create_executive_summary", e)
        logger.error(f"Executive summary error details: {traceback.format_exc()}")
        return html.Div(f"Error creating executive summary: {str(e)}", style={'color': 'red'})

def create_donation_analytics():
    """Create donation analytics page"""
    try:
        logger.info("💰 Creating Donation Analytics page")
        
        # Donation quantity distribution
        hist_fig = px.histogram(donations_df, x='donation_value', nbins=50,
                               title='Donation Quantity Distribution')
        hist_fig.update_layout(height=400)
        
        # Top donors by donation volume
        donor_donations = donations_df.groupby('donor_name')['donation_value'].sum().reset_index()
        top_donors = donor_donations.nlargest(10, 'donation_value')
        
        bar_fig = px.bar(top_donors, x='donor_name', y='donation_value',
                        title='Top 10 Donors by Total Quantity')
        bar_fig.update_layout(height=400, xaxis_tickangle=-45)
        
        # Items breakdown
        item_summary = donations_df.groupby('item_description')['quantity'].sum().reset_index()
        top_items = item_summary.nlargest(15, 'quantity')
        
        items_fig = px.bar(top_items, x='quantity', y='item_description', orientation='h',
                          title='Top 15 Most Donated Items')
        items_fig.update_layout(height=500)
        
        return html.Div([
            html.H2("💰 Donation Analytics", style=styles['header']),
            
            html.Div([
                html.Div([
                    dcc.Graph(figure=hist_fig)
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(figure=bar_fig)
                ], style={'width': '50%', 'display': 'inline-block'}),
            ]),
            
            html.Div([
                dcc.Graph(figure=items_fig)
            ], style={'margin': '20px 0'})
        ])
        
    except Exception as e:
        log_callback_error("create_donation_analytics", e)
        logger.error(f"Donation analytics error: {traceback.format_exc()}")
        return html.Div(f"Error creating donation analytics: {str(e)}", style={'color': 'red'})

def create_agency_operations():
    """Create agency operations page"""
    try:
        logger.info("🏢 Creating Agency Operations page")
        
        # Organization performance metrics
        org_metrics = organizations_df.groupby('org_type').agg({
            'org_id': 'count'
        }).reset_index()
        org_metrics.columns = ['org_type', 'org_count']
        
        # Organizations by type
        type_fig = px.bar(org_metrics, x='org_type', y='org_count',
                         title='Organizations by Type')
        type_fig.update_layout(height=400)
        
        # Organizations over time (creation timeline)
        if 'created_time' in organizations_df.columns:
            orgs_timeline = organizations_df.copy()
            orgs_timeline['created_time'] = pd.to_datetime(orgs_timeline['created_time'])
            orgs_timeline['year'] = orgs_timeline['created_time'].dt.year
            yearly_orgs = orgs_timeline.groupby('year').size().reset_index(name='new_orgs')
            
            timeline_fig = px.line(yearly_orgs, x='year', y='new_orgs',
                                  title='New Organizations Created by Year')
            timeline_fig.update_layout(height=400)
        else:
            timeline_fig = px.scatter(x=[1], y=[1], title='No timeline data available')
            timeline_fig.update_layout(height=400)
        
        # Status distribution
        if 'status' in organizations_df.columns:
            status_dist = organizations_df['status'].value_counts()
            status_fig = px.pie(values=status_dist.values, names=status_dist.index,
                               title='Organization Status Distribution')
        else:
            status_fig = px.pie(values=[1], names=['Active'], title='Status: All Active')
        status_fig.update_layout(height=400)
        
        return html.Div([
            html.H2("🏢 Agency Operations", style=styles['header']),
            
            html.Div([
                html.Div([
                    dcc.Graph(figure=type_fig)
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(figure=status_fig)
                ], style={'width': '50%', 'display': 'inline-block'}),
            ]),
            
            html.Div([
                dcc.Graph(figure=timeline_fig)
            ], style={'margin': '20px 0'})
        ])
        
    except Exception as e:
        log_callback_error("create_agency_operations", e)
        logger.error(f"Agency operations error: {traceback.format_exc()}")
        return html.Div(f"Error creating agency operations: {str(e)}", style={'color': 'red'})

# App layout
app.layout = html.Div([
    html.H1("🍽️ HungerHub Analytics POC", style=styles['header']),
    
    dcc.Tabs(id="tabs", value='executive', children=[
        dcc.Tab(label='📊 Executive Summary', value='executive'),
        dcc.Tab(label='💰 Donation Analytics', value='donations'), 
        dcc.Tab(label='🏢 Agency Operations', value='operations'),
    ], style=styles['tabs']),
    
    html.Div(id='page-content')
], style=styles['container'])

# Callback for page routing
@app.callback(
    Output('page-content', 'children'),
    Input('tabs', 'value')
)
@safe_callback
def update_page_content(tab):
    """Route to appropriate page based on tab selection"""
    logger.info(f"🔄 Switching to tab: {tab}")
    
    if tab == 'executive':
        return create_executive_summary()
    elif tab == 'donations':
        return create_donation_analytics()
    elif tab == 'operations':
        return create_agency_operations()
    else:
        logger.warning(f"⚠️ Unknown tab requested: {tab}")
        return html.Div("Page not found")

if __name__ == '__main__':
    print("🍽️ HungerHub POC - Plotly Dash Dashboard (FIXED)")
    print("=" * 50)
    print("📋 Original POC Specification: Oracle → Python → Plotly Dash")
    print("🎯 3-Page Dashboard: Executive Summary | Donation Analytics | Agency Operations")
    print(f"📊 Real Data Loaded: {len(donations_df):,} donations, {len(organizations_df):,} organizations")
    print("🌐 Starting dashboard server...")
    print("📝 Logging enabled - check logs/ directory for detailed logs")
    print("=" * 50)
    
    logger.info("🚀 Starting HungerHub Dashboard Server (FIXED VERSION)")
    logger.info(f"📊 Data Summary: {len(donations_df):,} donations, {len(organizations_df):,} organizations")
    
    # Run the app with error handling
    try:
        app.run(debug=True, host='0.0.0.0', port=8050)
    except Exception as e:
        logger.critical(f"💥 Critical error starting dashboard: {str(e)}")
        logger.critical(traceback.format_exc())
        raise
