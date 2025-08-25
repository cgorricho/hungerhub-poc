# Launch Scripts Summary

## 🧹 **Launch Scripts Cleanup - 2025-08-13**

### **Overview**
Eliminated launch scripts that reference deprecated files and fixed path issues in remaining scripts.

---

## ✅ **Active Launch Scripts (Root Directory)**

### 1. **`launch_enhanced_dash.sh`**
- **Target**: `src/dashboard/dash/enhanced_app.py`
- **Port**: `localhost:8050`
- **Features**: 
  - **Foreground execution** (attached terminal)
  - Process management (kills existing instances)
  - Timestamped logging with live output
  - Automatic virtual environment activation
- **Status**: ✅ **READY TO USE**

### 2. **`launch_enhanced_streamlit.sh`** 
- **Target**: `src/dashboard/streamlit/enhanced_app.py` 
- **Port**: `localhost:8501` (changed from 8503)
- **Features**:
  - **Foreground execution** (attached terminal)
  - Process management (kills existing instances)
  - Timestamped logging with live output
  - Automatic virtual environment activation
- **Status**: ✅ **READY TO USE**

---

## ❌ **Deprecated Launch Scripts (Moved to `src/deprecated/scripts/launch_scripts/`)**

### 1. **`launch_dash_dashboard.sh`** - DEPRECATED
- **Issues**: 
  - References `real_data_extractor.py` (deprecated)
  - Incorrect path `src/dashboard/app.py` (should be `src/dashboard/dash/app.py`)
- **Good concepts**: Virtual env management, comprehensive logging, error handling

### 2. **`launch_dashboard.sh`** - DEPRECATED  
- **Issues**:
  - References `test_dashboard.py` (deprecated)
  - Incorrect path `src/dashboard/main_app.py` (should be `src/dashboard/streamlit/main_app.py`)

### 3. **`launch_dash_dashboard.sh.backup`** - DEPRECATED
- **Reason**: Backup of deprecated script

---

## 🚀 **How to Use Active Launch Scripts**

### **For Dash Dashboard (Foreground Mode):**
```bash
./launch_enhanced_dash.sh
```
- Dashboard available at: http://localhost:8050
- Logs saved to: `logs/dash_app_TIMESTAMP.log`
- **Press Ctrl+C to stop** (runs in foreground with attached terminal)

### **For Streamlit Dashboard (Foreground Mode):**
```bash
./launch_enhanced_streamlit.sh  
```
- Dashboard available at: http://localhost:8501
- Logs saved to: `logs/streamlit_app_TIMESTAMP.log`
- **Press Ctrl+C to stop** (runs in foreground with attached terminal)

### **Alternative: Stop from Another Terminal:**
```bash
# Stop Dash
pkill -f "python.*enhanced_app.py"

# Stop Streamlit  
pkill -f "streamlit.*enhanced_app.py"

# Stop both
pkill -f "enhanced_app.py"
```

---

## 🔧 **Fixes Applied**

1. **✅ Removed Deprecated References**
   - Eliminated scripts referencing `real_data_extractor.py`
   - Eliminated scripts referencing `test_dashboard.py` 
   - Removed scripts with incorrect dashboard paths

2. **✅ Fixed Path Issues**
   - Updated hardcoded paths to use dynamic resolution
   - Ensured scripts work from any directory location

3. **✅ Updated Execution Mode**
   - Changed from background to **foreground execution**
   - Apps now run with **attached terminals** for better control
   - Streamlit port changed from 8503 to **8501** (standard port)
   - Maintained logging and process management features

---

## 📋 **Data Pipeline Before Dashboard Launch**

If you need data before running dashboards:

```bash
# 1. Extract Oracle data (if not already done)
python src/data_extraction/full_data_extractor.py

# 2. Create unified datasets
python src/data_extraction/create_unified_real_data.py

# 3. Launch dashboard
./launch_enhanced_dash.sh        # For Dash
# OR
./launch_enhanced_streamlit.sh   # For Streamlit
```

---

## 🎯 **Result**

**Before Cleanup**: 4 launch scripts (2 broken, 2 working)
**After Cleanup**: 2 launch scripts (both fully functional)

The HungerHub POC now has **clean, working launch scripts** that:
- ✅ Reference only active dashboard files
- ✅ Use correct file paths
- ✅ Include proper logging and process management  
- ✅ Work from any directory location

---

*Launch scripts cleanup completed by Agent Mode on 2025-08-13*
