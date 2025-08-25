# KPI Standardization Guide

Decision: Total Gross Weight is the dominant measuring unit across the dashboard.

Scope and principles:
- Primary KPI: Total Gross Weight
  - Display defaults: tons on charts, pounds in hover/details where helpful
  - Secondary metrics: item units (counts), donation counts
  - Labeling: Always label axes/legends with explicit units (e.g., Weight (tons), Units (count))

Implementation requirements:
- Config: define PRIMARY_VOLUME_METRIC = "weight" and units mapping
- Charts: weight-first
  - Donor Performance: primary series = weight (tons); secondary series = units (count)
  - Sankey: flow values determined by weight; title and legend reflect weight
  - Geographic map: color scale by total weight; hover includes lbs and org count
  - Storage composition: if quantity is displayed, clarify when it’s units vs weight
- UI/UX:
  - Use clear, consistent titles: "Total Weight (tons)"; avoid ambiguous "Quantity"
  - Avoid mixing unit families on the same axis; if unavoidable, use dual axes with clear labels
- Tests:
  - Verify that label builders produce weight-forward labels
  - Assert that PRIMARY_VOLUME_METRIC is consulted by chart builders

Data handling:
- Weight source: use TOTALGROSSWEIGHT where available; convert to tons via lbs/2000 for display
- Aggregations: sum over the appropriate dimension; avoid averaging weights unless intended and labeled

Change control:
- Any deviation from weight-first must be called out in PRs and cleared with stakeholders

