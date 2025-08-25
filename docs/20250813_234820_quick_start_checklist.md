# ⚡ HungerHub POC - Quick Start Checklist

**For Developers**: Print this checklist for easy reference during setup

---

## 🔐 SSH Setup (One-time)

### Pre-Setup
- [ ] VS Code installed
- [ ] Remote-SSH extension installed
- [ ] SSH private key file received from project lead

### SSH Configuration
- [ ] Open VS Code Command Palette (`Ctrl+Shift+P`)
- [ ] Run: "Remote-SSH: Open Configuration File"
- [ ] Add configuration block:
```
Host hungerhub-vm
    HostName 20.25.118.217
    User tagazureuser
    IdentityFile ~/.ssh/hungerhub_key
```
- [ ] Save SSH key as `~/.ssh/hungerhub_key` (or Windows equivalent)
- [ ] Set key permissions: `chmod 600 ~/.ssh/hungerhub_key` (Mac/Linux)

### Connection Test
- [ ] Command Palette → "Remote-SSH: Connect to Host"
- [ ] Select "hungerhub-vm"
- [ ] Wait for VS Code Server installation
- [ ] Open folder: `/home/tagazureuser/cgorr/2week_poc_execution/hungerhub_poc`

---

## 🚀 Launch Dashboards

### Terminal Setup
- [ ] Open VS Code terminal (`Ctrl+Shift+` `)
- [ ] Verify location: `pwd` shows project directory
- [ ] Make scripts executable: `chmod +x *.sh`

### Dash Dashboard (Primary)
- [ ] Run: `./launch_dash_dashboard.sh`
- [ ] Wait for: "Dashboard will be available at: http://localhost:8050"
- [ ] Check VS Code ports view for port forwarding
- [ ] Open: `http://localhost:8050`
- [ ] Verify: "✅ Using Real Oracle Data" message

### Streamlit Dashboard (Alternative)  
- [ ] Open new terminal tab
- [ ] Run: `./run_streamlit_app.sh`
- [ ] Wait for: "Streamlit Dashboard will be available at: http://localhost:8503"
- [ ] Open: `http://localhost:8503`
- [ ] Verify: "✅ Using Real Oracle Data" message

---

## ✅ Success Verification

### Connection Success
- [ ] VS Code status bar shows: "SSH: hungerhub-vm"
- [ ] Can see project files in VS Code Explorer
- [ ] Terminal shows: "tagazureuser@hungerhub-vm:"

### Dashboard Success
- [ ] Dash app loads with professional dark theme
- [ ] Streamlit app loads with clean sidebar interface
- [ ] Both show green "Using Real Oracle Data" status
- [ ] Can see: ~5,000 donations, ~2,500 organizations
- [ ] All navigation pages work (Executive Summary, Analytics, etc.)

### Data Success
- [ ] KPI numbers are realistic (not 1,000 mock entries)
- [ ] Charts show real date ranges (2018-2024)
- [ ] Donor names are realistic (Tyson, etc.)
- [ ] Geographic data shows real locations

---

## 🚨 Quick Troubleshooting

**Can't connect?**
- Check SSH key path and permissions
- Verify VM IP: `ping 20.25.118.217`

**Dashboard won't start?**
- Verify directory: `pwd`
- Check data files: `ls data/processed/unified_real/`
- Restart: `Ctrl+C` then re-run script

**Browser shows nothing?**
- Check VS Code ports view
- Hard refresh: `Ctrl+F5`
- Try incognito mode

**Still shows mock data?**
- Kill all processes: `pkill -f streamlit`
- Clear browser cache
- Re-run dashboard script

---

**Need Help?** Check `docs/DEVELOPER_SETUP_GUIDE.md` for detailed instructions

**Project Status**: ✅ Both dashboards operational with real Oracle data!
