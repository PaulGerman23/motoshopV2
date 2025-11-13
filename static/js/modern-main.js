// === MOTOSHOP MODERN - JAVASCRIPT ===

document.addEventListener('DOMContentLoaded', function() {
    initSidebar();
    initActiveLinks();
    initAlerts();
    initTooltips();
});

// === SIDEBAR ===
function initSidebar() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
    
    // Cerrar sidebar al hacer click fuera en móvil
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });
}

// === ACTIVE LINKS ===
function initActiveLinks() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
        
        // Activar en hover
        link.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateX(5px)';
            }
        });
        
        link.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = 'translateX(0)';
            }
        });
    });
}

// === ALERTS ===
function initAlerts() {
    const alerts = document.querySelectorAll('.modern-alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// === TOOLTIPS ===
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// === NOTIFICATIONS ===
function showNotification(message, type = 'success') {
    const container = document.querySelector('.page-content');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show modern-alert`;
    alert.innerHTML = `
        <i class="bi bi-check-circle-fill"></i>
        <span>${message}</span>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.insertBefore(alert, container.firstChild);
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

// === CONFIRMATION DIALOGS ===
document.querySelectorAll('[data-confirm]').forEach(element => {
    element.addEventListener('click', function(e) {
        const message = this.getAttribute('data-confirm');
        if (!confirm(message)) {
            e.preventDefault();
        }
    });
});

// === SEARCH FUNCTIONALITY ===
const searchInput = document.querySelector('.search-input');
if (searchInput) {
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value;
        
        if (query.length >= 2) {
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        }
    });
}

function performSearch(query) {
    console.log('Buscando:', query);
    // Implementar lógica de búsqueda aquí
}

// === SMOOTH SCROLL ===
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

// === RESPONSIVE TABLES ===
function makeTablesResponsive() {
    const tables = document.querySelectorAll('table:not(.modern-table)');
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.classList.add('table-responsive');
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

makeTablesResponsive();

// === ANIMATION ON SCROLL ===
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(card);
});

// === UTILITY FUNCTIONS ===

// Formatear moneda
function formatCurrency(value) {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS'
    }).format(value);
}

// Formatear fecha
function formatDate(date) {
    return new Intl.DateTimeFormat('es-AR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

// Copiar al portapapeles
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copiado al portapapeles', 'success');
    }).catch(err => {
        console.error('Error al copiar:', err);
    });
}

// === CONSOLE INFO ===
console.log('%c MotoShop System ', 'background: linear-gradient(135deg, #667eea, #764ba2); color: white; font-size: 20px; padding: 10px 20px; border-radius: 8px;');
console.log('%c Sistema de gestión moderno cargado correctamente ✓', 'color: #10b981; font-size: 14px; font-weight: bold;');

// === EXPORT ===
window.MotoShop = {
    showNotification,
    formatCurrency,
    formatDate,
    copyToClipboard
};