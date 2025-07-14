// Global variables
let currentChart = null;
let currentVisualization = null;
let countries = [];
let indicators = [];

// DOM elements
const vizInterface = document.getElementById('viz-interface');
const vizTitle = document.getElementById('viz-title');
const countrySelect = document.getElementById('country-select');
const indicatorSelect = document.getElementById('indicator-select');
const yearStartSlider = document.getElementById('year-start');
const yearEndSlider = document.getElementById('year-end');
const yearDisplay = document.getElementById('year-display');
const chartCanvas = document.getElementById('main-chart');
const chartLoading = document.querySelector('.chart-loading');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadInitialData();
});

// Initialize application
function initializeApp() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Update active navigation link on scroll
    window.addEventListener('scroll', updateActiveNavLink);
    
    // Update year display when sliders change
    yearStartSlider.addEventListener('input', updateYearDisplay);
    yearEndSlider.addEventListener('input', updateYearDisplay);
    
    // Ensure year-end is always >= year-start
    yearStartSlider.addEventListener('change', function() {
        if (parseInt(this.value) > parseInt(yearEndSlider.value)) {
            yearEndSlider.value = this.value;
        }
        updateYearDisplay();
    });
    
    yearEndSlider.addEventListener('change', function() {
        if (parseInt(this.value) < parseInt(yearStartSlider.value)) {
            yearStartSlider.value = this.value;
        }
        updateYearDisplay();
    });
}

// Setup event listeners
function setupEventListeners() {
    // Visualization card click handlers
    document.querySelectorAll('.viz-card').forEach(card => {
        card.addEventListener('click', function() {
            const vizType = this.dataset.viz;
            showVisualizationInterface(vizType);
        });
    });

    // Add hover effects to visualization cards
    document.querySelectorAll('.viz-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Load initial data
async function loadInitialData() {
    try {
        await Promise.all([
            loadCountries(),
            loadIndicators()
        ]);
    } catch (error) {
        console.error('Error loading initial data:', error);
        showError('Failed to load application data');
    }
}

// Load countries from API
async function loadCountries() {
    try {
        const response = await fetch('/api/countries/');
        if (!response.ok) throw new Error('Failed to load countries');
        
        countries = await response.json();
        populateCountrySelect();
    } catch (error) {
        console.error('Error loading countries:', error);
        showError('Failed to load countries. Please refresh the page.');
    }
}

// Load indicators from API
async function loadIndicators() {
    try {
        const response = await fetch('/api/indicators/');
        if (!response.ok) throw new Error('Failed to load indicators');
        
        indicators = await response.json();
        populateIndicatorSelect();
    } catch (error) {
        console.error('Error loading indicators:', error);
        showError('Failed to load indicators. Please refresh the page.');
    }
}

// Populate country select dropdown
function populateCountrySelect() {
    countrySelect.innerHTML = '<option value="">Select a country...</option>';
    countries.forEach(country => {
        const option = document.createElement('option');
        option.value = country.code;
        option.textContent = country.name;
        countrySelect.appendChild(option);
    });
}

// Populate indicator select dropdown
function populateIndicatorSelect() {
    indicatorSelect.innerHTML = '<option value="">Select an indicator...</option>';
    indicators.forEach(indicator => {
        const option = document.createElement('option');
        option.value = indicator.code;
        option.textContent = indicator.name;
        indicatorSelect.appendChild(option);
    });
}

// Update year display
function updateYearDisplay() {
    const startYear = yearStartSlider.value;
    const endYear = yearEndSlider.value;
    yearDisplay.textContent = `${startYear} - ${endYear}`;
}

// Update active navigation link
function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    let currentSection = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        
        if (pageYOffset >= sectionTop - 200) {
            currentSection = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
}

// Show visualization interface
function showVisualizationInterface(vizType) {
    currentVisualization = vizType;
    
    // Update title based on visualization type
    const titles = {
        'country-trends': 'Country Indicator Trends',
        'happiness-comparison': 'Happiness vs Indicators',
        'regional-happiness': 'Regional Happiness Distribution',
        'regional-snapshot': 'Regional Indicator Snapshot',
        'india-dashboard': 'India Dashboard'
    };
    
    vizTitle.textContent = titles[vizType] || 'Visualization';
    
    // Show the interface
    vizInterface.classList.remove('hidden');
    
    // Scroll to the interface
    vizInterface.scrollIntoView({ behavior: 'smooth' });
    
    // Hide home sections
    document.getElementById('home').style.display = 'none';
    document.getElementById('visualizations').style.display = 'none';
    document.getElementById('about').style.display = 'none';
}

// Hide visualization interface
function hideVizInterface() {
    vizInterface.classList.add('hidden');
    
    // Show home sections
    document.getElementById('home').style.display = 'block';
    document.getElementById('visualizations').style.display = 'block';
    document.getElementById('about').style.display = 'block';
    
    // Scroll to visualizations section
    document.getElementById('visualizations').scrollIntoView({ behavior: 'smooth' });
    
    // Clean up chart
    if (currentChart) {
        currentChart.destroy();
        currentChart = null;
    }
}

// Generate visualization
async function generateVisualization() {
    if (!validateInputs()) return;
    
    const country = countrySelect.value;
    const indicator = indicatorSelect.value;
    const startYear = yearStartSlider.value;
    const endYear = yearEndSlider.value;
    
    showLoading();
    
    try {
        const data = await fetchVisualizationData(currentVisualization, {
            country,
            indicator,
            startYear,
            endYear
        });
        
        renderChart(data);
    } catch (error) {
        console.error('Error generating visualization:', error);
        showError('Failed to generate visualization');
    } finally {
        hideLoading();
    }
}

// Validate inputs
function validateInputs() {
    if (!countrySelect.value) {
        showError('Please select a country');
        return false;
    }
    
    if (!indicatorSelect.value) {
        showError('Please select an indicator');
        return false;
    }
    
    return true;
}

// Fetch visualization data
async function fetchVisualizationData(vizType, params) {
    const endpoint = `/api/visualizations/${vizType}/`;
    const queryParams = new URLSearchParams(params);
    
    try {
        const response = await fetch(`${endpoint}?${queryParams}`);
        if (!response.ok) throw new Error('Failed to fetch data');
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching visualization data:', error);
        
        // Return error data structure
        return {
            labels: [],
            datasets: [],
            error: 'Failed to fetch data from API'
        };
    }
}


// Render chart
function renderChart(data) {
    if (currentChart) {
        currentChart.destroy();
    }
    
    const ctx = chartCanvas.getContext('2d');
    
    const config = {
        type: getChartType(currentVisualization),
        data: data,
        options: getChartOptions(currentVisualization)
    };
    
    currentChart = new Chart(ctx, config);
}

// Get chart type based on visualization
function getChartType(vizType) {
    switch (vizType) {
        case 'country-trends':
        case 'happiness-comparison':
        case 'india-dashboard':
            return 'line';
        case 'regional-happiness':
            return 'doughnut';
        case 'regional-snapshot':
            return 'bar';
        default:
            return 'line';
    }
}

// Get chart options based on visualization
function getChartOptions(vizType) {
    const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: document.getElementById('viz-title').textContent
            }
        }
    };
    
    switch (vizType) {
        case 'happiness-comparison':
            return {
                ...baseOptions,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            };
        case 'regional-happiness':
            return {
                ...baseOptions,
                cutout: '50%'
            };
        case 'country-trends':
        case 'regional-snapshot':
        case 'india-dashboard':
            return {
                ...baseOptions,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            };
        default:
            return baseOptions;
    }
}

// Show loading spinner
function showLoading() {
    chartLoading.classList.remove('hidden');
    chartCanvas.style.display = 'none';
}

// Hide loading spinner
function hideLoading() {
    chartLoading.classList.add('hidden');
    chartCanvas.style.display = 'block';
}

// Show error message
function showError(message) {
    alert(message); // Simple alert for now, can be improved with custom modal
}

// Utility function to scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Export functions for global access
window.showVisualizationInterface = showVisualizationInterface;
window.hideVizInterface = hideVizInterface;
window.generateVisualization = generateVisualization;
window.scrollToSection = scrollToSection;