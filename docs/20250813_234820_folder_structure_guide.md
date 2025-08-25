# HungerHub POC - Folder Structure Guide

## 🎯 **Aligned with Development Docs & 2-Week Plan**

This structure follows the **DEVELOPMENT_WORKFLOW_GUIDE.md** standards and implements the **HungerHub_Accelerated_2Week_POC.md** requirements.

## 📁 **Complete Directory Structure**

### **Root Level**
```
hungerhub_poc/
├── README.md                    # Project overview & quick start
├── requirements.txt             # Python dependencies
├── PROJECT_STATUS.md            # Current implementation status  
├── IMPROVEMENT_PLAN.md          # 14-day roadmap & milestones
├── .gitignore                   # Git ignore patterns
└── FOLDER_STRUCTURE_GUIDE.md    # This file
```

### **Source Code** (`src/`)
```
src/
├── __init__.py                  # Package initialization
├── README.md                    # Module documentation
├── data_extraction/             # Oracle connection & queries
│   └── __init__.py
├── etl_pipeline/                # Data cleaning & transformation
│   └── __init__.py  
├── analytics/                   # KPI calculation & analysis
│   └── __init__.py
└── dashboard/                   # Plotly Dash application
    ├── __init__.py
    ├── app.py                   # Main dashboard entry point
    ├── pages/                   # Individual dashboard pages
    │   ├── executive_summary.py
    │   ├── donation_analytics.py
    │   └── agency_operations.py
    ├── components/              # Reusable UI components
    └── assets/                  # CSS, images, static files
```

### **Data Storage** (`data/`)
```
data/
├── README.md                    # Data flow documentation
├── raw/                         # Original Oracle extracts
├── processed/                   # Cleaned Parquet files
└── output/                      # Analysis results & exports
```

### **Configuration** (`config/`)
```
config/
└── .env.example                 # Environment variables template
```

### **Testing** (`tests/`)
```
tests/
├── unit/                        # Unit tests
└── integration/                 # Integration tests
```

### **Documentation** (`docs/`)
```
docs/
├── architecture.md              # System design decisions
├── deployment.md                # Environment-specific instructions
├── testing_plan.md              # Testing strategies & results
└── improvement_history.md       # Record of completed improvements
```

### **Development Support**
```
├── logs/                        # Application logs
├── notebooks/                   # Jupyter notebooks for exploration
├── scripts/                     # Utility scripts
└── deployment/                  # Deployment configurations
```

## 🎯 **Alignment with POC Requirements**

### **Week 1 Implementation**
- `src/data_extraction/` → **Day 1-2**: Oracle connection
- `src/etl_pipeline/` → **Day 3-4**: ETL pipeline  
- `src/dashboard/` → **Day 5-7**: Dashboard framework

### **Week 2 Implementation**
- `src/dashboard/pages/` → **Day 8-10**: Essential visualizations
- `src/dashboard/components/` → **Day 11-12**: Interactivity & polish
- `deployment/` → **Day 13-14**: Production deployment

### **3-Page Dashboard Structure**
1. **Executive Summary** (`src/dashboard/pages/executive_summary.py`)
   - KPI cards, trends, top donors, geographic map
2. **Donation Analytics** (`src/dashboard/pages/donation_analytics.py`)
   - Distributions, patterns, rankings, seasonal analysis
3. **Agency Operations** (`src/dashboard/pages/agency_operations.py`)
   - Fulfillment rates, performance metrics, demand vs supply

## ✅ **Development Standards Compliance**

### **From DEVELOPMENT_WORKFLOW_GUIDE.md**:
- ✅ Standard project files (README.md, .gitignore, requirements.txt)
- ✅ PROJECT_STATUS.md for current implementation status
- ✅ IMPROVEMENT_PLAN.md for planned enhancements and roadmap
- ✅ Documentation directory with architecture and deployment guides
- ✅ Tests directory with unit and integration test structure
- ✅ Logs directory for application logging

### **Technical Architecture Alignment**:
- ✅ **Oracle → Python → Plotly Dash** pipeline structure
- ✅ **Parquet files** for fast I/O (data/processed/)
- ✅ **3-page dashboard** framework (dashboard/pages/)
- ✅ **Basic interactivity** support (dashboard/components/)
- ✅ **Azure deployment** preparation (deployment/)

## 🚀 **Ready for Development**

This structure is now ready for:
1. **Day 1**: Oracle Instant Client installation & connection testing
2. **Day 2**: Initial data extraction implementation
3. **Day 3-4**: ETL pipeline development
4. **Day 5+**: Dashboard framework implementation

**The folder structure perfectly aligns with both the development standards and the 2-week POC plan!**
