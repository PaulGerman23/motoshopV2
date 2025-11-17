// ================================================
// REPORTES DE VENTAS - JAVASCRIPT
// ================================================
function inicializarGraficos(ventasPorDia, ventasPorMetodo) {
// Gráfico de Ventas por Día
const ctxDia = document.getElementById('ventasPorDiaChart');
if (ctxDia) {
const labels = ventasPorDia.map(item => {
const fecha = new Date(item.dia);
return fecha.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit' });
});
    const datos = ventasPorDia.map(item => item.total);
    
    new Chart(ctxDia, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas Diarias',
                data: datos,
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderColor: '#667eea',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#667eea',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#667eea',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    borderRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return '$' + context.parsed.y.toLocaleString('es-AR', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString('es-AR');
                        }
                    }
                }
            }
        }
    });
}

// Gráfico de Métodos de Pago
const ctxMetodos = document.getElementById('metodosPagoChart');
if (ctxMetodos) {
    const total = Object.values(ventasPorMetodo).reduce((a, b) => a + b, 0);
    
    // Solo mostrar métodos con valores > 0
    const labels = [];
    const data = [];
    const colors = [];
    
    const metodosConfig = {
        efectivo: { label: 'Efectivo', color: '#10b981' },
        debito: { label: 'Débito', color: '#3b82f6' },
        credito: { label: 'Crédito', color: '#8b5cf6' },
        transferencia: { label: 'Transferencia', color: '#f59e0b' },
        mixto: { label: 'Mixto', color: '#6b7280' }
    };
    
    for (const [key, value] of Object.entries(ventasPorMetodo)) {
        if (value > 0) {
            labels.push(metodosConfig[key].label);
            data.push(value);
            colors.push(metodosConfig[key].color);
        }
    }
    
    new Chart(ctxMetodos, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    borderRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const valor = context.parsed;
                            const porcentaje = ((valor / total) * 100).toFixed(1);
                            return context.label + ': $' + valor.toLocaleString('es-AR') + ' (' + porcentaje + '%)';
                        }
                    }
                }
            }
        }
    });
}
}
// Función para exportar a PDF (placeholder)
function exportarPDF() {
window.print();
}
// Auto-cerrar alertas
document.addEventListener('DOMContentLoaded', function() {
setTimeout(() => {
const alerts = document.querySelectorAll('.alert-dismissible');
alerts.forEach(alert => {
const bsAlert = new bootstrap.Alert(alert);
bsAlert.close();
});
}, 5000);
});
console.log('✓ Módulo de reportes de ventas cargado');