# HungerHub Analytics POC

Streamlit-first analytics dashboards with shared modules, ETL from Oracle to Parquet, and mirrored Dash implementation.

## What's in this repo
- Streamlit app: src/dashboard/streamlit/enhanced_app.py
- Dash app: src/dashboard/dash/enhanced_app.py
- Shared modules: src/dashboard/modules/ (charts, metrics, labels, loaders, ui)
- ETL: src/data_extraction/
- Tests: tests/
- CI: .github/workflows/ci.yml (pytest on push/PR)
- LFS: .gitattributes (tracks data/**/*.parquet and data/**/*.csv)

## Quick start
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp config/.env.example config/.env
# Edit config/.env with Oracle credentials if needed

# Run Streamlit app
./run_streamlit_app.sh

# Run Dash app
./run_dash_app.sh
```

## Development conventions
- Primary KPI: total weight (lbs at rest; convert/label to metric tonnes for reporting)
- No simulated/demo data in production paths; fail fast with clear guidance
- Parquet-first loaders using utils/paths helpers
- Logging via LOG_LEVEL/LOG_DIR envs; logs directory is ensured

## CI and tests
- GitHub Actions runs pytest across Python 3.10–3.13
- Oracle-dependent tests skip when credentials are not provided

## Git LFS
- Large data files in data/ are tracked with Git LFS (parquet, csv)
- Run `git lfs install` locally; enable LFS at the repo level in GitHub settings

## Notes
- Legacy scripts moved to archive/legacy_code/
- HTML artifacts are under docs/artifacts/
