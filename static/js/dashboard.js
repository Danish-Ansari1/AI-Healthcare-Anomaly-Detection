// Initialize Charts
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Inter', sans-serif";

const vitalsCtx = document.getElementById('vitalsChart').getContext('2d');
const vitalsChart = new Chart(vitalsCtx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Heart Rate (bpm)',
                borderColor: '#3b82f6',
                data: [],
                tension: 0.4,
                borderWidth: 2
            },
            {
                label: 'SpO2 (%)',
                borderColor: '#10b981',
                data: [],
                tension: 0.4,
                borderWidth: 2
            }
        ]
    },
    options: {
        responsive: true,
        animation: { duration: 0 },
        scales: {
            x: { display: false },
            y: {
                beginAtZero: false,
                grid: { color: 'rgba(255,255,255,0.05)' }
            }
        },
        plugins: {
            legend: { position: 'top' }
        }
    }
});

const anomalyCtx = document.getElementById('anomalyChart').getContext('2d');
const anomalyChart = new Chart(anomalyCtx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Anomaly Score',
            backgroundColor: [],
            data: [],
            borderRadius: 4
        }]
    },
    options: {
        responsive: true,
        animation: { duration: 0 },
        scales: {
            x: { display: false },
            y: { grid: { color: 'rgba(255,255,255,0.05)' } }
        }
    }
});

// Fetch Data Periodic Polling
async function updateDashboard() {
    try {
        // --- 1. Stats Update (Backend keys se match kiya gaya) ---
        const statsRes = await fetch('/api/stats');
        const statsData = await statsRes.json();
        if (statsData.status === 'success') {
            // Note: backend se 'total_pts', 'high_alerts', 'med_alerts' aa raha hai
            document.getElementById('total-patients').textContent = statsData.data.total_pts || 0;
            document.getElementById('high-alerts').textContent = statsData.data.high_alerts || 0;
            document.getElementById('medium-alerts').textContent = statsData.data.med_alerts || 0;
        }

        // --- 2. Vitals & Table Update ---
        const vitalsRes = await fetch('/api/vitals');
        const vitalsData = await vitalsRes.json();
        
        if (vitalsData.status === 'success' && vitalsData.data.length > 0) {
            const records = [...vitalsData.data].slice(0, 20).reverse(); // Last 20 for chart
            
            // Update charts
            vitalsChart.data.labels = records.map(r => r.timestamp);
            vitalsChart.data.datasets[0].data = records.map(r => r.heart_rate);
            vitalsChart.data.datasets[1].data = records.map(r => r.spo2);
            vitalsChart.update();

            anomalyChart.data.labels = records.map(r => r.patient_id);
            // anomaly_score agar backend mein nahi hai toh severity ke base par score 0.5-1.0 de sakte hain
            anomalyChart.data.datasets[0].data = records.map(r => r.anomaly_score || 0.1); 
            anomalyChart.data.datasets[0].backgroundColor = records.map(r => {
                if(r.severity === 'HIGH') return '#ef4444'; // Red
                if(r.severity === 'MEDIUM') return '#f59e0b'; // Orange
                return '#10b981'; // Green
            });
            anomalyChart.update();

            // Update Table
            const tbody = document.querySelector('#vitals-table tbody');
            if (tbody) {
                tbody.innerHTML = '';
                vitalsData.data.forEach(r => {
                    const tr = document.createElement('tr');
                    
                    // BP Check
                    const bp_sys = r.bp_sys !== undefined ? r.bp_sys : '--';
                    const bp_dia = r.bp_dia !== undefined ? r.bp_dia : '--';
                    
                    // Severity Class Logic
                    let badgeClass = "badge-low";
                    if(r.severity === 'MEDIUM') badgeClass = "badge-medium";
                    if(r.severity === 'HIGH' || r.severity === 'CRITICAL') badgeClass = "badge-high";

                    tr.innerHTML = `
                        <td>${r.timestamp}</td>
                        <td><strong>${r.patient_id}</strong></td>
                        <td>${Number(r.heart_rate).toFixed(1)}</td>
                        <td>${Number(r.spo2).toFixed(1)}%</td>
                        <td>${Number(r.temperature).toFixed(1)}°C</td>
                        <td>${bp_sys}/${bp_dia}</td>
                        <td><span class="badge ${badgeClass}">${r.severity}</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        }
    } catch (err) {
        console.error("Error updating dashboard:", err);
    }
}

// Poll every 2 seconds
setInterval(updateDashboard, 2000);
updateDashboard();