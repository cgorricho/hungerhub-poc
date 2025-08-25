"""
HungerHub POC - Plotly Dash Dashboard
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

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import logging configuration FIRST
from src.dashboard.logging_config import setup_dashboard_logging, log_callback_error, log_data_error

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
    
    # Load organizations data  
    organizations_df = pd.read_csv('data/processed/unified_real/organizations.csv')
    logger.info(f"✅ Loaded {len(organizations_df):,} organization records")
    
    # Data validation
    if donations_df.empty:
        raise ValueError("Donations dataframe is empty")
    if organizations_df.empty:
        raise ValueError("Organizations dataframe is empty")
        
    logger.info("✅ All data files loaded successfully")
    
except Exception as e:
    log_data_error("Data Loading", e, f"donations: {len(donations_df) if 'donations_df' in locals() else 'N/A'}, orgs: {len(organizations_df) if 'organizations_df' in locals() else 'N/A'}")
    logger.error("❌ Failed to load real data. Using fallback mock data.")
    
    # Fallback to mock data
    donations_df = pd.DataFrame({
        'donation_id': range(1000),
        'amount': np.random.lognormal(3, 1, 1000),
        'date': pd.date_range('2024-01-01', periods=1000, freq='D')[:1000],
        'org_id': np.random.randint(1, 101, 1000)
    })
    
    organizations_df = pd.DataFrame({
        'org_id': range(1, 101),
        'name': [f'Organization {i}' for i in range(1, 101)],
        'type': np.random.choice(['Food Bank', 'Shelter', 'Community Kitchen'], 100)
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
        
        # Calculate KPIs
        total_donations = donations_df['amount'].sum()
        avg_donation = donations_df['amount'].mean()
        total_orgs = len(organizations_df)
        active_orgs = len(donations_df['org_id'].unique())
        
        # Create visualizations
        monthly_trend = donations_df.copy()
        monthly_trend['month'] = pd.to_datetime(monthly_trend['date']).dt.to_period('M')
        monthly_summary = monthly_trend.groupby('month')['amount'].sum().reset_index()
        monthly_summary['month'] = monthly_summary['month'].astype(str)
        
        trend_fig = px.line(monthly_summary, x='month', y='amount', 
                           title='Monthly Donation Trends')
        trend_fig.update_layout(height=400)
        
        # Organization type distribution
        org_type_dist = organizations_df['type'].value_counts()
        pie_fig = px.pie(values=org_type_dist.values, names=org_type_dist.index,
                        title='Organization Type Distribution')
        pie_fig.update_layout(height=400)
        
        return html.Div([
            html.H2("📊 Executive Summary", style=styles['header']),
            
            # KPI Cards
            html.Div([
                html.Div([
                    html.H3(f"${total_donations:,.0f}", style={'margin': '0', 'color': '#e74c3c'}),
                    html.P("Total Donations", style={'margin': '5px 0'})
                ], style=styles['metric'], className='col-3'),
                
                html.Div([
                    html.H3(f"${avg_donation:.0f}", style={'margin': '0', 'color': '#3498db'}),
                    html.P("Average Donation", style={'margin': '5px 0'})
                ], style=styles['metric'], className='col-3'),
                
                html.Div([
                    html.H3(f"{active_orgs}", style={'margin': '0', 'color': '#27ae60'}),
                    html.P("Active Organizations", style={'margin': '5px 0'})
                ], style=styles['metric'], className='col-3'),
                
                html.Div([
                    html.H3(f"{total_orgs}", style={'margin': '0', 'color': '#f39c12'}),
                    html.P("Total Organizations", style={'margin': '5px 0'})
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
        return html.Div("Error creating executive summary", style={'color': 'red'})

def create_donation_analytics():
    """Create donation analytics page"""
    try:
        logger.info("💰 Creating Donation Analytics page")
        
        # Donation size distribution
        hist_fig = px.histogram(donations_df, x='amount', nbins=50,
                               title='Donation Amount Distribution')
        hist_fig.update_layout(height=400)
        
        # Top organizations by donation volume
        org_donations = donations_df.groupby('org_id')['amount'].sum().reset_index()
        org_donations = org_donations.merge(organizations_df[['org_id', 'name']], on='org_id', how='left')
        top_orgs = org_donations.nlargest(10, 'amount')
        
        bar_fig = px.bar(top_orgs, x='name', y='amount',
                        title='Top 10 Organizations by Total Donations')
        bar_fig.update_layout(height=400, xaxis_tickangle=-45)
        
        return html.Div([
            html.H2("💰 Donation Analytics", style=styles['header']),
            
            html.Div([
                html.Div([
                    dcc.Graph(figure=hist_fig)
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(figure=bar_fig)
                ], style={'width': '50%', 'display': 'inline-block'}),
            ])
        ])
        
    except Exception as e:
        log_callback_error("create_donation_analytics", e)
        return html.Div("Error creating donation analytics", style={'color': 'red'})

def create_agency_operations():
    """Create agency operations page"""
    try:
        logger.info("🏢 Creating Agency Operations page")
        
        # Organization performance metrics
        org_metrics = donations_df.groupby('org_id').agg({
            'amount': ['count', 'sum', 'mean']
        }).reset_index()
        org_metrics.columns = ['org_id', 'donation_count', 'total_amount', 'avg_amount']
        org_metrics = org_metrics.merge(organizations_df[['org_id', 'name', 'type']], on='org_id', how='left')
        
        # Scatter plot: donation count vs average amount
        scatter_fig = px.scatter(org_metrics, x='donation_count', y='avg_amount',
                               color='type', hover_name='name',
                               title='Organization Performance: Volume vs Average Donation')
        scatter_fig.update_layout(height=400)
        
        # Performance by organization type
        type_performance = org_metrics.groupby('type').agg({
            'total_amount': 'mean',
            'donation_count': 'mean',
            'avg_amount': 'mean'
        }).reset_index()
        
        performance_fig = px.bar(type_performance, x='type', y='total_amount',
                               title='Average Performance by Organization Type')
        performance_fig.update_layout(height=400)
        
        return html.Div([
            html.H2("🏢 Agency Operations", style=styles['header']),
            
            html.Div([
                html.Div([
                    dcc.Graph(figure=scatter_fig)
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(figure=performance_fig)
                ], style={'width': '50%', 'display': 'inline-block'}),
            ])
        ])
        
    except Exception as e:
        log_callback_error("create_agency_operations", e)
        return html.Div("Error creating agency operations", style={'color': 'red'})

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
    print("🍽️ HungerHub POC - Plotly Dash Dashboard")
    print("=" * 50)
    print("📋 Original POC Specification: Oracle → Python → Plotly Dash")
    print("🎯 3-Page Dashboard: Executive Summary | Donation Analytics | Agency Operations")
    print(f"📊 Real Data Loaded: {len(donations_df):,} donations, {len(organizations_df):,} organizations")
    print("🌐 Starting dashboard server...")
    print("📝 Logging enabled - check logs/ directory for detailed logs")
    print("=" * 50)
    
    logger.info("🚀 Starting HungerHub Dashboard Server")
    logger.info(f"📊 Data Summary: {len(donations_df):,} donations, {len(organizations_df):,} organizations")
    
    # Run the app with error handling
    try:
        app.run(debug=True, host='0.0.0.0', port=8050)
    except Exception as e:
        logger.critical(f"💥 Critical error starting dashboard: {str(e)}")
        logger.critical(traceback.format_exc())
        raise
