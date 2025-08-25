# Data Simulation Policy

Policy: No simulated or mocked data in any production code path.

Rationale:
- Simulation risks misleading stakeholders and invalidating insights
- Ensures trust and auditability of analytics

Scope:
- Dash and Streamlit apps, shared dashboard modules, ETL scripts, data loaders
- Any code under src/ used to build production dashboards

Requirements:
- Fail-fast instead of simulating: if data is missing or errors occur, render a visible error/annotation and log the issue
- Remove demo placeholders like "Demo Donor", "Donor A", or random fallbacks
- No use of np.random/random for production visualizations
- Any generated example data must be confined to:
  - Dedicated dev-only scripts under dev_tools/
  - Unit tests (fixtures) under tests/
  - Docs/tutorials (clearly marked)

Acceptable dev practices:
- In tests: generate synthetic fixtures; never import production modules that generate randoms
- In notebooks/dev scripts: clearly marked, outside of src/, with NO import side effects
- Feature flags: A DEV_MODE or similar may gate dev-only behavior; default must be production-safe

Operational guidance:
- Logging: use environment-driven logging; write to logs/ and avoid prints in production
- Error UX: prefer informative placeholders/annotations over silent fallbacks
- Reviews: any change touching data loading or KPIs requires dual-AI review

Verification:
- Tests assert no simulation keywords in production paths
- CI greps for forbidden patterns (e.g., 'Demo Donor', 'np.random', 'random\(') in src/ dashboard modules

