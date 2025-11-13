// === MOTOSHOP DJANGO - JAVASCRIPT PRINCIPAL ===

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (alert.classList.contains('alert-dismissible')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });

    // Marcar link activo en el sidebar
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Confirmación antes de eliminar
    const deleteButtons = document.querySelectorAll('a[href*="eliminar"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Está seguro de que desea eliminar este registro?')) {
                e.preventDefault();
            }
        });
    });

    // Validación de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// === FUNCIONES GLOBALES ===

// Formatear números como moneda
function formatCurrency(value) {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS'
    }).format(value);
}

// Búsqueda en tablas
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    const filter = input.value.toUpperCase();
    const tr = table.getElementsByTagName('tr');

    for (let i = 1; i < tr.length; i++) {
        let td = tr[i].getElementsByTagName('td');
        let display = false;

        for (let j = 0; j < td.length; j++) {
            if (td[j]) {
                const txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    display = true;
                    break;
                }
            }
        }
        tr[i].style.display = display ? '' : 'none';
    }
}

// Calcular margen de ganancia
function calcularMargen() {
    const precioCosto = parseFloat(document.getElementById('id_precio_costo').value) || 0;
    const precioVenta = parseFloat(document.getElementById('id_precio_venta').value) || 0;

    if (precioCosto > 0) {
        const margen = ((precioVenta - precioCosto) / precioCosto) * 100;
        console.log('Margen de ganancia:', margen.toFixed(2) + '%');
    }
}

// Validar CUIT
function validarCUIT(cuit) {
    const cuitRegex = /^\d{2}-\d{8}-\d{1}$/;
    return cuitRegex.test(cuit);
}

// Validar DNI
function validarDNI(dni) {
    const dniRegex = /^\d{7,8}$/;
    return dniRegex.test(dni);
}

// Mostrar notificación
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('main');
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// === FUNCIONES PARA VENTAS ===

// Carrito de ventas (almacenado en memoria)
let carritoVentas = [];

function agregarProductoCarrito(productoId, descripcion, precio, stock) {
    const cantidad = parseInt(prompt(`Cantidad (Stock disponible: ${stock}):`, '1'));
    
    if (cantidad && cantidad > 0 && cantidad <= stock) {
        const item = {
            producto_id: productoId,
            descripcion: descripcion,
            precio: precio,
            cantidad: cantidad,
            subtotal: precio * cantidad
        };
        
        carritoVentas.push(item);
        actualizarCarritoUI();
        showNotification('Producto agregado al carrito', 'success');
    } else {
        showNotification('Cantidad inválida o stock insuficiente', 'danger');
    }
}

function actualizarCarritoUI() {
    const carritoContainer = document.getElementById('carritoVentas');
    if (!carritoContainer) return;

    let html = '<table class="table"><thead><tr><th>Producto</th><th>Cant.</th><th>Precio</th><th>Subtotal</th><th></th></tr></thead><tbody>';
    
    let total = 0;
    carritoVentas.forEach((item, index) => {
        total += item.subtotal;
        html += `
            <tr>
                <td>${item.descripcion}</td>
                <td>${item.cantidad}</td>
                <td>$${item.precio.toFixed(2)}</td>
                <td>$${item.subtotal.toFixed(2)}</td>
                <td><button onclick="eliminarDelCarrito(${index})" class="btn btn-sm btn-danger">X</button></td>
            </tr>
        `;
    });
    
    html += `</tbody><tfoot><tr><th colspan="3">TOTAL</th><th>$${total.toFixed(2)}</th><th></th></tr></tfoot></table>`;
    carritoContainer.innerHTML = html;
    
    // Actualizar campo hidden con JSON
    const productosInput = document.getElementById('productosJSON');
    if (productosInput) {
        productosInput.value = JSON.stringify(carritoVentas);
    }
}

function eliminarDelCarrito(index) {
    carritoVentas.splice(index, 1);
    actualizarCarritoUI();
    showNotification('Producto eliminado del carrito', 'info');
}

// === CONSOLA DE DEBUG ===
console.log('%c MotoShop Django System ', 'background: #667eea; color: white; font-size: 16px; padding: 10px;');
console.log('Sistema de gestión inicializado correctamente');