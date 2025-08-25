// HungerHub Static Dashboard JavaScript
// Real data visualization using Plotly.js

// Global data storage
let dashboardData = {};

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing HungerHub Static Dashboard');
    loadAllData();
});

// Load all JSON data files
async function loadAllData() {
    try {
        const sections = ['section1', 'section2', 'section3', 'section4'];
        const promises = sections.map(section => 
            fetch(`./data/${section}_data.json`)
                .then(response => response.json())
                .then(data => {
                    dashboardData[section] = data;
                    console.log(`✅ Loaded ${section} data`);
                })
                .catch(error => {
                    console.error(`❌ Failed to load ${section} data:`, error);
                })
        );
        
        await Promise.all(promises);
        console.log('📊 All data loaded successfully');
        
        // Initialize all sections
        initializeSection1();
        initializeSection2();
        initializeSection3();
        initializeSection4();
        
    } catch (error) {
        console.error('❌ Error loading dashboard data:', error);
    }
}

// Tab switching functionality
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Activate clicked tab
    event.target.closest('.tab').classList.add('active');
    
    // Resize charts when section becomes visible
    setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
    }, 100);
}

// Section 1: Donor Analysis
function initializeSection1() {
    if (!dashboardData.section1) return;
    
    const data = dashboardData.section1;
    
    // Create donor performance chart
    createDonorPerformanceChart(data.donor_performance);
    
    // Create metrics cards
    createMetricsCards(data.metrics);
    
    // Create monthly trends chart
    createMonthlyTrendsChart(data.monthly_trends);
    
    // Create trends analytics
    createTrendsAnalytics(data.monthly_trends, data.metrics);
    
    console.log('✅ Section 1 initialized');
}

function createDonorPerformanceChart(data) {
    const trace1 = {
        x: data.weights_tons,
        y: data.donors,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: '#3b82f6',
            line: {
                color: '#1d4ed8',
                width: 1
            }
        },
        name: 'Total Weight (tons)',
        text: data.weights_tons.map((val, i) => 
            `${val.toLocaleString()} tons<br>${data.weights_lbs[i].toLocaleString()} lbs`
        ),
        textposition: 'auto',
        hovertemplate: '<b>%{y}</b><br>' +
                      'Weight: %{x:.1f} tons<br>' +
                      'Pounds: %{customdata:,} lbs<extra></extra>',
        customdata: data.weights_lbs
    };
    
    const layout = {
        title: {
            text: 'Top Donor Performance by Total Weight',
            font: { size: 16, color: '#1f2937' }
        },
        xaxis: {
            title: 'Total Weight (metric tons)',
            gridcolor: '#e5e7eb'
        },
        yaxis: {
            title: '',
            automargin: true
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 140, r: 20, t: 60, b: 60 },
        height: 500
    };
    
    Plotly.newPlot('donor-performance-chart', [trace1], layout, {
        responsive: true,
        displayModeBar: false
    });
}

function createMetricsCards(metrics) {
    const metricsHtml = `
        <div class="metric-card">
            <span class="metric-value">${metrics.total_donors.toLocaleString()}</span>
            <div class="metric-label">Total Donors</div>
        </div>
        <div class="metric-card">
            <span class="metric-value">${metrics.total_weight_tons.toLocaleString()}</span>
            <div class="metric-label">Total Weight (tons)</div>
        </div>
        <div class="metric-card">
            <span class="metric-value">${(metrics.total_weight_lbs / 1000000).toFixed(1)}M</span>
            <div class="metric-label">Total Weight (lbs)</div>
        </div>
        <div class="metric-card">
            <span class="metric-value">${(metrics.avg_weight_per_donor_lbs / 1000).toFixed(0)}K</span>
            <div class="metric-label">Avg per Donor (lbs)</div>
        </div>
        <div class="metric-card">
            <span class="metric-value">${metrics.top_10_percentage}%</span>
            <div class="metric-label">Top 10 Contribution</div>
        </div>
    `;
    
    document.getElementById('donor-metrics').innerHTML = metricsHtml;
}

function createMonthlyTrendsChart(data) {
    const trace1 = {
        x: data.dates,
        y: data.donation_counts,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Monthly Donations',
        line: { color: '#10b981', width: 2 },
        marker: { size: 4 },
        yaxis: 'y1'
    };
    
    const trace2 = {
        x: data.dates,
        y: data.weights_lbs.map(w => w / 1000), // Convert to thousands
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Total Weight (1000s lbs)',
        line: { color: '#3b82f6', width: 2 },
        marker: { size: 4 },
        yaxis: 'y2'
    };
    
    const trace3 = {
        x: data.dates,
        y: data.quantities.map(q => q / 1000), // Convert to thousands
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Total Quantities (1000s)',
        line: { color: '#f59e0b', width: 2 },
        marker: { size: 4 },
        yaxis: 'y3'
    };
    
    const layout = {
        title: {
            text: 'Monthly Donation Trends (8+ Years)',
            font: { size: 16, color: '#1f2937' }
        },
        xaxis: {
            title: 'Month-Year',
            gridcolor: '#e5e7eb'
        },
        yaxis: {
            title: 'Donation Count',
            titlefont: { color: '#10b981' },
            tickfont: { color: '#10b981' },
            domain: [0.67, 1]
        },
        yaxis2: {
            title: 'Weight (1000s lbs)',
            titlefont: { color: '#3b82f6' },
            tickfont: { color: '#3b82f6' },
            domain: [0.33, 0.66],
            anchor: 'x'
        },
        yaxis3: {
            title: 'Quantities (1000s)',
            titlefont: { color: '#f59e0b' },
            tickfont: { color: '#f59e0b' },
            domain: [0, 0.32],
            anchor: 'x'
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 60, r: 20, t: 60, b: 60 },
        height: 500,
        legend: {
            x: 1.02,
            y: 1,
            xanchor: 'left'
        }
    };
    
    Plotly.newPlot('monthly-trends-chart', [trace1, trace2, trace3], layout, {
        responsive: true,
        displayModeBar: false
    });
}

function createTrendsAnalytics(trendsData, metrics) {
    // Calculate trend analytics
    const totalMonths = trendsData.dates.length;
    const avgDonationsPerMonth = trendsData.donation_counts.reduce((a, b) => a + b, 0) / totalMonths;
    const maxDonations = Math.max(...trendsData.donation_counts);
    const minDonations = Math.min(...trendsData.donation_counts);
    
    const avgWeightPerMonth = trendsData.weights_lbs.reduce((a, b) => a + b, 0) / totalMonths;
    
    const analyticsHtml = `
        <div class="metric-card">
            <span class="metric-value">${totalMonths}</span>
            <div class="metric-label">Months Tracked</div>
        </div>
        <div class="metric-card">
            <span class="metric-value">${avgDonationsPerMonth.toFixed(0)}</span>
            <div class="metric-label">Avg Donations/Month</div>
        </div>
        <div class="metric-card">
            <span class="metric-value">${maxDonations}</span>
            <div class="metric-label">Peak Monthly Donations</div>
        </div>
        <div class="metric-card">
            <span class="metric-value">${(avgWeightPerMonth / 1000).toFixed(0)}K</span>
            <div class="metric-label">Avg Weight/Month (lbs)</div>
        </div>
    `;
    
    document.getElementById('trends-analytics').innerHTML = analyticsHtml;
}

// Section 2: Items & Quantities
function initializeSection2() {
    if (!dashboardData.section2) return;
    
    const data = dashboardData.section2;
    
    // Create storage composition charts
    createStorageQuantityChart(data.storage_quantity);
    createStorageWeightChart(data.storage_weight);
    
    console.log('✅ Section 2 initialized');
}

function createStorageQuantityChart(data) {
    const trace = {
        labels: data.storage_types,
        values: data.quantities,
        type: 'pie',
        marker: {
            colors: ['#d62728', '#87CEEB', '#000080'], // Red, Light Blue, Navy Blue
        },
        textinfo: 'label+percent',
        textposition: 'auto',
        hovertemplate: '<b>%{label}</b><br>' +
                      'Quantity: %{value:,}<br>' +
                      'Percentage: %{percent}<extra></extra>'
    };
    
    const layout = {
        title: {
            text: 'Storage Composition by Quantity',
            font: { size: 16, color: '#1f2937' }
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 20, r: 20, t: 60, b: 20 },
        height: 400
    };
    
    Plotly.newPlot('storage-quantity-chart', [trace], layout, {
        responsive: true,
        displayModeBar: false
    });
}

function createStorageWeightChart(data) {
    const trace = {
        labels: data.storage_types,
        values: data.weights_lbs,
        type: 'pie',
        marker: {
            colors: ['#d62728', '#87CEEB', '#000080'], // Red, Light Blue, Navy Blue
        },
        textinfo: 'label+percent',
        textposition: 'auto',
        hovertemplate: '<b>%{label}</b><br>' +
                      'Weight: %{value:,} lbs<br>' +
                      'Tons: %{customdata:.1f}<br>' +
                      'Percentage: %{percent}<extra></extra>',
        customdata: data.weights_tons
    };
    
    const layout = {
        title: {
            text: 'Storage Composition by Total Weight',
            font: { size: 16, color: '#1f2937' }
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 20, r: 20, t: 60, b: 20 },
        height: 400
    };
    
    Plotly.newPlot('storage-weight-chart', [trace], layout, {
        responsive: true,
        displayModeBar: false
    });
}

// Section 3: Bidding Analytics
function initializeSection3() {
    if (!dashboardData.section3) return;
    
    const data = dashboardData.section3;
    
    // Create states ranking and Sankey charts
    createStatesRankingChart(data.states_ranking);
    createSankeyDiagram(data.sankey);
    
    console.log('✅ Section 3 initialized');
}

function createStatesRankingChart(data) {
    const trace = {
        x: data.weights_tons,
        y: data.states,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: '#10b981',
            line: {
                color: '#059669',
                width: 1
            }
        },
        text: data.weights_tons.map(val => `${val.toFixed(1)}t`),
        textposition: 'auto',
        hovertemplate: '<b>%{y}</b><br>' +
                      'Weight: %{x:.1f} tons<br>' +
                      'Pounds: %{customdata:,} lbs<extra></extra>',
        customdata: data.weights_lbs
    };
    
    const layout = {
        title: {
            text: 'Top 10 States by Total Weight Distribution',
            font: { size: 16, color: '#1f2937' }
        },
        xaxis: {
            title: 'Total Weight (metric tons)',
            gridcolor: '#e5e7eb'
        },
        yaxis: {
            title: '',
            automargin: true
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 60, r: 20, t: 60, b: 60 },
        height: 400
    };
    
    Plotly.newPlot('states-ranking-chart', [trace], layout, {
        responsive: true,
        displayModeBar: false
    });
}

function createSankeyDiagram(data) {
    const trace = {
        type: 'sankey',
        node: {
            pad: 15,
            thickness: 20,
            line: {
                color: 'black',
                width: 0.5
            },
            label: data.labels,
            color: [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', // Donors
                '#8c564b', '#e377c2', '#7f7f7f', // Storage
                '#bcbd22', '#17becf', '#aec7e8', '#ffbb78' // Recipients
            ]
        },
        link: {
            source: data.sources,
            target: data.targets,
            value: data.values,
            color: 'rgba(255, 255, 255, 0.4)'
        }
    };
    
    const layout = {
        title: {
            text: 'Food Flow: Donors → Storage → Recipients',
            font: { size: 16, color: '#1f2937' }
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 20, r: 20, t: 60, b: 20 },
        height: 400
    };
    
    Plotly.newPlot('sankey-chart', [trace], layout, {
        responsive: true,
        displayModeBar: false
    });
}

// Section 4: Geographic Distribution
function initializeSection4() {
    if (!dashboardData.section4) return;
    
    const data = dashboardData.section4;
    
    // Create choropleth map
    createChoroplethMap(data.choropleth);
    
    console.log('✅ Section 4 initialized');
}

function createChoroplethMap(data) {
    const choroplethTrace = {
        type: 'choropleth',
        locations: data.state_codes,
        z: data.weights_tons,
        locationmode: 'USA-states',
        colorscale: [
            [0, '#f0f9ff'],
            [0.2, '#bae6fd'],
            [0.4, '#7dd3fc'],
            [0.6, '#38bdf8'],
            [0.8, '#0ea5e9'],
            [1, '#0284c7']
        ],
        colorbar: {
            title: 'Total Weight (tons)',
            thickness: 15,
            len: 0.7
        },
        hovertemplate: '<b>%{location}</b><br>' +
                      'Weight: %{z:.1f} tons<br>' +
                      'Pounds: %{customdata[0]:,} lbs<br>' +
                      'Organizations: %{customdata[1]}<extra></extra>',
        customdata: data.weights_lbs.map((w, i) => [w, data.org_counts[i]])
    };
    
    const scatterTrace = {
        type: 'scattergo',
        mode: 'markers',
        lon: getStateLongitudes(data.state_codes),
        lat: getStateLatitudes(data.state_codes),
        marker: {
            size: data.org_counts.map(count => Math.max(6, count / 1.2)), // Larger bubbles
            color: '#dc2626',
            opacity: 0.7,
            line: {
                color: 'white',
                width: 1
            }
        },
        text: data.state_codes.map((state, i) => 
            `${state}: ${data.org_counts[i]} organizations`
        ),
        hovertemplate: '<b>%{text}</b><extra></extra>',
        name: 'Organizations'
    };
    
    const layout = {
        title: {
            text: 'U.S. Geographic Distribution by Total Weight',
            font: { size: 16, color: '#1f2937' }
        },
        geo: {
            scope: 'usa',
            projection: { type: 'albers usa' },
            showlakes: true,
            lakecolor: 'rgb(255, 255, 255)'
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        margin: { l: 20, r: 20, t: 60, b: 20 },
        height: 500
    };
    
    Plotly.newPlot('choropleth-map', [choroplethTrace, scatterTrace], layout, {
        responsive: true,
        displayModeBar: false
    });
}

// Helper function to get approximate state center coordinates
function getStateLatitudes(stateCodes) {
    const stateCoords = {
        'CA': 36.7783, 'TX': 31.9686, 'FL': 27.7663, 'NY': 40.7128, 'IL': 40.6331,
        'PA': 41.2033, 'OH': 40.3888, 'GA': 33.7490, 'NC': 35.7596, 'MI': 44.3148,
        'VA': 37.4316, 'WA': 47.7511, 'AZ': 34.0489, 'TN': 35.7796, 'IN': 40.2732,
        'MO': 37.9643, 'MD': 39.0458, 'WI': 44.2619, 'CO': 39.5501, 'MN': 46.7296,
        'AL': 32.3617, 'SC': 33.8361, 'LA': 31.2444, 'KY': 37.8393, 'OR': 43.8041,
        'OK': 35.0078, 'CT': 41.7658, 'IA': 41.8780, 'MS': 32.3547, 'AR': 35.2010,
        'KS': 39.0119, 'UT': 39.3210, 'NV': 38.8026, 'NM': 34.8405, 'WV': 37.7859,
        'NE': 41.4925, 'ID': 44.0682, 'NH': 43.1939, 'HI': 19.8968, 'RI': 41.6809,
        'MT': 46.8797, 'DE': 38.9108, 'SD': 43.9695, 'ND': 47.5515, 'AK': 64.0685,
        'VT': 44.5588, 'WY': 43.0759, 'DC': 38.9072, 'ME': 45.2538
    };
    return stateCodes.map(code => stateCoords[code] || 0);
}

function getStateLongitudes(stateCodes) {
    const stateCoords = {
        'CA': -119.4179, 'TX': -99.9018, 'FL': -82.6404, 'NY': -74.0060, 'IL': -89.3985,
        'PA': -77.1945, 'OH': -82.7649, 'GA': -84.3880, 'NC': -79.0193, 'MI': -84.5467,
        'VA': -78.6569, 'WA': -120.7401, 'AZ': -111.0937, 'TN': -86.6876, 'IN': -86.1349,
        'MO': -92.6038, 'MD': -76.6413, 'WI': -89.6165, 'CO': -105.7821, 'MN': -94.6859,
        'AL': -86.7816, 'SC': -81.1637, 'LA': -92.1449, 'KY': -84.2700, 'OR': -120.5542,
        'OK': -97.0929, 'CT': -72.6851, 'IA': -93.0977, 'MS': -89.3985, 'AR': -92.3341,
        'KS': -98.4842, 'UT': -111.0937, 'NV': -116.4194, 'NM': -106.2485, 'WV': -81.6326,
        'NE': -99.9018, 'ID': -114.7420, 'NH': -71.5376, 'HI': -155.5828, 'RI': -71.4774,
        'MT': -110.3626, 'DE': -75.5277, 'SD': -99.9018, 'ND': -100.7837, 'AK': -153.0063,
        'VT': -72.5806, 'WY': -107.5024, 'DC': -77.0369, 'ME': -69.4455
    };
    return stateCodes.map(code => stateCoords[code] || 0);
}
