"""
Labels and unit helpers for dashboard charts, aligned with PRIMARY_VOLUME_METRIC.
Supports reporting in metric tonnes (t) while source data remains in pounds (lbs).
"""
from __future__ import annotations

from typing import Literal

# Canonical storage unit stays in pounds (lbs)
STORAGE_UNIT: Literal["lbs"] = "lbs"

# Reporting system: "imperial" (short tons) or "metric" (tonnes)
WEIGHT_SYSTEM: Literal["imperial", "metric"] = "metric"

# Exact conversion constants
LBS_PER_SHORT_TON = 2000.0
LBS_PER_KG = 2.20462262185
LBS_PER_METRIC_TON = 2204.62262185


def lbs_to_reporting_tons(lbs: float, system: str = WEIGHT_SYSTEM) -> float:
    """Convert stored pounds to the configured reporting tons value.
    - imperial: short tons (US)
    - metric: metric tonnes (t)
    """
    if system == "imperial":
        return lbs / LBS_PER_SHORT_TON
    # default metric
    return lbs / LBS_PER_METRIC_TON


def reporting_unit_label(system: str = WEIGHT_SYSTEM) -> str:
    return "tons" if system == "imperial" else "t"


def primary_metric_label(system: str = WEIGHT_SYSTEM) -> str:
    return f"Total Weight ({reporting_unit_label(system)})"

