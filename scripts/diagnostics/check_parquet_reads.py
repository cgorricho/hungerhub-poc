#!/usr/bin/env python3
import sys
from pathlib import Path

try:
    import pandas as pd
except Exception as e:
    print(f"ERROR: pandas not available: {e}")
    sys.exit(1)

try:
    from src.utils.paths import get_data_dir
except Exception as e:
    print(f"ERROR: Cannot import get_data_dir from src.utils.paths: {e}")
    sys.exit(1)

REQUIRED_UNIFIED = [
    'unified_donation_flow.parquet',
    'view_donor_performance.parquet',
    'view_flow_stage_summary.parquet',
    'view_monthly_donation_trends.parquet',
    'view_storage_requirement_analysis.parquet',
]

REQUIRED_REAL = [
    'AMX_DONATION_HEADER.parquet',
    'AMX_DONATION_LINES.parquet',
    'ACBIDS_ARCHIVE.parquet',
    'ACSHARES.parquet',
]

def try_read(base: Path, fname: str):
    p = base / fname
    try:
        df = pd.read_parquet(p)
        print(f"OK: {p} -> rows={len(df):,} cols={list(df.columns)[:8]}{'...' if len(df.columns)>8 else ''}")
        return True
    except FileNotFoundError as e:
        print(f"MISSING: {p}")
    except Exception as e:
        print(f"ERROR reading {p}: {e}")
    return False

if __name__ == "__main__":
    print("[Diagnostic] Parquet read check for Streamlit enhanced app dependencies")
    base_unified = get_data_dir('processed/unified_real')
    base_real = get_data_dir('processed/real')
    print(f"Unified base: {base_unified}")
    print(f"Real base:    {base_real}")
    print("-- unified_real --")
    for f in REQUIRED_UNIFIED:
        try_read(base_unified, f)
    print("-- real --")
    for f in REQUIRED_REAL:
        try_read(base_real, f)
    print("-- Done.")

