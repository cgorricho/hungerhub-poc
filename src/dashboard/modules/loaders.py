"""
Shared data loading helpers for dashboards. Parquet-first with CSV fallback,
returning DataFrames with weight in canonical lbs columns.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd

from src.utils.paths import get_data_dir


def read_unified_view(name: str) -> Optional[pd.DataFrame]:
    base = get_data_dir("processed/unified_real")
    parquet_path = base / f"{name}.parquet"
    csv_path = base / f"{name}.csv"

    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None

