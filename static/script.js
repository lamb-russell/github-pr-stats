/**
 * This script handles the fetching and displaying of data for the GitHub Pull Requests Dashboard.
 * It includes functions for rendering charts, displaying pull request data in a table,
 * and handling form submissions.
 */

// Ensure all DOM elements are loaded before executing the script
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the data fetching and chart rendering
    fetchAndDisplayPRData();
    //fetchAndDisplayChart('/data/weekly-stats', 'weeklyPrChart', 'bar', {/* chart options */});
    fetchAndDisplayChart('/data/author-breakdown', 'authorPrChart', 'pie', {/* chart options */});
    fetchAndDisplayChart('/data/daily-counts', 'dailyPrChart', 'line', {/* chart options */});
    fetchAndDisplayWeeklyStatsByTeam();

    // Initialize form submission handling
    setupFormSubmission();
});

/**
 * Fetches and displays PR data in a table.
 */
function fetchAndDisplayPRData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('prTableBody');
            data.forEach(pr => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${pr.repo_name}</td>
                    <td>${pr.author}</td>
                    <td>${pr.team_name || 'N/A'}</td>
                    <td>${pr.pr_status}</td>
                    <td>${pr.pr_title}</td>
                    <td><a href="${pr.pr_url}" target="_blank">Link</a></td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error fetching PR data:', error));
}

/**
 * Fetches data from a specified URL and displays it in a chart.
 * @param {string} url - The URL to fetch data from.
 * @param {string} elementId - The ID of the canvas element to render the chart in.
 * @param {string} chartType - The type of chart to render (e.g., 'bar', 'line').
 * @param {Object} chartOptions - Options for chart rendering.
 */
function fetchAndDisplayChart(url, elementId, chartType, chartOptions) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById(elementId).getContext('2d');
            new Chart(ctx, {
                type: chartType,
                data: data,
                options: chartOptions || getDefaultChartOptions(chartType)
            });
        })
        .catch(error => console.error(`Error fetching chart data from ${url}:`, error));
}

/**
 * Provides default chart options based on the chart type.
 * @param {string} chartType - The type of chart.
 * @return {Object} Default chart options for the given chart type.
 */
function getDefaultChartOptions(chartType) {
    switch (chartType) {
        case 'bar':
            return {
                scales: {
                    y: { beginAtZero: true }
                },
                plugins: {
                    legend: { display: true }
                }
            };
        case 'line':
            return {
                scales: {
                    y: { beginAtZero: true }
                },
                elements: {
                    line: { tension: 0.4 } // Smoother lines
                }
            };
        case 'pie':
            return {
                plugins: {
                    legend: { position: 'top' }
                }
            };
        default:
            return {};
    }
}


/**
 * Fetches and displays weekly stats by team in a bar chart.
 */
function fetchAndDisplayWeeklyStatsByTeam() {
    fetch('/data/weekly-stats-by-team')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('weeklyPrChartByTeam').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    scales: {
                        x: { stacked: true },
                        y: { stacked: true }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching weekly stats by team:', error));
}

/**
 * Sets up the form submission event listener and handler.
 */
function setupFormSubmission() {
    const form = document.getElementById('teamMappingForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const teamName = document.getElementById('teamName').value;

        fetch('/add-team-mapping', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, teamName })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // Optionally, clear the form or give user feedback
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
}
