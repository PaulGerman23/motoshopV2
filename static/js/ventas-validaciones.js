// ================================================
// VALIDACIONES COMPLETAS PARA SISTEMA DE VENTAS
// ================================================

/**
 * Validaciones de Producto
 */
class ValidadorProducto {
    static validarStock(cantidad, stockDisponible) {
        if (!cantidad || cantidad === '' || cantidad === null) {
            return { 
                valido: false, 
                mensaje: 'Debe ingresar una cantidad' 
            };
        }

        const cant = parseInt(cantidad);

        if (isNaN(cant)) {
            return { 
                valido: false, 
                mensaje: 'La cantidad debe ser un número' 
            };
        }

        if (cant <= 0) {
            return { 
                valido: false, 
                mensaje: 'La cantidad debe ser mayor a 0' 
            };
        }

        if (cant > stockDisponible) {
            return { 
                valido: false, 
                mensaje: `Stock insuficiente. Disponible: ${stockDisponible} unidades` 
            };
        }

        return { 
            valido: true, 
            valor: cant 
        };
    }

    static validarPrecio(precio) {
        if (!precio || precio === '' || precio === null) {
            return { valido: false, mensaje: 'El precio es requerido' };
        }

        const precioNum = parseFloat(precio);

        if (isNaN(precioNum) || precioNum < 0) {
            return { valido: false, mensaje: 'El precio debe ser un número válido' };
        }

        return { valido: true, valor: precioNum };
    }

    static validarProductoDuplicado(productoId, carrito) {
        const existe = carrito.find(item => item.producto_id === productoId);
        
        if (existe) {
            return { 
                valido: false, 
                mensaje: 'Este producto ya está en el carrito', 
                producto: existe 
            };
        }

        return { valido: true };
    }
}

/**
 * Validaciones de Carrito
 */
class ValidadorCarrito {
    static validarCarritoVacio(carrito) {
        if (!carrito || carrito.length === 0) {
            return { 
                valido: false, 
                mensaje: 'El carrito está vacío. Agregue al menos un producto.' 
            };
        }

        return { valido: true };
    }

    static validarTotal(total) {
        if (!total || total <= 0) {
            return { 
                valido: false, 
                mensaje: 'El total debe ser mayor a 0' 
            };
        }

        return { valido: true, valor: total };
    }

    static validarDescuento(descuento, subtotal) {
        if (!descuento || typeof descuento !== 'object') {
            return { valido: true, valor: 0 }; // Descuento opcional
        }

        const { tipo, valor } = descuento;

        if (!tipo || !['porcentaje', 'monto'].includes(tipo)) {
            return { 
                valido: false, 
                mensaje: 'Tipo de descuento inválido' 
            };
        }

        const valorNum = parseFloat(valor) || 0;

        if (valorNum < 0) {
            return { 
                valido: false, 
                mensaje: 'El descuento no puede ser negativo' 
            };
        }

        if (tipo === 'porcentaje' && valorNum > 100) {
            return { 
                valido: false, 
                mensaje: 'El descuento no puede ser mayor al 100%' 
            };
        }

        if (tipo === 'monto' && valorNum > subtotal) {
            return { 
                valido: false, 
                mensaje: 'El descuento no puede ser mayor al subtotal' 
            };
        }

        return { valido: true, valor: valorNum };
    }

    static validarStockDisponibleEnCarrito(carrito) {
        for (const item of carrito) {
            if (item.stock < item.cantidad) {
                return {
                    valido: false,
                    mensaje: `Stock insuficiente para "${item.descripcion}". Disponible: ${item.stock}`,
                    producto: item
                };
            }
        }

        return { valido: true };
    }
}

/**
 * Validaciones de Pago
 */
class ValidadorPago {
    static validarMetodoPago(metodoPago) {
        const metodosValidos = ['efectivo', 'debito', 'credito', 'transferencia', 'mixto'];

        if (!metodoPago || metodoPago === '') {
            return { 
                valido: false, 
                mensaje: 'Debe seleccionar un método de pago' 
            };
        }

        if (!metodosValidos.includes(metodoPago)) {
            return { 
                valido: false, 
                mensaje: 'Método de pago inválido' 
            };
        }

        return { valido: true, valor: metodoPago };
    }

    static validarPagoMixto(montoEfectivo, montoTarjeta, totalVenta) {
        const efectivo = parseFloat(montoEfectivo) || 0;
        const tarjeta = parseFloat(montoTarjeta) || 0;
        const total = parseFloat(totalVenta);

        if (efectivo < 0 || tarjeta < 0) {
            return { 
                valido: false, 
                mensaje: 'Los montos no pueden ser negativos' 
            };
        }

        if (efectivo + tarjeta !== total) {
            return { 
                valido: false, 
                mensaje: `La suma debe ser igual al total: $${total.toFixed(2)}` 
            };
        }

        if (efectivo === 0 && tarjeta === 0) {
            return { 
                valido: false, 
                mensaje: 'Debe ingresar al menos un monto' 
            };
        }

        return { 
            valido: true, 
            valores: { efectivo, tarjeta } 
        };
    }

    static validarCambio(montoRecibido, totalVenta) {
        const recibido = parseFloat(montoRecibido) || 0;
        const total = parseFloat(totalVenta);

        if (recibido < total) {
            return { 
                valido: false, 
                mensaje: `Monto insuficiente. Falta: $${(total - recibido).toFixed(2)}`,
                faltante: total - recibido
            };
        }

        return { 
            valido: true, 
            cambio: recibido - total 
        };
    }
}

/**
 * Validaciones de Ticket
 */
class ValidadorTicket {
    static validarTicketExistente(ticketId) {
        if (!ticketId || ticketId === null) {
            return { 
                valido: false, 
                mensaje: 'ID de ticket inválido' 
            };
        }

        return { valido: true, valor: ticketId };
    }

    static validarEstadoTicket(estado) {
        const estadosValidos = ['pendiente', 'finalizado', 'cancelado'];

        if (!estadosValidos.includes(estado)) {
            return { 
                valido: false, 
                mensaje: 'Estado de ticket inválido' 
            };
        }

        if (estado !== 'pendiente') {
            return { 
                valido: false, 
                mensaje: `No se puede modificar un ticket ${estado}` 
            };
        }

        return { valido: true };
    }
}

/**
 * Validaciones de Cliente
 */
class ValidadorCliente {
    static validarDNI(dni) {
        if (!dni || dni === '') {
            return { valido: true }; // DNI opcional
        }

        const dniRegex = /^\d{7,8}$/;

        if (!dniRegex.test(dni)) {
            return { 
                valido: false, 
                mensaje: 'DNI inválido. Debe tener 7 u 8 dígitos' 
            };
        }

        return { valido: true, valor: dni };
    }

    static validarCUIT(cuit) {
        if (!cuit || cuit === '') {
            return { valido: true }; // CUIT opcional
        }

        const cuitRegex = /^\d{2}-\d{8}-\d{1}$/;

        if (!cuitRegex.test(cuit)) {
            return { 
                valido: false, 
                mensaje: 'CUIT inválido. Formato: XX-XXXXXXXX-X' 
            };
        }

        return { valido: true, valor: cuit };
    }

    static validarEmail(email) {
        if (!email || email === '') {
            return { valido: true }; // Email opcional
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!emailRegex.test(email)) {
            return { 
                valido: false, 
                mensaje: 'Email inválido' 
            };
        }

        return { valido: true, valor: email };
    }

    static validarTelefono(telefono) {
        if (!telefono || telefono === '') {
            return { valido: true }; // Teléfono opcional
        }

        const telefonoLimpio = telefono.replace(/[\s\-\(\)]/g, '');
        
        if (telefonoLimpio.length < 7 || telefonoLimpio.length > 15) {
            return { 
                valido: false, 
                mensaje: 'Teléfono inválido' 
            };
        }

        return { valido: true, valor: telefono };
    }
}

/**
 * Validación Integral de Venta
 */
class ValidadorVentaCompleta {
    static validarVentaCompleta(datosVenta) {
        const errores = [];
        const { carrito, metodoPago, descuento, cliente } = datosVenta;

        // Validar carrito
        const validacionCarrito = ValidadorCarrito.validarCarritoVacio(carrito);
        if (!validacionCarrito.valido) {
            errores.push(validacionCarrito.mensaje);
        }

        // Validar productos individuales
        if (carrito && carrito.length > 0) {
            for (const item of carrito) {
                const validacionStock = ValidadorProducto.validarStock(item.cantidad, item.stock);
                if (!validacionStock.valido) {
                    errores.push(`${item.descripcion}: ${validacionStock.mensaje}`);
                }

                const validacionPrecio = ValidadorProducto.validarPrecio(item.precio);
                if (!validacionPrecio.valido) {
                    errores.push(`${item.descripcion}: ${validacionPrecio.mensaje}`);
                }
            }
        }

        // Validar método de pago
        const validacionPago = ValidadorPago.validarMetodoPago(metodoPago);
        if (!validacionPago.valido) {
            errores.push(validacionPago.mensaje);
        }

        // Calcular totales
        const subtotal = carrito.reduce((sum, item) => sum + parseFloat(item.subtotal), 0);
        
        // Validar descuento
        const validacionDescuento = ValidadorCarrito.validarDescuento(descuento, subtotal);
        if (!validacionDescuento.valido) {
            errores.push(validacionDescuento.mensaje);
        }

        // Validar total
        let descuentoMonto = 0;
        if (descuento && descuento.tipo === 'porcentaje') {
            descuentoMonto = subtotal * (descuento.valor / 100);
        } else if (descuento && descuento.tipo === 'monto') {
            descuentoMonto = descuento.valor;
        }

        const total = subtotal - descuentoMonto;
        const validacionTotal = ValidadorCarrito.validarTotal(total);
        if (!validacionTotal.valido) {
            errores.push(validacionTotal.mensaje);
        }

        // Validar cliente si existe
        if (cliente) {
            if (cliente.dni) {
                const validacionDNI = ValidadorCliente.validarDNI(cliente.dni);
                if (!validacionDNI.valido) errores.push(validacionDNI.mensaje);
            }

            if (cliente.email) {
                const validacionEmail = ValidadorCliente.validarEmail(cliente.email);
                if (!validacionEmail.valido) errores.push(validacionEmail.mensaje);
            }

            if (cliente.telefono) {
                const validacionTelefono = ValidadorCliente.validarTelefono(cliente.telefono);
                if (!validacionTelefono.valido) errores.push(validacionTelefono.mensaje);
            }
        }

        return {
            valido: errores.length === 0,
            errores: errores,
            totales: {
                subtotal,
                descuento: descuentoMonto,
                total
            }
        };
    }
}

/**
 * Utilidades de Validación
 */
class UtilidadesValidacion {
    static sanitizarNumero(valor) {
        const num = parseFloat(valor);
        return isNaN(num) ? 0 : num;
    }

    static sanitizarEntero(valor) {
        const num = parseInt(valor);
        return isNaN(num) ? 0 : num;
    }

    static formatearMoneda(valor) {
        return new Intl.NumberFormat('es-AR', {
            style: 'currency',
            currency: 'ARS'
        }).format(valor);
    }

    static mostrarErrores(errores, contenedor = null) {
        if (!errores || errores.length === 0) return;

        const mensajeHTML = errores.map(error => 
            `<div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                ${error}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>`
        ).join('');

        if (contenedor) {
            contenedor.innerHTML = mensajeHTML;
        } else {
            const defaultContainer = document.querySelector('.page-content') || document.body;
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = mensajeHTML;
            defaultContainer.insertBefore(tempDiv, defaultContainer.firstChild);
        }

        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            document.querySelectorAll('.alert-danger').forEach(alert => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, 5000);
    }
}

// Exportar para uso global
window.ValidadorProducto = ValidadorProducto;
window.ValidadorCarrito = ValidadorCarrito;
window.ValidadorPago = ValidadorPago;
window.ValidadorTicket = ValidadorTicket;
window.ValidadorCliente = ValidadorCliente;
window.ValidadorVentaCompleta = ValidadorVentaCompleta;
window.UtilidadesValidacion = UtilidadesValidacion;

console.log('✓ Sistema de validaciones cargado correctamente');