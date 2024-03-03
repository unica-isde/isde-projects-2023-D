$(document).ready(function () {
    var scripts = document.getElementById('makeHistogram');
    var histogram_data = scripts.getAttribute('histogram_data');
    var data_array = JSON.parse(histogram_data);
    makeHistogram(data_array);
});

function generateLabels(length) {
    const labels = [];
    for (let i = 0; i < length; i++) {
        labels.push(`${i}`);
    }
    return labels
}

function makeHistogram(data) {
    console.log(data);

    // Computing the maximum value in the array
    const maxHistogramValue = Math.max(...data);

    // Getting the histogram canvas element
    const ctx = document.getElementById('histogramChart').getContext('2d')

    // Creation of the Histogram using the Chart.js library
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: generateLabels(256),
            datasets: [{
                label: 'Histogram',
                data: data,
                backgroundColor: 'rgba(0, 0, 0, 1)',
                borderColor: 'rgba(0, 0, 0, 1)',
                borderWidth: 1,
                barThickness: 2.5
            }]
        },
        options: {
            scales: {
                y: {
                    display: false,
                    beginAtZero: true,
                    max: maxHistogramValue
                },
                x: {
                    display: false
                },
            },
            plugins: {
                legend: {
                    display: false
                }
            },
            layout: {
                padding: 0 
            },
            elements: {
                bar: {
                    barPercentage: 1, 
                    categoryPercentage: 1 
                }
            }
            
        }
    })
}