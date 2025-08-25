"""
UI helpers that are independent of Streamlit/Dash specifics, e.g.,
formatters for metric badges or placeholders.
"""
from __future__ import annotations

from typing import Optional


def format_tonnes(value_t: Optional[float]) -> str:
    if value_t is None:
        return "— t"
    try:
        return f"{float(value_t):,.2f} t"
    except Exception:
        return "— t"

