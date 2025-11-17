// ================================================
// REPORTES DE STOCK - JAVASCRIPT
// ================================================

function inicializarGraficoCategoria(categoriaData) {
    const ctx = document.getElementById('categoriaChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: categoriaData.labels,
                datasets: [{
                    data: categoriaData.data,
                    backgroundColor: [
                        '#667eea',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#3b82f6',
                        '#8b5cf6',
                        '#ec4899',
                        '#14b8a6'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 12
                            },
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        borderRadius: 8,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const valor = context.parsed;
                                const porcentaje = ((valor / total) * 100).toFixed(1);
                                return context.label + ': ' + valor + ' productos (' + porcentaje + '%)';
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

// Función para filtrar tabla de inventario
function filtrarInventario() {
    const input = document.getElementById('buscarProducto');
    const filter = input.value.toLowerCase();
    const table = document.querySelector('.modern-table tbody');
    const rows = table.getElementsByTagName('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let found = false;
        
        for (let j = 0; j < cells.length; j++) {
            const cell = cells[j];
            if (cell) {
                const textValue = cell.textContent || cell.innerText;
                if (textValue.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
        }
        
        if (found) {
            rows[i].style.display = '';
        } else {
            rows[i].style.display = 'none';
        }
    }
}

// Destacar productos con alertas
document.addEventListener('DOMContentLoaded', function() {
    const alertRows = document.querySelectorAll('.nivel-bajo, .nivel-medio');
    alertRows.forEach(row => {
        row.closest('tr').style.backgroundColor = 'rgba(245, 158, 11, 0.05)';
    });
    
    // Auto-cerrar alertas
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

console.log('✓ Módulo de reportes de stock cargado');