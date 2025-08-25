# HungerHub ETL Pipeline Documentation

## Overview

This document explains the ETL (Extract, Transform, Load) pipeline implemented within the `src/` directory. The pipeline is designed to extract full table data from the Oracle databases, process and unify it, and prepare it for visualization in the dashboards.

The process is not fully automated in a single script. It consists of two main standalone scripts that must be run in a specific order, followed by the launch of the dashboard applications which consume the final output.

---

## Pipeline Execution Flow

The ETL process is executed in two distinct, manual stages:

1.  **Stage 1: Extraction** - The `full_data_extractor.py` script connects to the Oracle database and extracts the complete, unfiltered high-priority tables into local Parquet and CSV files.
2.  **Stage 2: Unification** - The `create_unified_real_data.py` script takes the raw extracted files from Stage 1, cleans them, merges them into unified datasets (donations, organizations, orders), and saves them in a dashboard-ready format.

After these two stages are complete, the dashboard applications can be launched to visualize the final, unified data.

---

## File Breakdown by Execution Stage

Here is the logical order of operations and the purpose of each key file in the pipeline.

### Stage 1: Data Extraction (Standalone Script)

*   **File:** `data_extraction/full_data_extractor.py`
    *   **Purpose:** This is the **first script** to run in the ETL pipeline. It connects to the production Oracle database and performs a full extraction of the high-priority tables identified during the R&D phase. It does **not** sample the data. Its output is a set of raw data files (CSV and Parquet) stored primarily in `data/processed/real/`.
    *   **How to Run:** This script is run independently from the command line:
      ```bash
      python src/data_extraction/full_data_extractor.py
      ```

### Stage 2: Data Unification (Standalone Script)

*   **File:** `data_extraction/create_unified_real_data.py`
    *   **Purpose:** This is the **second script** to run. It depends on the output from `full_data_extractor.py`. It takes the raw extracted tables, performs transformations, merges them into three core unified datasets (`donations`, `organizations`, `orders`), and saves them to the `data/processed/unified_real/` directory.
    *   **How to Run:** This script is run independently after the extraction is complete:
      ```bash
      python src/data_extraction/create_unified_real_data.py
      ```

### Stage 3: Dashboard Visualization (Application Entry Points)

These scripts are **not** part of the ETL data processing but are the consumers of its final output. They should only be run after the extraction and unification stages are complete.

*   **File:** `dashboard/dash/enhanced_app.py`
    *   **Purpose:** This file contains the source code for the primary **Plotly Dash** application. It loads the unified data from `data/processed/unified_real/` and presents it in a 3-page interactive dashboard.
    *   **How it's Invoked:** It is launched via the `launch_enhanced_dash.sh` script in the project root.

*   **File:** `dashboard/streamlit/enhanced_app.py`
    *   **Purpose:** This file contains the source code for the alternative **Streamlit** dashboard. It also loads the unified data from `data/processed/unified_real/`.
    *   **How it's Invoked:** It is launched via the `launch_enhanced_streamlit.sh` script in the project root.

---

### Supporting & Utility Modules

*   **File:** `data_extraction/oracle_connection_test.py`
    *   **Purpose:** A utility script to quickly test the connection to the Oracle database, independent of the main ETL process.

*   **File:** `data_extraction/oracle_table_discovery.py`
    *   **Purpose:** A utility script used during development to explore the database schema and identify tables with data.

### Deprecated Files

*   **Files under `src/deprecated/`:** This directory contains older versions of scripts, including:
    *   `deprecated/pipeline/etl_pipeline.py`: The original ETL script that worked with mock sample data.
    *   `deprecated/data_extraction/real_data_extractor.py`: The first version of the extractor that used sampling instead of full extraction.

These files are kept for historical reference but are **not** used in the current production ETL pipeline.