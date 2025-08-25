# Streamlit Tab Restructuring Guide

**Date:** 2025-08-14

## Issue

The developer is restructuring the `src/dashboard/streamlit/enhanced_app.py` from a single-page layout to a tabbed interface and requires guidance on the correct Python indentation and code structure for Streamlit tabs.

## The Core Principle of Streamlit Tabs

Any content you want to appear *inside* a specific tab must be indented directly under its corresponding `with tab_variable:` block. If the code is "un-indented" back to the same level as the `with` statement, it is no longer inside that block.

## Corrected Indentation Structure

Here is a pseudo-code template demonstrating the correct structure. This can be used as a direct guide for indenting the existing code blocks in `enhanced_app.py`.

```python
# =================================================================
# Main App Setup (No indentation)
# =================================================================
import streamlit as st
import pandas as pd

# Load your data here
# ...

st.title("HungerHub Analytics Dashboard")

# =================================================================
# Tab Creation (No indentation)
# =================================================================
tab1, tab2 = st.tabs(["📊 Donor & Timeline Analysis", "📦 Items & Quantities"])


# =================================================================
# --- TAB 1: DONOR & TIMELINE ANALYSIS ---
# =================================================================
with tab1:
    # All code for Tab 1 must be indented by 4 spaces
    
    # --- Section 1: Donor Analysis ---
    st.markdown("### Donor Performance Analysis")
    donor_col1, donor_col2 = st.columns([2, 1])

    with donor_col1:
        # This code is indented by 8 spaces (4 for 'with tab1', 4 for 'with donor_col1')
        # Your donor performance dual-axis chart code goes here
        st.plotly_chart(...)

    with donor_col2:
        # This code is also indented by 8 spaces
        # Your donor metrics and key insights panel code goes here
        st.metric(...)
        st.dataframe(...)

    # --- Monthly Timeline Section (Correctly nested inside Tab 1) ---
    st.markdown("---") # Visual separator
    st.markdown("### Monthly Donation Timeline")
    
    # This code is indented by 4 spaces, placing it inside tab1 but after the columns above
    trends_col1, trends_col2 = st.columns([3, 1])

    with trends_col1:
        # Indented by 8 spaces
        # Your multi-metric timeline chart code goes here
        st.plotly_chart(...)

    with trends_col2:
        # Indented by 8 spaces
        # Your timeline analytics and seasonality analysis code goes here
        st.dataframe(...)


# =================================================================
# --- TAB 2: ITEMS & QUANTITIES ---
# =================================================================
with tab2:
    # All code for Tab 2 must be indented by 4 spaces
    
    # --- Section 2: Items & Quantities ---
    st.markdown("### Item & Quantity Analysis")
    items_col1, items_col2 = st.columns([2, 1])

    with items_col1:
        # Indented by 8 spaces
        # Your storage composition sunburst chart code goes here
        st.plotly_chart(...)
        
        # Your donation flow funnel chart code can go below it in the same column
        st.plotly_chart(...)

    with items_col2:
        # Indented by 8 spaces
        # Your items & quantities metrics panel code goes here
        st.metric(...)
        st.dataframe(...)

# =================================================================
# Code outside of any 'with tabX:' block will appear on every page,
# either above or below the tabs depending on its position.
# =================================================================
st.markdown("---")
st.info("Dashboard data is based on the full, processed Oracle dataset.")

```

## Best Practices for Complex Layouts

1.  **Encapsulate in Functions:** For very complex tabs, consider moving the code for each tab into its own function. This makes the main body of your app much cleaner.
    ```python
    def render_donor_analysis_tab():
        st.markdown("### Donor Performance Analysis")
        # ... all your tab 1 code ...

    def render_items_quantities_tab():
        st.markdown("### Item & Quantity Analysis")
        # ... all your tab 2 code ...

    tab1, tab2 = st.tabs(["...", "..."])

    with tab1:
        render_donor_analysis_tab()

    with tab2:
        render_items_quantities_tab()
    ```

2.  **Use Visual Separators:** Use `st.markdown("---")` to create horizontal lines that visually separate distinct sections within a single tab.

3.  **Incremental Changes:** When refactoring a large script like this, move one section at a time into its correct tab and re-run the app to ensure it works before moving the next section. This makes debugging much easier.
