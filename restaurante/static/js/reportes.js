document.addEventListener("DOMContentLoaded", function() {
    // 1. Curva de Ingresos Semanales
    const ventasLabels = JSON.parse(document.getElementById('ventas-labels').textContent);
    const ventasData = JSON.parse(document.getElementById('ventas-data').textContent);

    const ctxVentas = document.getElementById('ventasChart');
    if (ctxVentas) {
        new Chart(ctxVentas, {
            type: 'line',
            data: {
                labels: ventasLabels,
                datasets: [{
                    label: 'Ingresos ($)',
                    data: ventasData,
                    borderColor: '#7B1535',
                    backgroundColor: 'rgba(123, 21, 53, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#7B1535',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#1a1a1a',
                        titleFont: { family: 'Poppins', size: 13 },
                        bodyFont: { family: 'Poppins', size: 14, weight: 'bold' },
                        padding: 12,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                let value = context.parsed.y;
                                return '$' + value.toLocaleString('es-CO');
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            font: { family: 'Poppins', size: 12 },
                            color: '#888'
                        }
                    },
                    y: {
                        grid: {
                            color: '#eaeaea',
                            drawBorder: false,
                            borderDash: [5, 5]
                        },
                        ticks: {
                            font: { family: 'Poppins', size: 12 },
                            color: '#888',
                            callback: function(value) {
                                if(value >= 1000000) return '$' + (value / 1000000).toFixed(1) + 'M';
                                if(value >= 1000) return '$' + (value / 1000).toFixed(0) + 'k';
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });
    }

    // 2. Gráfica Precio vs Costo (Rentabilidad)
    const rentLabels = JSON.parse(document.getElementById('rent-labels').textContent);
    const rentPrecios = JSON.parse(document.getElementById('rent-precios').textContent);
    const rentCostos = JSON.parse(document.getElementById('rent-costos').textContent);

    const ctxRent = document.getElementById('rentabilidadChart');
    if (ctxRent) {
        new Chart(ctxRent, {
            type: 'bar',
            data: {
                labels: rentLabels,
                datasets: [
                    {
                        label: 'Precio de Venta',
                        data: rentPrecios,
                        backgroundColor: '#a34860',
                        borderRadius: 4,
                        barPercentage: 0.6,
                        categoryPercentage: 0.8
                    },
                    {
                        label: 'Costo Insumos',
                        data: rentCostos,
                        backgroundColor: '#d6a655',
                        borderRadius: 4,
                        barPercentage: 0.6,
                        categoryPercentage: 0.8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { family: 'Poppins', size: 12 },
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1a1a1a',
                        titleFont: { family: 'Poppins', size: 13 },
                        bodyFont: { family: 'Poppins', size: 14, weight: 'bold' },
                        padding: 12,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                let value = context.parsed.y;
                                return context.dataset.label + ': $' + value.toLocaleString('es-CO');
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            font: { family: 'Poppins', size: 11 },
                            color: '#888'
                        }
                    },
                    y: {
                        grid: {
                            color: '#eaeaea',
                            drawBorder: false,
                            borderDash: [5, 5]
                        },
                        ticks: {
                            font: { family: 'Poppins', size: 12 },
                            color: '#888',
                            callback: function(value) {
                                if(value >= 1000000) return '$' + (value / 1000000).toFixed(1) + 'M';
                                if(value >= 1000) return '$' + (value / 1000).toFixed(0) + 'k';
                                return '$' + value;
                            }
                        }
                    }
                }
            }
        });
    }
});
