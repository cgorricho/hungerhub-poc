# Streamlit Enhanced App Stall Resolution Plan

Author: Agent Mode (gpt-5)
Date: 2025-08-18T04:13:55Z
Target: src/dashboard/streamlit/enhanced_app.py

Summary
- The enhanced Streamlit app intermittently “stalls” on load. Gemini’s review indicates a FileNotFoundError due to data paths resolving under src/data/... instead of data/....
- Additional minor robustness issues exist (e.g., undefined state_impact_df after a failed try in the Geo tab, inconsistent path usage bypassing the paths utility), which can exacerbate failures.
- This plan prioritizes a minimal, high-confidence fix for the path resolution, followed by guardrails to prevent future hard-stops, and finishes with focused validation.

Primary hypothesis (aligned with Gemini)
- Root cause: get_project_root()/get_data_dir() localization causes processed data lookups to resolve to src/data/... rather than data/..., so initial parquet reads fail with FileNotFoundError during load_donation_data().
- Consequence: Streamlit shows an error and halts early; perceived as a “stall.”

Secondary findings to harden later
- In Tab 4 (Geo/Org): if the data-read try block fails, state_impact_df is referenced afterward but never defined, causing a NameError.
- In a few places, manual path math (Path(__file__).parents.../data/...) is used instead of get_data_dir(), creating inconsistency.

Non-goals for this fix
- No behavioral changes to analytics or UI beyond stability and correct data loading.
- No re-introduction of simulated/fallback production data paths (policy remains fail-fast for missing data).

Execution plan
1) Reproduce and validate the issue (no code changes)
   - Run diagnostics to print resolved data dirs and verify required files:
     - python3 scripts/diagnostics/print_data_paths.py
     - python3 scripts/diagnostics/check_parquet_reads.py
   - Expectation if broken: unified_real resolves under src/data/..., missing files reported.

2) Fix path resolution at the root (minimal change)
   - Inspect src/utils/paths.py (get_project_root, get_data_dir) and correct base resolution so get_data_dir('processed/unified_real') -> <repo>/data/processed/unified_real (not <repo>/src/data/...).
   - Keep behavior robust regardless of current working directory and execution context.
   - Do not change enhanced_app.py yet.

3) Validate the fix (no UI changes yet)
   - Re-run the diagnostics from step 1; confirm directories and parquet reads succeed.
   - If successful, run the healthcheck app to confirm Streamlit environment:
     - streamlit run src/dashboard/streamlit/healthcheck_app.py --server.port 8599 --server.headless true

4) Standardize path usage inside enhanced_app.py (consistency sweep)
   - Replace any manual project_root/path math with get_data_dir(...), especially in:
     - Geo/Org tab where data_dir = project_root / 'data/processed/real' appears.
   - This eliminates divergence in data locations and prevents partial loads.

5) Add robust guards (no behavioral changes)
   - Initialize state_impact_df to an empty DataFrame before the try, or set it in the except, so downstream operations don’t crash when data is unavailable.
   - Before using nlargest/iterating, check not state_impact_df.empty.
   - Ensure any optional visuals that depend on extended datasets short-circuit with user-facing st.info/st.error without raising.

6) Caching and load hygiene
   - Keep st.cache_data on the data-loading functions with modest TTL to avoid heavy I/O on first paint every time.
   - Avoid any heavyweight reads at import time; ensure they occur within functions.

7) Validation (functional)
   - Launch the enhanced app:
     - streamlit run src/dashboard/streamlit/enhanced_app.py --server.port 8599
   - Smoke test:
     - Confirm the Donation Tracking page renders without error.
     - Verify Donor chart and Monthly trends appear.
     - Navigate to Geo/Org tab; confirm either real map renders or a clear non-fatal message is shown if inputs are missing; no stalls.

8) Regression checks
   - Run pytest to ensure existing tests still pass and no simulation artifacts reintroduced.
   - If CI is configured, push to a feature branch and let the workflow validate on multiple Python versions.

9) Rollback and risk mitigation
   - All edits will be in a feature branch, small and isolated:
     - Fix in src/utils/paths.py
     - Minor defensive changes in enhanced_app.py (path standardization + guards)
   - If issues arise, rollback by reverting the feature branch merge or cherry-pick revert.

10) Open questions for Gemini
   - Confirm the intended canonical behavior of get_project_root(): should it anchor at the repo root (folder containing data/, src/, docs/, etc.) regardless of invocation path?
   - Any additional datasets expected by enhanced_app.py that should be validated by diagnostics?
   - Preference for failing visuals: st.error vs st.info + placeholder figure?

Deliverables
- Diagnostics scripts (already added):
  - scripts/diagnostics/print_data_paths.py
  - scripts/diagnostics/check_parquet_reads.py
  - scripts/diagnostics/repro_geo_state_impact.py
- Minimal code patches:
  - src/utils/paths.py: correct get_project_root/get_data_dir base
  - src/dashboard/streamlit/enhanced_app.py: replace manual paths with get_data_dir; add guards around state_impact_df usage

Success criteria
- Diagnostics show correct absolute paths under data/ (not src/data/), and parquet reads succeed.
- Streamlit enhanced app loads without stalling, both in Donation Tracking and Geo/Org tabs.
- Tests pass in local and CI environments.

Appendix: Incorporating Gemini remark (2025-08-18 04:19Z)
- Path utility hardening: Implement marker-based repo root detection in src/utils/paths.py by walking parents from Path(__file__).resolve() and returning the first directory containing a reliable marker (preferred order: .git, pyproject.toml or requirements.txt, README.md, data/ alongside src/). Fall back to two-levels-up heuristic only if no marker found.
- Cross-CWD verification: Add a focused test script (scripts/test_path_resolution.py) to print get_data_dir('processed/unified_real') and assert existence when run from multiple working directories (repo root and src/). This directly matches Gemini’s Phase 2 guidance.
- Launch verification: After utilities pass the cross-CWD test, run the Streamlit app and confirm the FileNotFoundError is gone (Gemini’s Phase 3). Retain the additional guards outlined above as secondary hardening, executed after the primary path fix is verified.

