# 🚀 HungerHub POC - Developer Setup Guide

**Document Version**: 1.0  
**Last Updated**: August 7, 2025  
**Target Audience**: Peer Developers  

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ Visual Studio Code installed
- ✅ VS Code SSH extension installed (`Remote - SSH`)
- ✅ SSH private key file provided by project lead
- ✅ Basic familiarity with VS Code and terminal usage

---

## 🔐 Step 1: SSH Connection Setup in VS Code

### 1.1 Install Required VS Code Extensions
1. Open VS Code
2. Go to Extensions (`Ctrl+Shift+X` or `Cmd+Shift+X`)
3. Search for and install: **"Remote - SSH"** by Microsoft
4. Restart VS Code if prompted

### 1.2 Configure SSH Connection
1. **Open Command Palette**: `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: **"Remote-SSH: Open Configuration File"**
3. Select your SSH config file (usually `~/.ssh/config`)
4. Add the following configuration:

```ssh-config
Host hungerhub-vm
    HostName 20.25.118.217
    User tagazureuser
    Port 22
    IdentityFile ~/.ssh/hungerhub_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

### 1.3 Setup SSH Key
1. **Save the SSH private key** provided by project lead as:
   - **Windows**: `C:\Users\[YourUsername]\.ssh\hungerhub_key`
   - **Mac/Linux**: `~/.ssh/hungerhub_key`

2. **Set proper permissions** (Mac/Linux only):
   ```bash
   chmod 600 ~/.ssh/hungerhub_key
   ```

3. **Windows Users**: Ensure the key file has restricted permissions:
   - Right-click the key file → Properties → Security
   - Remove all users except your account
   - Give your account "Full Control"

### 1.4 Connect to VM
1. **Open Command Palette**: `Ctrl+Shift+P`
2. Type: **"Remote-SSH: Connect to Host"**
3. Select: **"hungerhub-vm"**
4. VS Code will open a new window connected to the VM
5. **First connection**: VS Code will install the VS Code Server (wait for completion)

---

## 📁 Step 2: Navigate to Project Directory

### 2.1 Open Project Folder
1. In the connected VS Code window, click **"Open Folder"**
2. Navigate to: `/home/tagazureuser/cgorr/2week_poc_execution/hungerhub_poc`
3. Click **"OK"** to open the project

### 2.2 Verify Project Structure
You should see the following folders:
```
hungerhub_poc/
├── src/
│   └── dashboard/
│       ├── dash/
│       └── streamlit/
├── data/
├── ai_collaboration/
├── docs/
├── venv/
└── [other folders...]
```

---

## 🖥️ Step 3: Running the Dashboard Applications

### 3.1 Open VS Code Terminal
1. In VS Code: **Terminal** → **New Terminal** (`Ctrl+Shift+` ` or `Cmd+Shift+` `)
2. Terminal should open in the project root directory
3. Verify location: `pwd` should show `/home/tagazureuser/cgorr/2week_poc_execution/hungerhub_poc`

### 3.2 Run Plotly Dash Dashboard (Primary)
```bash
# Make script executable (first time only)
chmod +x launch_dash_dashboard.sh

# Launch the Dash application
./launch_dash_dashboard.sh
```

**Expected Output**:
```
🍽️ Starting HungerHub Analytics Dashboard...
✅ Real Oracle data found
🌐 Dashboard will be available at: http://localhost:8050
📊 Use Ctrl+C to stop the dashboard
```

### 3.3 Run Streamlit Dashboard (Alternative)
**Open a new terminal tab**: `Ctrl+Shift+5` (or Terminal → New Terminal)

```bash
# Make script executable (first time only)
chmod +x run_streamlit_app.sh

# Launch the Streamlit application
./run_streamlit_app.sh
```

**Expected Output**:
```
🍽️ Starting HungerHub Streamlit Dashboard...
✅ Real Oracle data found - same as Dash app
🌐 Streamlit Dashboard will be available at: http://localhost:8503
📊 Use Ctrl+C to stop the dashboard
```

---

## 🌐 Step 4: Access Dashboards in Your Browser

### 4.1 Setup Port Forwarding (Automatic in VS Code)
When you run the applications, VS Code should automatically detect the ports and offer to forward them. Look for notifications like:

**"Your application running on port 8050 is available. [Open in Browser]"**

### 4.2 Manual Port Forwarding (if needed)
1. **Open Command Palette**: `Ctrl+Shift+P`
2. Type: **"Ports: Focus on Ports View"**
3. Click the **"+"** button to add a port
4. Enter port numbers:
   - **8050** (for Dash dashboard)
   - **8503** (for Streamlit dashboard)

### 4.3 Access Applications
Click the links VS Code provides, or manually open:

#### **Primary Dash Dashboard**:
- **Local URL**: `http://localhost:8050`
- **Features**: Production-ready, comprehensive analytics
- **Pages**: Executive Summary, Donation Analytics, Organization Management

#### **Alternative Streamlit Dashboard**:
- **Local URL**: `http://localhost:8503`  
- **Features**: Interactive, user-friendly interface
- **Pages**: Executive Summary, Donation Analytics, Organization Management, Data Overview

---

## 🔧 Troubleshooting

### Connection Issues
**Problem**: Cannot connect to SSH
**Solutions**:
1. Verify SSH key file path and permissions
2. Check if VM IP address is accessible: `ping 20.25.118.217`
3. Ensure VS Code Remote-SSH extension is installed
4. Try connecting via terminal first: `ssh -i ~/.ssh/hungerhub_key tagazureuser@20.25.118.217`

### Dashboard Won't Start
**Problem**: Shell scripts fail to run
**Solutions**:
1. Ensure you're in the project root directory: `pwd`
2. Make scripts executable: `chmod +x *.sh`
3. Check virtual environment: `source venv/bin/activate`
4. Verify data files exist: `ls -la data/processed/unified_real/`

### Port Forwarding Issues
**Problem**: Cannot access localhost URLs
**Solutions**:
1. Check VS Code ports view: `Ctrl+Shift+P` → "Ports: Focus on Ports View"
2. Manually add ports 8050 and 8503
3. Ensure applications are running (check terminal output)
4. Try accessing via VS Code's "Simple Browser": `Ctrl+Shift+P` → "Simple Browser: Show"

### Browser Shows Old Content
**Problem**: Dashboard shows cached or incorrect data
**Solutions**:
1. **Hard refresh**: `Ctrl+F5` (or `Cmd+Shift+R` on Mac)
2. **Clear browser cache** for localhost
3. **Use incognito/private mode**
4. **Restart the dashboard application** (Ctrl+C, then re-run script)

---

## 📊 What You Should See

### ✅ Successful Connection Indicators
- VS Code status bar shows: **"SSH: hungerhub-vm"**
- Terminal prompt shows: **"tagazureuser@hungerhub-vm:"**
- Project files visible in VS Code Explorer

### ✅ Working Dashboard Indicators
- **Dash App**: Professional dark theme with multi-page navigation
- **Streamlit App**: Clean interface with sidebar navigation
- **Both apps show**: "✅ Using Real Oracle Data"
- **Data visible**: 5,000+ donations, 2,500+ organizations

### 📈 Expected Dashboard Features
- **Executive Summary**: KPI cards, trend charts, geographic maps
- **Donation Analytics**: Time series, donor rankings, distribution analysis
- **Organization Management**: Status breakdowns, performance metrics
- **Interactive Elements**: Filters, date selectors, drill-down capabilities

---

## 🆘 Getting Help

### Contact Information
- **Project Lead**: [Your contact information]
- **Technical Issues**: Check `ai_collaboration/` folder for technical documentation
- **Data Questions**: Review `data/` folder structure and processing logs

### Useful Commands
```bash
# Check if services are running
ps aux | grep -E "(dash|streamlit)"

# Kill all dashboard processes
pkill -f dash
pkill -f streamlit

# Restart virtual environment
source venv/bin/activate

# Check data files
ls -la data/processed/unified_real/

# View application logs
ls -la logs/
```

### Documentation References
- **Project Status**: `ai_collaboration/shared_context/current_project_status.md`
- **Technical Architecture**: `ai_collaboration/agent_mode_reports/`
- **POC Timeline**: `/home/tagazureuser/cgorr/2week_poc_execution/01_poc_planning/HungerHub_Accelerated_2Week_POC.md`

---

## 🎯 Success Checklist

After completing this setup, you should be able to:

- [ ] ✅ Connect to the VM via VS Code SSH
- [ ] ✅ Navigate the project directory structure  
- [ ] ✅ Run both dashboard applications
- [ ] ✅ Access dashboards in your local browser
- [ ] ✅ See real Oracle data in both applications
- [ ] ✅ Navigate between different dashboard pages
- [ ] ✅ Interact with visualizations and filters

**Welcome to the HungerHub POC development environment!** 🚀

---

**Document Created**: August 7, 2025  
**VM Details**: Ubuntu 22.04, Python 3.13, Oracle Integration  
**Project Status**: Week 2, Day 8+ (Ahead of Schedule)  
