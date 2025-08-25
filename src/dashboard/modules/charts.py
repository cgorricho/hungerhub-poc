"""
Shared chart-building functions for the HungerHub dashboards.

Phase 3 modularization: Streamlit-first, then Dash mirrors usage.
These functions should be pure (no I/O); they receive prepared DataFrames
and configuration and return Plotly figures or derived data structures.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from .labels import primary_metric_label


def donor_performance(df: pd.DataFrame, include_avg_weight_per_unit: bool = False) -> go.Figure:
    """
    Build a donor performance bar chart.

    Expected columns (minimal):
    - donor_name
    - total_weight_lbs
    
    Optional columns for secondary y-axis:
    - total_donated_qty (for calculating avg weight per unit)

    Returns a Plotly Figure reporting in metric tonnes.
    If include_avg_weight_per_unit=True and qty data is available,
    adds red dots on secondary y-axis showing average weight per unit.
    """
    fig = go.Figure()
    if df is None or df.empty:
        fig.update_layout(title_text="Donor Performance: no data available")
        return fig

    required = {"donor_name", "total_weight_lbs"}
    if not required.issubset(df.columns):
        fig.update_layout(title_text="Donor Performance: missing required columns")
        return fig

    lbs = df["total_weight_lbs"].astype(float)
    tonnes = lbs / 2204.62262185

    # Primary bar chart (total weight)
    fig.add_bar(
        x=df["donor_name"], 
        y=tonnes, 
        name=primary_metric_label(),
        yaxis="y",
        marker_color="steelblue"
    )

    # Secondary y-axis for average weight per unit if requested and data available
    if include_avg_weight_per_unit and "total_donated_qty" in df.columns:
        qty = df["total_donated_qty"].astype(float)
        # Calculate average weight per unit in pounds (not tonnes)
        avg_weight_per_unit_lbs = lbs / qty
        # Filter out invalid values (division by zero, etc.)
        valid_mask = (qty > 0) & pd.notna(avg_weight_per_unit_lbs)
        
        if valid_mask.any():
            fig.add_scatter(
                x=df.loc[valid_mask, "donor_name"],
                y=avg_weight_per_unit_lbs[valid_mask],
                mode="markers",
                name="Avg Weight per Unit (lbs)",
                yaxis="y2",
                marker=dict(color="red", size=12, symbol="circle"),
                line=dict(color="red")
            )
            
            # Configure secondary y-axis
            fig.update_layout(
                yaxis2=dict(
                    title="Average Weight per Unit (lbs)",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                    zeroline=False
                )
            )

    fig.update_layout(
        title_text=f"Donor Performance by {primary_metric_label()}",
        xaxis_title="Donor",
        yaxis_title=primary_metric_label(),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=0.92,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    return fig


def monthly_trends(df: pd.DataFrame) -> go.Figure:
    """
    Build monthly trends line chart.

    Expected columns: month, total_weight_lbs
    """
    fig = go.Figure()
    if df is None or df.empty:
        fig.update_layout(title_text="Monthly Trends: no data available")
        return fig

    required = {"month", "total_weight_lbs"}
    if not required.issubset(df.columns):
        fig.update_layout(title_text="Monthly Trends: missing required columns")
        return fig

    tonnes = df["total_weight_lbs"].astype(float) / 2204.62262185

    fig.add_scatter(x=df["month"], y=tonnes, mode="lines+markers", name=primary_metric_label())
    fig.update_layout(
        title_text=f"Monthly Trends by {primary_metric_label()}",
        xaxis_title="Month",
        yaxis_title=primary_metric_label(),
    )
    return fig


def storage_sunburst(df: pd.DataFrame) -> go.Figure:
    """
    Build a storage requirement sunburst chart.

    Expected columns: primary_storage_requirement, secondary_storage_requirement (optional),
    and total_weight_lbs.
    """
    fig = go.Figure()
    if df is None or df.empty:
        fig.update_layout(title_text="Storage Requirements: no data available")
        return fig

    if "total_weight_lbs" not in df.columns or "primary_storage_requirement" not in df.columns:
        fig.update_layout(title_text="Storage Requirements: missing required columns")
        return fig

    metric_col = "total_weight_lbs"

    # Build hierarchical labels and parents
    labels = []
    parents = []
    values = []

    primary_groups = df.groupby(["primary_storage_requirement"], dropna=False)[metric_col].sum().reset_index()
    for _, row in primary_groups.iterrows():
        labels.append(str(row["primary_storage_requirement"]))
        parents.append("")
        values.append(float(row[metric_col]) / 2204.62262185)

    if "secondary_storage_requirement" in df.columns:
        secondary_groups = df.groupby(["primary_storage_requirement", "secondary_storage_requirement"], dropna=False)[metric_col].sum().reset_index()
        for _, row in secondary_groups.iterrows():
            labels.append(str(row["secondary_storage_requirement"]))
            parents.append(str(row["primary_storage_requirement"]))
            values.append(float(row[metric_col]) / 2204.62262185)

    fig = go.Figure(go.Sunburst(labels=labels, parents=parents, values=values))
    fig.update_layout(title_text="Storage Requirements by " + primary_metric_label())
    return fig


def sankey_flow(nodes_df: pd.DataFrame, links_df: pd.DataFrame) -> go.Figure:
    """
    Build a Sankey diagram given separate nodes and links dataframes.

    nodes_df expected columns: id, label
    links_df expected columns: source, target, value_lbs
    """
    fig = go.Figure()
    if nodes_df is None or nodes_df.empty or links_df is None or links_df.empty:
        fig.update_layout(title_text="Flow: no data available")
        return fig

    if not {"id", "label"}.issubset(nodes_df.columns) or not {"source", "target", "value_lbs"}.issubset(links_df.columns):
        fig.update_layout(title_text="Flow: missing required columns")
        return fig

    values_tonnes = (links_df["value_lbs"].astype(float) / 2204.62262185).tolist()

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(label=nodes_df["label"].tolist()),
                link=dict(
                    source=links_df["source"].astype(int).tolist(),
                    target=links_df["target"].astype(int).tolist(),
                    value=values_tonnes,
                ),
            )
        ]
    )
    fig.update_layout(title_text=f"Flow by {primary_metric_label()}")
    return fig

