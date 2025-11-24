// ===== Global State =====
let currentConfig = null;
let currentResults = null;
let scenarios = [];
let charts = {
    water: null,
    food: null,
    energy: null,
    ecology: null
};

// ===== Initialize App =====
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    await loadPredefinedScenarios();
    setupEventListeners();
});

// ===== Load Configuration =====
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        
        if (data.success) {
            currentConfig = data.config;
            populateForm(currentConfig);
        } else {
            showError('Error al cargar configuración: ' + data.error);
        }
    } catch (error) {
        showError('Error de conexión: ' + error.message);
    }
}

// ===== Load Predefined Scenarios =====
async function loadPredefinedScenarios() {
    try {
        const response = await fetch('/api/scenarios');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('scenarioSelect');
            
            Object.entries(data.scenarios).forEach(([key, scenario]) => {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = scenario.name;
                option.dataset.description = scenario.description;
                option.dataset.scenarios = JSON.stringify(scenario.scenarios);
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading scenarios:', error);
    }
}

// ===== Populate Form =====
function populateForm(config) {
    // Growth Scenarios (convert to percentage)
    document.getElementById('growth_pop').value = (config.scenarios.growth_pop * 100).toFixed(1);
    document.getElementById('growth_gdp').value = (config.scenarios.growth_gdp * 100).toFixed(1);
    document.getElementById('growth_urbanization').value = (config.scenarios.growth_urbanization * 100).toFixed(1);
    document.getElementById('growth_agri_yield').value = (config.scenarios.growth_agri_yield * 100).toFixed(1);
}

// ===== Get Form Data =====
function getFormData() {
    const config = JSON.parse(JSON.stringify(currentConfig)); // Deep clone
    
    // Growth scenarios (convert from percentage)
    config.scenarios.growth_pop = parseFloat(document.getElementById('growth_pop').value) / 100;
    config.scenarios.growth_gdp = parseFloat(document.getElementById('growth_gdp').value) / 100;
    config.scenarios.growth_urbanization = parseFloat(document.getElementById('growth_urbanization').value) / 100;
    config.scenarios.growth_agri_yield = parseFloat(document.getElementById('growth_agri_yield').value) / 100;
    
    return config;
}

// ===== Event Listeners =====
function setupEventListeners() {
    document.getElementById('runSimulation').addEventListener('click', runSimulation);
    document.getElementById('resetConfig').addEventListener('click', () => {
        populateForm(currentConfig);
    });
    document.getElementById('addScenario').addEventListener('click', addScenarioToComparison);
    document.getElementById('exportCSV').addEventListener('click', exportCSV);
    document.getElementById('exportJSON').addEventListener('click', exportJSON);
    document.getElementById('clearScenarios').addEventListener('click', clearScenarios);
    
    document.getElementById('scenarioSelect').addEventListener('change', (e) => {
        const option = e.target.selectedOptions[0];
        if (option.value) {
            const scenarioData = JSON.parse(option.dataset.scenarios);
            document.getElementById('growth_pop').value = (scenarioData.growth_pop * 100).toFixed(1);
            document.getElementById('growth_gdp').value = (scenarioData.growth_gdp * 100).toFixed(1);
            document.getElementById('growth_urbanization').value = (scenarioData.growth_urbanization * 100).toFixed(1);
            document.getElementById('growth_agri_yield').value = (scenarioData.growth_agri_yield * 100).toFixed(1);
        }
    });
}

// ===== Run Simulation =====
async function runSimulation() {
    const loadingState = document.getElementById('loadingState');
    const resultsContent = document.getElementById('resultsContent');
    
    // Show loading
    loadingState.style.display = 'flex';
    resultsContent.style.display = 'none';
    
    try {
        const config = getFormData();
        const years = parseInt(document.getElementById('years').value);
        
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                initial_data: config.initial_data,
                params: config.params,
                scenarios: config.scenarios,
                years: years
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentResults = data.results;
            updateSummaryCards(data.summary);
            updateCharts(data.results);
            
            // Hide loading, show results
            loadingState.style.display = 'none';
            resultsContent.style.display = 'block';
        } else {
            showError('Error en simulación: ' + data.error);
            loadingState.style.display = 'none';
        }
    } catch (error) {
        showError('Error de conexión: ' + error.message);
        loadingState.style.display = 'none';
    }
}

// ===== Update Summary Cards =====
function updateSummaryCards(summary) {
    document.getElementById('waterRatio').textContent = summary.final_water_ratio.toFixed(2);
    document.getElementById('foodRatio').textContent = summary.final_food_ratio.toFixed(2);
    document.getElementById('energyRatio').textContent = summary.final_energy_ratio.toFixed(2);
    document.getElementById('energyDemandValue').textContent = formatNumber(summary.final_energy_demand);
    document.getElementById('energySupplyValue').textContent = formatNumber(summary.final_energy_supply);
    document.getElementById('co2Total').textContent = formatNumber(summary.total_co2_emissions);
}

// ===== Update Charts =====
function updateCharts(results) {
    const years = results.map(r => r.year);
    
    // Water Chart
    updateChart('waterChart', 'water', {
        labels: years,
        datasets: [
            {
                label: 'Demanda de Agua',
                data: results.map(r => r.water_demand),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4
            },
            {
                label: 'Oferta de Agua',
                data: results.map(r => r.water_supply),
                borderColor: '#60a5fa',
                backgroundColor: 'rgba(96, 165, 250, 0.1)',
                tension: 0.4
            }
        ]
    });
    
    // Food Chart
    updateChart('foodChart', 'food', {
        labels: years,
        datasets: [
            {
                label: 'Ratio Seguridad Alimentaria',
                data: results.map(r => r.food_ratio),
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4
            }
        ]
    });
    
    // Energy Chart
    updateChart('energyChart', 'energy', {
        labels: years,
        datasets: [
            {
                label: 'Demanda de Energía',
                data: results.map(r => r.energy_demand),
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                tension: 0.4
            },
            {
                label: 'Oferta de Energía',
                data: results.map(r => r.energy_supply),
                borderColor: '#fbbf24',
                backgroundColor: 'rgba(251, 191, 36, 0.1)',
                tension: 0.4
            }
        ]
    });
    
    // Ecology Chart
    updateChart('ecologyChart', 'ecology', {
        labels: years,
        datasets: [
            {
                label: 'Emisiones CO₂ (Mt)',
                data: results.map(r => r.total_co2),
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                tension: 0.4,
                fill: true
            }
        ]
    });
}

// ===== Update Individual Chart =====
function updateChart(canvasId, chartKey, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Destroy existing chart
    if (charts[chartKey]) {
        charts[chartKey].destroy();
    }
    
    // Create new chart
    charts[chartKey] = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#1f2937',
                        font: {
                            family: 'Inter',
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1f2937',
                    bodyColor: '#6b7280',
                    borderColor: '#e5e7eb',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#f3f4f6'
                    },
                    ticks: {
                        color: '#6b7280',
                        font: {
                            family: 'Inter',
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: '#f3f4f6'
                    },
                    ticks: {
                        color: '#6b7280',
                        font: {
                            family: 'Inter',
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

// ===== Add Scenario to Comparison =====
function addScenarioToComparison() {
    if (!currentResults) {
        alert('Primero ejecuta una simulación');
        return;
    }
    
    const name = prompt('Nombre del escenario:');
    if (!name) return;
    
    scenarios.push({
        name: name,
        results: currentResults,
        config: getFormData()
    });
    
    updateScenariosDisplay();
}

// ===== Update Scenarios Display =====
function updateScenariosDisplay() {
    const container = document.getElementById('scenariosComparison');
    const list = document.getElementById('scenariosList');
    
    if (scenarios.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'block';
    list.innerHTML = '';
    
    scenarios.forEach((scenario, index) => {
        const item = document.createElement('div');
        item.className = 'scenario-item';
        item.innerHTML = `
            <div class="scenario-info">
                <h4>${scenario.name}</h4>
                <p>${scenario.results.length} años simulados</p>
            </div>
            <button class="scenario-remove" onclick="removeScenario(${index})">Eliminar</button>
        `;
        list.appendChild(item);
    });
    
    // Update charts to show all scenarios
    if (scenarios.length > 0) {
        updateChartsWithComparison();
    }
}

// ===== Remove Scenario =====
function removeScenario(index) {
    scenarios.splice(index, 1);
    updateScenariosDisplay();
    
    if (scenarios.length === 0 && currentResults) {
        updateCharts(currentResults);
    }
}

// ===== Clear All Scenarios =====
function clearScenarios() {
    scenarios = [];
    updateScenariosDisplay();
    
    if (currentResults) {
        updateCharts(currentResults);
    }
}

// ===== Update Charts with Comparison =====
function updateChartsWithComparison() {
    const colors = [
        'rgb(102, 126, 234)',
        'rgb(245, 87, 108)',
        'rgb(79, 172, 254)',
        'rgb(67, 233, 123)',
        'rgb(240, 147, 251)'
    ];
    
    // Water Chart
    const waterDatasets = scenarios.map((scenario, i) => ({
        label: `${scenario.name} - Ratio Agua`,
        data: scenario.results.map(r => r.water_ratio),
        borderColor: colors[i % colors.length],
        backgroundColor: colors[i % colors.length] + '20',
        tension: 0.4
    }));
    
    updateChart('waterChart', 'water', {
        labels: scenarios[0].results.map(r => r.year),
        datasets: waterDatasets
    });
    
    // Similar for other charts...
}

// ===== Export CSV =====
async function exportCSV() {
    if (!currentResults) {
        alert('No hay resultados para exportar');
        return;
    }
    
    try {
        const response = await fetch('/api/export/csv', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                results: currentResults
            })
        });
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'simulacion_wefe.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        showError('Error al exportar CSV: ' + error.message);
    }
}

// ===== Export JSON =====
function exportJSON() {
    if (!currentResults) {
        alert('No hay resultados para exportar');
        return;
    }
    
    const dataStr = JSON.stringify(currentResults, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'simulacion_wefe.json';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// ===== Utility Functions =====
function formatNumber(num) {
    return new Intl.NumberFormat('es-MX').format(Math.round(num));
}

function showError(message) {
    alert(message);
    console.error(message);
}
