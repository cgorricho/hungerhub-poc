import streamlit as st
import pandas as pd
import os

st.title("Debug Test - Data Loading")

st.write("Current working directory:", os.getcwd())
st.write("Contents of current directory:", os.listdir('.'))

st.write("Looking for data files...")
donations_path = 'data/processed/unified_real/donations.csv'
orgs_path = 'data/processed/unified_real/organizations.csv'

st.write(f"Donations path: {donations_path}")
st.write(f"Organizations path: {orgs_path}")
st.write(f"Donations file exists: {os.path.exists(donations_path)}")
st.write(f"Organizations file exists: {os.path.exists(orgs_path)}")

try:
    donations_df = pd.read_csv(donations_path)
    organizations_df = pd.read_csv(orgs_path)
    st.success(f"✅ SUCCESS: Loaded {len(donations_df)} donations and {len(organizations_df)} organizations")
    st.write("Sample donation data:")
    st.dataframe(donations_df.head())
except Exception as e:
    st.error(f"❌ ERROR: {str(e)}")
    
    if os.path.exists('data'):
        st.write("Contents of data directory:")
        for root, dirs, files in os.walk('data'):
            st.write(f"  {root}: {files}")
    else:
        st.write("data directory does not exist")
