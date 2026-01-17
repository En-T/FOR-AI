const Charts = {
    drawChart: function(canvasId, type, labels, data, title) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: title,
                    data: data,
                    backgroundColor: [
                        'rgba(13, 110, 253, 0.2)',
                        'rgba(25, 135, 84, 0.2)',
                        'rgba(255, 193, 7, 0.2)',
                        'rgba(220, 53, 69, 0.2)',
                        'rgba(13, 202, 240, 0.2)'
                    ],
                    borderColor: [
                        'rgba(13, 110, 253, 1)',
                        'rgba(25, 135, 84, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(220, 53, 69, 1)',
                        'rgba(13, 202, 240, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: type === 'bar' ? {
                    y: {
                        beginAtZero: true
                    }
                } : {}
            }
        });
    }
};
