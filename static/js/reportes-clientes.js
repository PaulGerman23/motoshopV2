// ================================================
// REPORTES DE CLIENTES - JAVASCRIPT
// ================================================

function inicializarGraficoIVA(condicionIVAData) {
    const ctx = document.getElementById('condicionIVAChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'pie',
            data: condicionIVAData,
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
                                return context.label + ': ' + valor + ' clientes (' + porcentaje + '%)';
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

// Función para calcular métricas adicionales
function calcularMetricas() {
    const totalClientes = parseInt(document.querySelector('.stat-value').textContent);
    const clientesConCompras = document.querySelectorAll('.badge.bg-primary').length;
    
    // Calcular tasa de conversión
    const tasaConversion = ((clientesConCompras / totalClientes) * 100).toFixed(1);
    console.log('Tasa de conversión:', tasaConversion + '%');
}

// Animaciones para las métricas
function animarMetricas() {
    const metricas = document.querySelectorAll('.metrica-card');
    
    metricas.forEach((metrica, index) => {
        setTimeout(() => {
            metrica.style.opacity = '0';
            metrica.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                metrica.style.transition = 'all 0.5s ease';
                metrica.style.opacity = '1';
                metrica.style.transform = 'translateY(0)';
            }, 50);
        }, index * 100);
    });
}

// Destacar clientes VIP (top 3)
function destacarClientesVIP() {
    const topRows = document.querySelectorAll('.ranking-badge');
    
    topRows.forEach((badge, index) => {
        if (index < 3) {
            const row = badge.closest('tr');
            if (row) {
                row.style.background = 'linear-gradient(90deg, rgba(102, 126, 234, 0.05) 0%, transparent 100%)';
            }
            
            // Agregar corona a los top 3
            if (index === 0) {
                badge.innerHTML = '<i class="bi bi-trophy-fill" style="color: #fbbf24;"></i>';
                badge.style.background = 'linear-gradient(135deg, #fbbf24, #f59e0b)';
            } else if (index === 1) {
                badge.innerHTML = '<i class="bi bi-trophy-fill" style="color: #d1d5db;"></i>';
                badge.style.background = 'linear-gradient(135deg, #d1d5db, #9ca3af)';
            } else if (index === 2) {
                badge.innerHTML = '<i class="bi bi-trophy-fill" style="color: #f97316;"></i>';
                badge.style.background = 'linear-gradient(135deg, #f97316, #ea580c)';
            }
        }
    });
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    // Calcular métricas
    calcularMetricas();
    
    // Animar métricas
    animarMetricas();
    
    // Destacar clientes VIP
    destacarClientesVIP();
    
    // Auto-cerrar alertas
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Efecto hover en insights
    const insightCards = document.querySelectorAll('.insight-card');
    insightCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

console.log('✓ Módulo de reportes de clientes cargado');