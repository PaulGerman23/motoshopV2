// ================================================
// SISTEMA POS COMPLETO - VENTAS Y TICKETS
// ================================================

// Estado global del carrito y ticket
let carrito = [];
let ticketActual = null;
let descuentoGlobal = { tipo: 'porcentaje', valor: 0 };

// ================================================
// VALIDACIONES
// ================================================

function validarCantidad(cantidad, stock) {
    if (!cantidad || cantidad === '') return { valido: false, mensaje: null };
    
    const cant = parseInt(cantidad);
    
    if (isNaN(cant) || cant <= 0) {
        return { valido: false, mensaje: 'Cantidad inválida' };
    }
    
    if (cant > stock) {
        return { valido: false, mensaje: 'Stock insuficiente' };
    }
    
    return { valido: true, valor: cant };
}

function validarMetodoPago() {
    const metodoPago = document.getElementById('tipo_pago')?.value;
    if (!metodoPago || metodoPago === '') {
        return { valido: false, mensaje: 'Debe seleccionar un método de pago' };
    }
    return { valido: true, valor: metodoPago };
}

function validarCarrito() {
    if (carrito.length === 0) {
        return { valido: false, mensaje: 'El carrito está vacío' };
    }
    
    const total = calcularTotal();
    if (total <= 0) {
        return { valido: false, mensaje: 'El total debe ser mayor a 0' };
    }
    
    return { valido: true };
}

// ================================================
// GESTIÓN DEL CARRITO
// ================================================

function agregarAlCarrito(button) {
    const id = button.getAttribute('data-id');
    const descripcion = button.getAttribute('data-descripcion');
    const precio = parseFloat(button.getAttribute('data-precio'));
    const stock = parseInt(button.getAttribute('data-stock'));
    
    // Verificar si ya existe en el carrito
    const itemExistente = carrito.find(item => item.producto_id === id);
    if (itemExistente) {
        mostrarNotificacion('Este producto ya está en el carrito. Modifica la cantidad desde el carrito.', 'warning');
        return;
    }
    
    // Solicitar cantidad
    const cantidadInput = prompt(`Stock disponible: ${stock} unidades\n\nIngrese la cantidad:`, '1');
    
    // Si presiona Cancelar, simplemente retornar sin mensaje
    if (cantidadInput === null) return;
    
    // Validar cantidad
    const validacion = validarCantidad(cantidadInput, stock);
    
    if (!validacion.valido) {
        if (validacion.mensaje) {
            mostrarNotificacion(validacion.mensaje, 'danger');
        }
        return;
    }
    
    const cantidad = validacion.valor;
    
    // Agregar al carrito
    const item = {
        producto_id: id,
        descripcion: descripcion,
        precio: precio,
        cantidad: cantidad,
        stock: stock,
        subtotal: precio * cantidad
    };
    
    carrito.push(item);
    actualizarCarrito();
    mostrarNotificacion('Producto agregado al carrito', 'success');
}

function modificarCantidad(index, nuevaCantidad) {
    const item = carrito[index];
    const validacion = validarCantidad(nuevaCantidad, item.stock);
    
    if (!validacion.valido) {
        if (validacion.mensaje) {
            mostrarNotificacion(validacion.mensaje, 'danger');
        }
        return false;
    }
    
    item.cantidad = validacion.valor;
    item.subtotal = item.precio * item.cantidad;
    actualizarCarrito();
    return true;
}

function eliminarItem(index) {
    carrito.splice(index, 1);
    actualizarCarrito();
    mostrarNotificacion('Producto eliminado del carrito', 'info');
}

function limpiarCarrito() {
    if (carrito.length === 0) {
        mostrarNotificacion('El carrito ya está vacío', 'info');
        return;
    }
    
    if (confirm('¿Limpiar todo el carrito?')) {
        carrito = [];
        descuentoGlobal = { tipo: 'porcentaje', valor: 0 };
        actualizarCarrito();
        mostrarNotificacion('Carrito limpiado', 'info');
    }
}

// ================================================
// CÁLCULOS
// ================================================

function calcularSubtotal() {
    return carrito.reduce((sum, item) => sum + item.subtotal, 0);
}

function calcularDescuento() {
    const subtotal = calcularSubtotal();
    
    if (descuentoGlobal.tipo === 'porcentaje') {
        return subtotal * (descuentoGlobal.valor / 100);
    } else {
        return descuentoGlobal.valor;
    }
}

function calcularTotal() {
    const subtotal = calcularSubtotal();
    const descuento = calcularDescuento();
    return Math.max(0, subtotal - descuento);
}

// ================================================
// RENDERIZADO
// ================================================

function actualizarCarrito() {
    const container = document.getElementById('carritoItems');
    const subtotalEl = document.getElementById('subtotalVenta');
    const descuentoEl = document.getElementById('descuentoVenta');
    const totalEl = document.getElementById('totalVenta');
    const btnFinalizar = document.getElementById('btnFinalizarVenta');
    const btnGuardarTicket = document.getElementById('btnGuardarTicket');
    
    // Renderizar items
    if (carrito.length === 0) {
        container.innerHTML = '<p class="text-muted text-center py-4">El carrito está vacío</p>';
        if (subtotalEl) subtotalEl.textContent = '$0.00';
        if (descuentoEl) descuentoEl.textContent = '$0.00';
        if (totalEl) totalEl.textContent = '$0.00';
        if (btnFinalizar) btnFinalizar.disabled = true;
        if (btnGuardarTicket) btnGuardarTicket.disabled = true;
        return;
    }
    
    let html = '';
    carrito.forEach((item, index) => {
        html += `
            <div class="cart-item mb-2">
                <div class="d-flex justify-content-between align-items-start mb-1">
                    <div class="flex-grow-1">
                        <small class="text-muted d-block">${item.descripcion}</small>
                        <div class="d-flex align-items-center gap-2 mt-1">
                            <input type="number" class="form-control form-control-sm" 
                                   style="width: 70px;" 
                                   value="${item.cantidad}" 
                                   min="1" 
                                   max="${item.stock}"
                                   onchange="modificarCantidad(${index}, this.value)"
                                   onkeypress="if(event.key==='Enter') this.blur()">
                            <span class="text-muted">x</span>
                            <strong>$${item.precio.toFixed(2)}</strong>
                        </div>
                    </div>
                    <div class="text-end">
                        <button type="button" class="btn btn-sm btn-danger mb-1" onclick="eliminarItem(${index})">
                            <i class="bi bi-x"></i>
                        </button>
                        <div>
                            <strong class="text-success">$${item.subtotal.toFixed(2)}</strong>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Actualizar totales
    const subtotal = calcularSubtotal();
    const descuento = calcularDescuento();
    const total = calcularTotal();
    
    if (subtotalEl) subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
    if (descuentoEl) descuentoEl.textContent = `-$${descuento.toFixed(2)}`;
    if (totalEl) totalEl.textContent = `$${total.toFixed(2)}`;
    
    // Habilitar botones
    if (btnFinalizar) btnFinalizar.disabled = false;
    if (btnGuardarTicket) btnGuardarTicket.disabled = false;
    
    // Actualizar JSON oculto
    const productosInput = document.getElementById('productosJSON');
    if (productosInput) {
        productosInput.value = JSON.stringify(carrito);
    }
}

// ================================================
// DESCUENTOS
// ================================================

function aplicarDescuento() {
    const tipo = document.getElementById('tipoDescuento')?.value || 'porcentaje';
    const valor = parseFloat(document.getElementById('valorDescuento')?.value || 0);
    
    if (valor < 0) {
        mostrarNotificacion('El descuento no puede ser negativo', 'danger');
        return;
    }
    
    const subtotal = calcularSubtotal();
    
    if (tipo === 'porcentaje' && valor > 100) {
        mostrarNotificacion('El descuento no puede ser mayor al 100%', 'danger');
        return;
    }
    
    if (tipo === 'monto' && valor > subtotal) {
        mostrarNotificacion('El descuento no puede ser mayor al subtotal', 'danger');
        return;
    }
    
    descuentoGlobal = { tipo, valor };
    actualizarCarrito();
    
    const modal = bootstrap.Modal.getInstance(document.getElementById('modalDescuento'));
    if (modal) modal.hide();
    
    mostrarNotificacion('Descuento aplicado correctamente', 'success');
}

function quitarDescuento() {
    descuentoGlobal = { tipo: 'porcentaje', valor: 0 };
    actualizarCarrito();
    mostrarNotificacion('Descuento removido', 'info');
}

// ================================================
// TICKETS (VENTAS EN ESPERA)
// ================================================

async function guardarTicket() {
    // Validar carrito
    const validacionCarrito = validarCarrito();
    if (!validacionCarrito.valido) {
        mostrarNotificacion(validacionCarrito.mensaje, 'warning');
        return;
    }
    
    const cliente = document.getElementById('cliente')?.value || '';
    const observacion = document.getElementById('observacion')?.value || '';
    
    try {
        const response = await fetch('/ventas/tickets/guardar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                cliente_id: cliente,
                productos: carrito,
                descuento: descuentoGlobal,
                observacion: observacion
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarNotificacion(`Ticket #${data.ticket.codigo_ticket} guardado correctamente`, 'success');
            limpiarCarrito();
            actualizarListaTickets();
        } else {
            mostrarNotificacion(data.error || 'Error al guardar el ticket', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al conectar con el servidor', 'danger');
    }
}

async function recuperarTicket(ticketId) {
    try {
        const response = await fetch(`/ventas/tickets/${ticketId}/recuperar/`);
        const data = await response.json();
        
        if (data.success) {
            // Cargar datos del ticket
            carrito = data.ticket.productos;
            descuentoGlobal = data.ticket.descuento;
            ticketActual = ticketId;
            
            // Actualizar formulario
            if (data.ticket.cliente_id) {
                document.getElementById('cliente').value = data.ticket.cliente_id;
            }
            if (data.ticket.observacion) {
                document.getElementById('observacion').value = data.ticket.observacion;
            }
            
            actualizarCarrito();
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalTickets'));
            if (modal) modal.hide();
            
            mostrarNotificacion(`Ticket #${data.ticket.codigo_ticket} recuperado`, 'success');
        } else {
            mostrarNotificacion(data.error || 'Error al recuperar el ticket', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al conectar con el servidor', 'danger');
    }
}

async function cancelarTicket(ticketId) {
    if (!confirm('¿Está seguro de cancelar este ticket?')) return;
    
    try {
        const response = await fetch(`/ventas/tickets/${ticketId}/cancelar/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarNotificacion('Ticket cancelado correctamente', 'success');
            actualizarListaTickets();
        } else {
            mostrarNotificacion(data.error || 'Error al cancelar el ticket', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al conectar con el servidor', 'danger');
    }
}

async function actualizarListaTickets() {
    const container = document.getElementById('listaTickets');
    if (!container) return;
    
    try {
        const response = await fetch('/ventas/tickets/lista/');
        const data = await response.json();
        
        if (data.tickets.length === 0) {
            container.innerHTML = '<p class="text-muted text-center py-4">No hay tickets pendientes</p>';
            return;
        }
        
        let html = '<div class="list-group">';
        data.tickets.forEach(ticket => {
            html += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">Ticket #${ticket.codigo_ticket}</h6>
                            <small class="text-muted">${ticket.fecha_creacion}</small>
                            <p class="mb-1 mt-2"><strong>Total: $${ticket.total}</strong></p>
                            <small>${ticket.items_count} productos</small>
                        </div>
                        <div class="btn-group-vertical">
                            <button class="btn btn-sm btn-primary" onclick="recuperarTicket(${ticket.id})">
                                <i class="bi bi-arrow-counterclockwise"></i> Recuperar
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="cancelarTicket(${ticket.id})">
                                <i class="bi bi-x"></i> Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    } catch (error) {
        console.error('Error:', error);
    }
}

// ================================================
// FINALIZAR VENTA
// ================================================

function validarYFinalizarVenta(event) {
    event.preventDefault();
    
    // Validar carrito
    const validacionCarrito = validarCarrito();
    if (!validacionCarrito.valido) {
        mostrarNotificacion(validacionCarrito.mensaje, 'warning');
        return false;
    }
    
    // Validar método de pago
    const validacionPago = validarMetodoPago();
    if (!validacionPago.valido) {
        mostrarNotificacion(validacionPago.mensaje, 'warning');
        return false;
    }
    
    // Si hay ticket actual, finalizar ticket
    if (ticketActual) {
        finalizarTicket();
        return false;
    }
    
    // Agregar datos de descuento al formulario
    const descuentoInput = document.createElement('input');
    descuentoInput.type = 'hidden';
    descuentoInput.name = 'descuento';
    descuentoInput.value = JSON.stringify(descuentoGlobal);
    event.target.appendChild(descuentoInput);
    
    // Continuar con el submit
    event.target.submit();
}

async function finalizarTicket() {
    const validacionPago = validarMetodoPago();
    if (!validacionPago.valido) {
        mostrarNotificacion(validacionPago.mensaje, 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/ventas/tickets/${ticketActual}/finalizar/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                tipo_pago: validacionPago.valor
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mostrarNotificacion(`Venta #${data.venta.codigo_venta} registrada correctamente`, 'success');
            
            // Limpiar y redirigir
            setTimeout(() => {
                window.location.href = `/ventas/detalle/${data.venta.id}/`;
            }, 1500);
        } else {
            mostrarNotificacion(data.error || 'Error al finalizar el ticket', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al conectar con el servidor', 'danger');
    }
}

// ================================================
// BÚSQUEDA DE PRODUCTOS
// ================================================

function buscarProducto(event) {
    const texto = event.target.value.toLowerCase();
    const filas = document.querySelectorAll('#listaProductos tr');
    
    filas.forEach(fila => {
        const contenido = fila.textContent.toLowerCase();
        fila.style.display = contenido.includes(texto) ? '' : 'none';
    });
}

// ================================================
// UTILIDADES
// ================================================

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function mostrarNotificacion(mensaje, tipo = 'info') {
    const iconos = {
        'success': 'bi-check-circle-fill',
        'danger': 'bi-exclamation-triangle-fill',
        'warning': 'bi-exclamation-circle-fill',
        'info': 'bi-info-circle-fill'
    };
    
    const container = document.querySelector('.page-content') || document.body;
    const alert = document.createElement('div');
    alert.className = `alert alert-${tipo} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        <i class="bi ${iconos[tipo] || iconos['info']} me-2"></i>
        <span>${mensaje}</span>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(alert);
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

// ================================================
// INICIALIZACIÓN
// ================================================

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar búsqueda
    const searchInput = document.getElementById('buscarProducto');
    if (searchInput) {
        searchInput.addEventListener('input', buscarProducto);
    }
    
    // Inicializar formulario de venta
    const formVenta = document.getElementById('formVenta');
    if (formVenta) {
        formVenta.addEventListener('submit', validarYFinalizarVenta);
    }
    
    // Cargar lista de tickets si existe el modal
    const modalTickets = document.getElementById('modalTickets');
    if (modalTickets) {
        modalTickets.addEventListener('show.bs.modal', actualizarListaTickets);
    }
    
    console.log('✓ Sistema POS inicializado correctamente');
});