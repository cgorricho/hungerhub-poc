#!/usr/bin/env python3
import sys
from pathlib import Path
from pprint import pprint

try:
    from src.utils.paths import get_data_dir
except Exception as e:
    print(f"ERROR: Cannot import get_data_dir from src.utils.paths: {e}")
    sys.exit(1)

EXPECTED_UNIFIED_FILES = [
    'unified_donation_flow.parquet',
    'view_donor_performance.parquet',
    'view_flow_stage_summary.parquet',
    'view_monthly_donation_trends.parquet',
    'view_storage_requirement_analysis.parquet',
    'transformation_metadata.json',
]

EXPECTED_REAL_FILES = [
    'AMX_DONATION_HEADER.parquet',
    'AMX_DONATION_LINES.parquet',
    'ACBIDS_ARCHIVE.parquet',
    'ACSHARES.parquet',
]

def check_dir(label: str, rel: str, expected_files):
    base = get_data_dir(rel)
    print(f"{label}: {base}")
    if not base.exists():
        print(f"  MISSING: directory does not exist")
        return
    present = []
    missing = []
    for fname in expected_files:
        p = base / fname
        (present if p.exists() else missing).append(str(p))
    print("  Present files:")
    for p in present:
        print(f"    - {p}")
    if missing:
        print("  Missing files:")
        for p in missing:
            print(f"    - {p}")

if __name__ == "__main__":
    print("[Diagnostic] Data directory resolution")
    repo_root_guess = Path(__file__).resolve().parents[2]
    print(f"Script location: {Path(__file__).resolve()}")
    print(f"Repo root guess (two levels up): {repo_root_guess}")
    print("--")

    check_dir("Processed unified_real", 'processed/unified_real', EXPECTED_UNIFIED_FILES)
    print("--")
    check_dir("Processed real", 'processed/real', EXPECTED_REAL_FILES)
    print("-- Done.")

