# Dashboard Data Consistency - Quality Assessment Report

**Date:** 2025-08-14

## Executive Summary

The assessment confirms that the dashboard is **excellent** in its data sourcing; it correctly and exclusively uses real data processed from the Oracle database extracts. However, the assessment reveals **significant inconsistencies** in how core business metrics are used across different charts and tabs. Specifically, the dashboard inconsistently uses "Total Gross Weight" and "Total Units Donated" as the primary measure of donation volume, which could lead to confusing or misleading interpretations for the end-user.

**Overall Score: 7/10** (High score for data sourcing, but points deducted for the critical metric inconsistency).

---

## Part 1: Data Source Verification

**Status:** ✅ **PASS**

My review confirms that 100% of the data visualized in the dashboard originates from the correct, production-grade ETL pipeline outputs.

*   **Data Loading Functions:** All data loading functions (`load_donation_data`, `load_raw_oracle_data`, `load_donor_gross_weight_data`) correctly point to file paths within the `data/processed/real/` and `data/processed/unified_real/` directories.
*   **No Mock Data:** There are no hardcoded dataframes, references to sample files, or mock data being used anywhere in the application.
*   **Real-Time Connection:** The dashboard is successfully loading the data processed from the real Oracle database, as intended by the project plan.

**Conclusion:** The data foundation of the dashboard is solid and correctly implemented.

---

## Part 2: Metric Consistency Analysis

**Status:** ⚠️ **FAIL**

My review identified critical inconsistencies in the use of primary metrics, particularly regarding how a donor's contribution is measured. The dashboard alternates between using **weight** (`TOTALGROSSWEIGHT`) and **units** (`total_donated_qty`), even within the same section, which violates the principle of data consistency.

### Key Inconsistency: Weight vs. Units

1.  **Inconsistent Donor Performance Chart (Tab 1):**
    *   The "Top Donor Performance Overview" chart is a dual-axis chart.
    *   The **bar chart** measures performance by **Total Gross Weight (in Tons)**.
    *   The **scatter plot** on the secondary axis measures performance by **Total Units Donated**.
    *   **Issue:** This chart directly compares two different units of measure (weight vs. item count) as if they are equivalent representations of performance, which is confusing. A donor who donates many small, light items would appear high on the "Units" metric but low on the "Weight" metric, and vice-versa.

2.  **Inconsistent Sankey Diagram (Tab 4):**
    *   The "HungerHub Real Donation Flow" Sankey diagram calculates its flow values based on `TOTALGROSSWEIGHT`.
    *   **Issue:** This visualization uses **weight** as its primary measure, which is inconsistent with the "Total Units" metric used in other parts of the dashboard, including the scatter plot in the main donor chart. An end-user looking at both charts would be seeing performance measured in two different ways without a clear explanation.

3.  **Confusing Metrics Display (Tab 1):**
    *   The "Donor Metrics Dashboard" displays metrics for both "Total Units" and "Total Weight (lbs)".
    *   **Issue:** While it's good to show both, the lack of a clearly defined *primary* KPI makes it difficult for a user to know which metric the main visualizations are based on without inspecting the code. The dashboard should have a primary, consistently used metric for all major performance rankings.

### Impact of Inconsistency

*   **Misinterpretation:** A user may incorrectly conclude that a donor is a "top performer" based on a unit count chart, while they may be a low-volume donor in terms of actual weight/substance.
*   **Lack of Trust:** Inconsistent metrics can erode user trust in the data and the insights presented by the dashboard.
*   **Flawed Comparisons:** It becomes impossible to accurately compare different charts (e.g., the Donor Performance chart vs. the Sankey diagram) because they are based on different underlying units of measure.

---

## Recommendations

1.  **Establish a Single Primary Metric:** The development team must decide on a **single, primary Key Performance Indicator (KPI)** for measuring donation volume. Based on industry standards for food banking, **Total Gross Weight** is the more common and meaningful metric. "Total Units" should be treated as a secondary, supplementary metric.

2.  **Update All Visualizations for Consistency:** Once a primary metric is chosen (e.g., Total Gross Weight), all major visualizations should be updated to use it.
    *   **Donor Performance Chart:** Both the bar chart and the scatter plot should represent `TOTALGROSSWEIGHT`. The scatter plot can be used to show a different aspect of the weight (e.g., average weight per donation) but should not introduce a different unit.
    *   **Sankey Diagram:** This is already correct (using weight), but its title and labels should be updated to make this clear (e.g., "Donation Flow by Total Weight").
    *   **All other charts:** All other performance-based rankings and visualizations should be reviewed and standardized to use the chosen primary metric.

3.  **Clarify Labels and Titles:** All chart titles, axis labels, and tooltips must be updated to be explicit about the unit of measure being displayed (e.g., "Total Weight (Tons)", "Total Units Donated"). This removes ambiguity for the end-user.
