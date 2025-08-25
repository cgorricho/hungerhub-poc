"""
Data adapter for Streamlit dashboard
Handles data loading and adaptation for the Streamlit app.
Policy: No synthetic/mock data generation. Fail fast with clear guidance if data is unavailable.
"""
from typing import Tuple, Optional
import pandas as pd
import streamlit as st
from pathlib import Path
from src.utils.paths import get_data_dir


def _read_table_parquet_first(file_stem: str) -> pd.DataFrame:
    """Read a table from unified_real with parquet-first strategy, fallback to CSV.
    Raises FileNotFoundError if neither exists.
    """
    data_dir = get_data_dir('processed/unified_real')
    parquet_path = data_dir / f"{file_stem}.parquet"
    csv_path = data_dir / f"{file_stem}.csv"

    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if csv_path.exists():
        st.warning(f"Using CSV fallback for {file_stem} at {csv_path}")
        return pd.read_csv(csv_path)

    raise FileNotFoundError(f"Neither parquet nor CSV found for {file_stem} under {data_dir}")


def load_and_adapt_data() -> Tuple[pd.DataFrame, pd.DataFrame, bool]:
    """Load real unified data and adapt it for Streamlit dashboard.

    Returns: (services_df, people_df, is_real_data)
    """
    try:
        donations_df = _read_table_parquet_first('donations')
        organizations_df = _read_table_parquet_first('organizations')

        # Adapt donations as services data
        services_df = donations_df.rename(columns={
            'donation_date': 'service_date',
            'item_description': 'service_type',
            'donor_name': 'client_name',
            'quantity': 'amount'
        }).copy()

        # Adapt organizations as people data
        people_df = organizations_df.rename(columns={
            'org_name': 'client_name',
            'created_time': 'registration_date'
        }).copy()

        # Ensure datetime types where applicable
        if 'service_date' in services_df.columns:
            services_df['service_date'] = pd.to_datetime(services_df['service_date'], errors='coerce')
        if 'registration_date' in people_df.columns:
            people_df['registration_date'] = pd.to_datetime(people_df['registration_date'], errors='coerce')

        return services_df, people_df, True

    except Exception as e:
        st.error(
            "Real data could not be loaded. Please ensure unified datasets exist under "
            f"{get_data_dir('processed/unified_real')} (expected donations/organizations in parquet or CSV).\n"
            f"Error: {e}"
        )
        # Fail-fast: do not simulate
        return pd.DataFrame(), pd.DataFrame(), False
