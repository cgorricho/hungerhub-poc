"""
Shared metrics/aggregation helpers. Keep inputs in lbs; this module can return
aggregations in lbs and/or reporting tonnes.
"""
from __future__ import annotations

import pandas as pd

LBS_PER_METRIC_TON = 2204.62262185


def donor_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns per-donor totals with columns:
    - donor_name
    - total_weight_lbs
    - total_weight_t (metric tonnes)
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["donor_name", "total_weight_lbs", "total_weight_t"])
    if not {"donor_name", "weight_lbs"}.issubset(df.columns):
        return pd.DataFrame(columns=["donor_name", "total_weight_lbs", "total_weight_t"])

    agg = (
        df.groupby("donor_name", dropna=False)["weight_lbs"].sum().reset_index(name="total_weight_lbs")
    )
    agg["total_weight_t"] = agg["total_weight_lbs"] / LBS_PER_METRIC_TON
    return agg


def monthly_totals(df: pd.DataFrame, month_col: str = "month") -> pd.DataFrame:
    """
    Returns per-month totals with columns:
    - month
    - total_weight_lbs
    - total_weight_t
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=[month_col, "total_weight_lbs", "total_weight_t"])
    if not {month_col, "weight_lbs"}.issubset(df.columns):
        return pd.DataFrame(columns=[month_col, "total_weight_lbs", "total_weight_t"])

    agg = (
        df.groupby(month_col, dropna=False)["weight_lbs"].sum().reset_index(name="total_weight_lbs")
    )
    agg["total_weight_t"] = agg["total_weight_lbs"] / LBS_PER_METRIC_TON
    return agg

