"""
Shared chart-building functions for the HungerHub dashboards.

Phase 3 modularization: Streamlit-first, then Dash mirrors usage.
These functions should be pure (no I/O); they receive prepared DataFrames
and configuration and return Plotly figures or derived data structures.
"""
from __future__ import annotations

from typing import Optional, Tuple, Dict

import pandas as pd
import plotly.graph_objects as go

from .labels import label_for_primary_metric


def donor_performance(df: pd.DataFrame, primary_metric: str = "weight") -> go.Figure:
    """
    Build a donor performance bar chart.

    Expected columns (minimal):
    - donor_name
    - total_weight (if primary_metric == "weight") OR total_units (if == "units")

    Returns a Plotly Figure.
    """
    fig = go.Figure()
    if df is None or df.empty:
        fig.update_layout(title_text="Donor Performance: no data available")
        return fig

    metric_col = "total_weight" if primary_metric == "weight" else "total_units"
    if metric_col not in df.columns or "donor_name" not in df.columns:
        fig.update_layout(title_text="Donor Performance: missing required columns")
        return fig

    fig.add_bar(x=df["donor_name"], y=df[metric_col], name=label_for_primary_metric(primary_metric))
    fig.update_layout(
        title_text=f"Donor Performance by {label_for_primary_metric(primary_metric)}",
        xaxis_title="Donor",
        yaxis_title=label_for_primary_metric(primary_metric),
    )
    return fig


def monthly_trends(df: pd.DataFrame, primary_metric: str = "weight") -> go.Figure:
    """
    Build monthly trends line chart.

    Expected columns: month, total_weight/total_units
    """
    fig = go.Figure()
    if df is None or df.empty:
        fig.update_layout(title_text="Monthly Trends: no data available")
        return fig

    metric_col = "total_weight" if primary_metric == "weight" else "total_units"
    if metric_col not in df.columns or "month" not in df.columns:
        fig.update_layout(title_text="Monthly Trends: missing required columns")
        return fig

    fig.add_scatter(x=df["month"], y=df[metric_col], mode="lines+markers", name=label_for_primary_metric(primary_metric))
    fig.update_layout(
        title_text=f"Monthly Trends by {label_for_primary_metric(primary_metric)}",
        xaxis_title="Month",
        yaxis_title=label_for_primary_metric(primary_metric),
    )
    return fig


def storage_sunburst(df: pd.DataFrame, primary_metric: str = "weight") -> go.Figure:
    """
    Build a storage requirement sunburst chart.

    Expected columns: primary_storage_requirement, secondary_storage_requirement (optional),
    and metric column depending on primary_metric.
    """
    fig = go.Figure()
    if df is None or df.empty:
        fig.update_layout(title_text="Storage Requirements: no data available")
        return fig

    metric_col = "total_weight" if primary_metric == "weight" else "total_units"
    if metric_col not in df.columns or "primary_storage_requirement" not in df.columns:
        fig.update_layout(title_text="Storage Requirements: missing required columns")
        return fig

    # Build hierarchical labels and parents
    labels = []
    parents = []
    values = []

    primary_groups = df.groupby(["primary_storage_requirement"], dropna=False)[metric_col].sum().reset_index()
    for _, row in primary_groups.iterrows():
        labels.append(str(row["primary_storage_requirement"]))
        parents.append("")
        values.append(float(row[metric_col]))

    if "secondary_storage_requirement" in df.columns:
        secondary_groups = df.groupby(["primary_storage_requirement", "secondary_storage_requirement"], dropna=False)[metric_col].sum().reset_index()
        for _, row in secondary_groups.iterrows():
            labels.append(str(row["secondary_storage_requirement"]))
            parents.append(str(row["primary_storage_requirement"]))
            values.append(float(row[metric_col]))

    fig = go.Figure(go.Sunburst(labels=labels, parents=parents, values=values))
    fig.update_layout(title_text="Storage Requirements by " + label_for_primary_metric(primary_metric))
    return fig


def sankey_flow(nodes_df: pd.DataFrame, links_df: pd.DataFrame, primary_metric: str = "weight") -> go.Figure:
    """
    Build a Sankey diagram given separate nodes and links dataframes.

    nodes_df expected columns: id, label
    links_df expected columns: source, target, value
    """
    fig = go.Figure()
    if nodes_df is None or nodes_df.empty or links_df is None or links_df.empty:
        fig.update_layout(title_text="Flow: no data available")
        return fig

    if not set(["id", "label"]).issubset(nodes_df.columns) or not set(["source", "target", "value"]).issubset(links_df.columns):
        fig.update_layout(title_text="Flow: missing required columns")
        return fig

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(label=nodes_df["label"].tolist()),
                link=dict(
                    source=links_df["source"].astype(int).tolist(),
                    target=links_df["target"].astype(int).tolist(),
                    value=links_df["value"].astype(float).tolist(),
                ),
            )
        ]
    )
    fig.update_layout(title_text=f"Flow by {label_for_primary_metric(primary_metric)}")
    return fig

