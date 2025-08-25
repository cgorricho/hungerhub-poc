# 🖥️ HungerHub POC - VM Connection Reference

**For Project Distribution**: Share this with peer developers along with SSH private key

---

## 📋 Connection Details

### Azure VM Information
```
IP Address: 20.25.118.217
Username: tagazureuser
Port: 22 (default SSH)
OS: Ubuntu 22.04 LTS
```

### SSH Key Requirements
- **Key Type**: RSA private key
- **File Location**: `~/.ssh/hungerhub_key` (or Windows equivalent)
- **Permissions**: 600 (Mac/Linux) or restricted access (Windows)
- **Status**: Provided separately by project lead

### VS Code SSH Configuration Block
```ssh-config
Host hungerhub-vm
    HostName 20.25.118.217
    User tagazureuser
    Port 22
    IdentityFile ~/.ssh/hungerhub_key
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

---

## 🗂️ Project Paths

### Main Project Directory
```
/home/tagazureuser/cgorr/2week_poc_execution/hungerhub_poc/
```

### Key Directories
```
├── src/dashboard/          # Dashboard applications
│   ├── dash/              # Plotly Dash app
│   └── streamlit/         # Streamlit app
├── data/processed/        # Real Oracle data
├── docs/                  # Documentation
├── venv/                  # Python virtual environment
└── ai_collaboration/      # AI development reports
```

---

## 🚀 Dashboard Applications

### Available Applications
| Application | Port | URL | Status |
|-------------|------|-----|--------|
| Plotly Dash | 8050 | `http://localhost:8050` | ✅ Primary |
| Streamlit | 8503 | `http://localhost:8503` | ✅ Alternative |

### Launch Scripts
```bash
# Plotly Dash (Primary)
./launch_dash_dashboard.sh

# Streamlit (Alternative)  
./run_streamlit_app.sh
```

---

## 📊 Expected Data

### Real Oracle Data Status
- **Total Donations**: ~5,000 records
- **Total Organizations**: ~2,500 records
- **Date Range**: 2018-2024
- **Data Sources**: Choice Oracle + Agency Oracle
- **Status Indicator**: "✅ Using Real Oracle Data"

### Mock Data Warning
If you see "⚠️ Using Mock Data", there's an issue:
- Dashboard not loading real data files
- Need to troubleshoot connection or file paths
- Should show realistic numbers, not 1,000 mock entries

---

## 🔐 Security Notes

### SSH Key Security
- **DO NOT** commit SSH keys to version control
- **DO NOT** share private keys via email/slack
- **DO** store keys in secure local location
- **DO** use proper file permissions

### VM Access
- VM is configured for development access only
- Contains non-production, POC-level data
- Suitable for demonstration and development
- Not for production data processing

---

## ✅ Success Indicators

### Connection Success
- VS Code connects without password prompt
- Status bar shows "SSH: hungerhub-vm"
- Can browse project files in VS Code Explorer

### Application Success  
- Dashboards load with professional interfaces
- Green "Using Real Oracle Data" status visible
- Realistic data numbers (5K donations, 2.5K orgs)
- All navigation pages functional

### Development Ready
- Both dashboard frameworks accessible
- Real data integration working
- Port forwarding automatic in VS Code
- Ready for development and demonstration

---

**Shared**: August 7, 2025  
**Project**: HungerHub POC (Week 2, Day 8+)  
**Status**: ✅ Production-ready development environment
