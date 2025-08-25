# HungerHub Static Dashboard

A static HTML version of the HungerHub Dashboard that replicates all functionality from the Dash application without requiring a server runtime.

## 🎯 Overview

This static dashboard provides comprehensive food donation analytics with the same visualizations as the dynamic Dash app:

- **Section 1: Donor Analysis** - Top donor performance, metrics, and monthly trends
- **Section 2: Items & Quantities** - Storage composition by quantity and weight  
- **Section 3: Bidding Analytics** - State rankings and food flow Sankey diagrams
- **Section 4: Geographic Distribution** - US choropleth map with organization bubbles

## 📁 File Structure

```
static/
├── hungerhub_dashboard.html    # Main dashboard file
├── assets/
│   └── dashboard.js            # JavaScript for data loading and chart creation
├── data/                       # JSON data files
│   ├── section1_data.json      # Donor analysis data
│   ├── section2_data.json      # Storage composition data  
│   ├── section3_data.json      # Bidding analytics data
│   ├── section4_data.json      # Geographic data
│   └── generation_summary.json # Data generation metadata
└── generate_data.py            # Script to generate JSON data from Oracle sources
```

## 🚀 Usage

### Option 1: Local File Server (Recommended)
```bash
# Navigate to static directory
cd src/dashboard/static

# Start local server on port 8080
python3 -m http.server 8080

# Open browser to:
# http://localhost:8080/hungerhub_dashboard.html
```

### Option 2: Direct File Access
Simply open `hungerhub_dashboard.html` in a modern web browser. Note: Some features may require a local server due to CORS restrictions.

### Option 3: Deploy to Web Server
Upload all files to any web server and access the HTML file directly.

## 🔧 Data Updates

To update the dashboard with fresh data:

```bash
# Navigate to project root
cd /path/to/hungerhub_poc

# Run data generation script
python src/dashboard/static/generate_data.py
```

This will:
- Load real Oracle data from the processed datasets
- Generate JSON files with the latest donation metrics
- Update all visualization data automatically

## ✨ Features

### Interactive Elements
- **Tab Navigation**: Switch between 4 main sections
- **Hover Details**: Rich tooltips on all charts
- **Responsive Design**: Works on desktop and mobile devices
- **Fast Loading**: No server dependencies, instant rendering

### Visualizations
- **Bar Charts**: Donor performance and state rankings
- **Pie Charts**: Storage composition analysis  
- **Line Charts**: Multi-metric monthly trends over 8+ years
- **Sankey Diagrams**: Food flow from donors to recipients
- **Choropleth Maps**: Geographic weight distribution with organization bubbles

### Data Accuracy
- **Real Oracle Data**: Same data sources as the Dash application
- **Comprehensive Coverage**: 247 donors, 8+ years of historical data
- **Multiple Metrics**: Weights, quantities, donation counts, and percentages

## 🎨 Customization

### Styling
The dashboard uses CSS variables for easy theme customization. Edit the `:root` section in the HTML file:

```css
:root {
    --primary: #1f2937;      /* Dark gray */
    --accent: #3b82f6;       /* Blue */
    --success: #10b981;      /* Green */
    /* ... more variables ... */
}
```

### Data Structure
Each JSON file follows a consistent structure:

```json
{
    "section_data": {
        "chart_type": {
            "labels": ["..."],
            "values": [...]
        }
    },
    "generated_at": "2024-08-21T17:22:43.123456"
}
```

## 🔍 Browser Compatibility

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

Requires modern JavaScript support for:
- ES6 async/await
- Fetch API
- CSS Grid/Flexbox

## 📊 Performance

- **Load Time**: < 2 seconds (including all charts)
- **File Size**: ~45KB total (HTML + JS + CSS)
- **Data Size**: ~11KB JSON data
- **Memory Usage**: ~50MB (Plotly.js charts)

## 🚨 Limitations

Compared to the dynamic Dash app, the static version:
- No real-time data filtering (shows all data)
- No server-side computations
- Data updates require regeneration
- Limited to pre-calculated datasets

## 📈 Future Enhancements

Potential improvements for the static dashboard:
- Client-side filtering capabilities
- Data export functionality  
- Print-optimized layouts
- Offline caching with service workers
- Progressive web app (PWA) features

## 🔒 Security

This static dashboard:
- Contains no sensitive data (aggregated metrics only)
- Requires no authentication
- Makes no external API calls
- Safe for public deployment

## 📞 Support

For issues or questions:
- Review browser developer console for errors
- Check that all files are properly served
- Verify JSON data files are valid
- Test with different browsers

---

**Generated**: August 21, 2024  
**Version**: 1.0  
**Data Source**: HungerHub Oracle Database (Real Production Data)
