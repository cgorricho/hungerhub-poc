# Sunburst Chart Label Correction Report

**Date:** 2025-08-14

## Issue

The dashboard development plan (`CONSOLIDATED_KPI_DASHBOARD_PLAN.md`) outlines a **Donor Hierarchy Sunburst Chart** for Page 1. The labels on this chart are not displaying horizontally in either the Dash or Streamlit applications, making them difficult to read.

## Analysis

This is a common layout behavior in the Plotly visualization library. By default, the text orientation for labels inside a sunburst chart is set to `'auto'`, which attempts to fit the text radially or tangentially based on the available space within each sector.

## Recommended Correction

To force all labels to be rendered horizontally, the `insidetextorientation` property of the chart's trace must be explicitly set to `'horizontal'`.

### Implementation

After the Plotly figure for the sunburst chart is created (e.g., `fig = px.sunburst(...)`), the following line of code should be added:

```python
# Assuming 'fig' is the variable holding the sunburst chart figure
fig.update_traces(insidetextorientation='horizontal')
```

### Explanation of the Fix

*   `fig.update_traces(...)`: This method applies a change to all data traces within the Plotly figure.
*   `insidetextorientation='horizontal'`: This parameter specifically targets the orientation of text inside the chart's sectors and forces it into a horizontal layout, which is ideal for readability.

This single line of code is the correct and most efficient way to resolve the issue in both the Dash and Streamlit applications, as they both use Plotly for rendering.
