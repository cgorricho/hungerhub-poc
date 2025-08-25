import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Set page config
st.set_page_config(page_title="HungerHub Analytics", page_icon="🍽️", layout="wide")

# Title
st.title("🍽️ HungerHub Analytics Dashboard")
st.markdown("**Real Oracle Data Analysis - Food Security & Distribution**")

# Load real data - using absolute paths
project_root = "/home/tagazureuser/cgorr/2week_poc_execution/hungerhub_poc"
donations_path = os.path.join(project_root, "data/processed/unified_real/donations.csv")
orgs_path = os.path.join(project_root, "data/processed/unified_real/organizations.csv")

try:
    donations_df = pd.read_csv(donations_path)
    organizations_df = pd.read_csv(orgs_path)
    st.success(f"✅ **Real Oracle Data Loaded**: {len(donations_df):,} donations, {len(organizations_df):,} organizations")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Main dashboard
st.header("📊 Key Metrics")

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Donations", f"{len(donations_df):,}")
with col2:
    st.metric("Organizations", f"{len(organizations_df):,}")
with col3:
    st.metric("Total Quantity", f"{donations_df['quantity'].sum():,}")
with col4:
    st.metric("Unique Donors", donations_df['donor_name'].nunique())

# Charts section
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Donors by Quantity")
    top_donors = donations_df.groupby('donor_name')['quantity'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(x=top_donors.values, y=top_donors.index, orientation='h', 
                 title="Top Donors", labels={'x': 'Total Quantity', 'y': 'Donor'})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Donations by Source")
    source_counts = donations_df['source_database'].value_counts()
    fig = px.pie(values=source_counts.values, names=source_counts.index, 
                 title="Data Sources")
    st.plotly_chart(fig, use_container_width=True)

# Data tables
st.header("📋 Data Preview")
tab1, tab2 = st.tabs(["Donations", "Organizations"])

with tab1:
    st.subheader("Recent Donations")
    st.dataframe(donations_df.head(10), use_container_width=True)
    
with tab2:
    st.subheader("Organizations")
    st.dataframe(organizations_df.head(10), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("🔄 **Data Source**: Oracle Choice & Agency Databases | **Last Updated**: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
