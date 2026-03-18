# HungerHub — Oracle Data Analytics Platform

Production-ready analytics dashboard for HungerHub, a food bank / donation management system. Features dual Dash and Streamlit interfaces sharing a common module architecture, complete ETL pipeline from Oracle to Parquet, and CI/CD via GitHub Actions.

## Architecture

```
Oracle Database (cx_Oracle)
    ↓ ETL Pipeline
Parquet Files (fast columnar storage)
    ↓ Shared Analytics Modules
    ├── Plotly Dash App
    └── Streamlit App
```

### Why Two Frameworks?

The shared module architecture (`src/dashboard/modules/`) powers both Dash and Streamlit interfaces with identical business logic. This demonstrates:
- **Code reuse** — charts, metrics, labels, and data loaders written once, used by both frameworks
- **Framework comparison** — same data, same KPIs, different rendering approaches
- **Stakeholder flexibility** — deploy whichever framework fits the team's preference

## Dashboard Pages

### 1. Executive Summary
- Key Performance Indicators with trend indicators
- Donation volume and distribution metrics
- Operational efficiency scores

### 2. Donation Analytics
- Donor segmentation and retention analysis
- Geographic distribution of donations
- Seasonal patterns and forecasting

### 3. Agency Operations
- Order fulfillment tracking
- Agency performance metrics
- Supply chain efficiency

## ETL Pipeline

| Stage | Technology | Purpose |
|-------|-----------|---------|
| Extract | cx_Oracle | Connect to Oracle database, execute analytical queries |
| Transform | pandas | Clean, aggregate, compute KPIs |
| Load | Parquet (via Git LFS) | Fast columnar storage for dashboard consumption |

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Database | Oracle (cx_Oracle connector) |
| Backend | Python, pandas, SQLAlchemy |
| Dashboards | Plotly Dash + Streamlit |
| Storage | Parquet files (Git LFS) |
| CI/CD | GitHub Actions (pytest on push/PR) |
| Deployment | Azure VM + nginx reverse proxy |

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp config/.env.example config/.env
# Edit config/.env with Oracle credentials

# Streamlit
./run_streamlit_app.sh

# Dash
./run_dash_app.sh
```

## Project Context

Built as a 2-week accelerated POC using the Techbridge AI Collaboration framework (Agent Mode + Gemini CLI + Developer). Demonstrates rapid delivery of enterprise analytics from Oracle data sources.
