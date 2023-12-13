fetch('/data')
    .then(response => response.json())
    .then(data => {
        const tableBody = document.getElementById('prTableBody');
        data.forEach(pr => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${pr.repo_name}</td>
                <td>${pr.author}</td>
                <td>${pr.team_name || 'N/A'}</td> <!-- Add team name here -->
                <td>${pr.pr_status}</td>
                <td>${pr.pr_title}</td>
                <td><a href="${pr.pr_url}" target="_blank">Link</a></td>
            `;
            tableBody.appendChild(row);
        });
    });




 function fetchAndDisplayChart(url, elementId, chartType, chartOptions) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById(elementId).getContext('2d');
            new Chart(ctx, {
                type: chartType,
                data: data,
                options: chartOptions
            });
        });
}

// Example for weekly PR stats (you'll need to adjust the data format as needed)
fetchAndDisplayChart('/data/weekly-stats', 'weeklyPrChart', 'bar', {/* chart options */});

// Similar for author breakdown and daily PR counts
fetchAndDisplayChart('/data/author-breakdown', 'authorPrChart', 'pie', {/* chart options */});
fetchAndDisplayChart('/data/daily-counts', 'dailyPrChart', 'line', {/* chart options */});

//form submission
document.getElementById('teamMappingForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const teamName = document.getElementById('teamName').value;

    fetch('/add-team-mapping', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, teamName })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Optionally, clear the form or give user feedback
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

function fetchAndDisplayWeeklyStatsByTeam() {
    fetch('/data/weekly-stats-by-team')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('weeklyPrChartByTeam').getContext('2d');
            new Chart(ctx, {
                type: 'bar', // or 'bar' for a grouped bar chart
                data: data,
                options: {
                    scales: {
                        x: {
                            stacked: true, // Set to false for a grouped bar chart
                        },
                        y: {
                            stacked: true // Set to false for a grouped bar chart
                        }
                    }
                }
            });
        });
}

fetchAndDisplayWeeklyStatsByTeam();


