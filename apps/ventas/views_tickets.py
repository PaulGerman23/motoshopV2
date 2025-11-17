# apps/ventas/views_tickets.py
# AGREGAR ESTAS VISTAS AL PROYECTO

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.views.decorators.http import require_http_methods
import json
from decimal import Decimal

from .models import Ticket, DetalleTicket, Venta, DetalleVenta
from apps.inventario.models import Producto
from apps.clientes.models import Cliente


@login_required
@require_http_methods(["POST"])
def guardar_ticket(request):
    """Guarda un ticket (venta en espera)"""
    try:
        data = json.loads(request.body)
        productos = data.get('productos', [])
        descuento = data.get('descuento', {'tipo': 'porcentaje', 'valor': 0})
        cliente_id = data.get('cliente_id')
        observacion = data.get('observacion', '')
        
        if not productos:
            return JsonResponse({'success': False, 'error': 'No hay productos en el carrito'})
        
        with transaction.atomic():
            # Generar código de ticket
            ultimo_ticket = Ticket.objects.order_by('-codigo_ticket').first()
            nuevo_codigo = (ultimo_ticket.codigo_ticket + 1) if ultimo_ticket else 1
            
            # Crear ticket
            ticket = Ticket.objects.create(
                ticket_id=f"TKT-{nuevo_codigo:06d}",
                codigo_ticket=nuevo_codigo,
                usuario=request.user,
                cliente_id=cliente_id if cliente_id else None,
                observacion=observacion,
                descuento_porcentaje=descuento['valor'] if descuento['tipo'] == 'porcentaje' else 0,
                descuento_monto=descuento['valor'] if descuento['tipo'] == 'monto' else 0,
                estado='pendiente'
            )
            
            # Crear detalles
            subtotal = Decimal('0')
            for prod_data in productos:
                producto = Producto.objects.get(id=prod_data['producto_id'])
                
                # Validar stock
                if producto.stock < int(prod_data['cantidad']):
                    raise ValueError(f'Stock insuficiente para {producto.descripcion}')
                
                detalle = DetalleTicket.objects.create(
                    ticket=ticket,
                    producto=producto,
                    descripcion=producto.descripcion,
                    cantidad=int(prod_data['cantidad']),
                    precio_unitario=Decimal(str(prod_data['precio'])),
                    subtotal=Decimal(str(prod_data['subtotal']))
                )
                subtotal += detalle.subtotal
            
            # Calcular totales
            ticket.subtotal = subtotal
            if ticket.descuento_porcentaje > 0:
                ticket.descuento = subtotal * (ticket.descuento_porcentaje / 100)
            else:
                ticket.descuento = ticket.descuento_monto
            ticket.total = subtotal - ticket.descuento
            ticket.save()
        
        return JsonResponse({
            'success': True,
            'ticket': {
                'id': ticket.id,
                'codigo_ticket': ticket.codigo_ticket,
                'ticket_id': ticket.ticket_id,
                'total': float(ticket.total)
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def lista_tickets(request):
    """Devuelve la lista de tickets pendientes"""
    try:
        tickets = Ticket.objects.filter(
            usuario=request.user,
            estado='pendiente'
        ).order_by('-fecha_creacion')
        
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'id': ticket.id,
                'codigo_ticket': ticket.codigo_ticket,
                'ticket_id': ticket.ticket_id,
                'total': float(ticket.total),
                'fecha_creacion': ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'items_count': ticket.detalles.filter(activo=True).count()
            })
        
        return JsonResponse({'tickets': tickets_data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def recuperar_ticket(request, ticket_id):
    """Recupera un ticket para continuar editándolo"""
    try:
        ticket = get_object_or_404(Ticket, id=ticket_id, usuario=request.user, estado='pendiente')
        
        # Obtener productos del ticket
        productos = []
        for detalle in ticket.detalles.filter(activo=True):
            # Verificar stock actual
            if detalle.producto and detalle.producto.stock < detalle.cantidad:
                return JsonResponse({
                    'success': False,
                    'error': f'Stock insuficiente para {detalle.producto.descripcion}. Stock actual: {detalle.producto.stock}'
                })
            
            productos.append({
                'producto_id': str(detalle.producto.id),
                'descripcion': detalle.descripcion,
                'precio': float(detalle.precio_unitario),
                'cantidad': detalle.cantidad,
                'stock': detalle.producto.stock if detalle.producto else 0,
                'subtotal': float(detalle.subtotal)
            })
        
        # Preparar descuento
        if ticket.descuento_porcentaje > 0:
            descuento = {'tipo': 'porcentaje', 'valor': float(ticket.descuento_porcentaje)}
        else:
            descuento = {'tipo': 'monto', 'valor': float(ticket.descuento_monto)}
        
        return JsonResponse({
            'success': True,
            'ticket': {
                'id': ticket.id,
                'codigo_ticket': ticket.codigo_ticket,
                'productos': productos,
                'descuento': descuento,
                'cliente_id': ticket.cliente.id if ticket.cliente else None,
                'observacion': ticket.observacion or ''
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def finalizar_ticket(request, ticket_id):
    """Finaliza un ticket y crea la venta definitiva"""
    try:
        data = json.loads(request.body)
        tipo_pago = data.get('tipo_pago')
        
        if not tipo_pago:
            return JsonResponse({'success': False, 'error': 'Debe especificar un método de pago'})
        
        ticket = get_object_or_404(Ticket, id=ticket_id, usuario=request.user, estado='pendiente')
        
        with transaction.atomic():
            # Establecer tipo de pago
            ticket.tipo_pago = tipo_pago
            ticket.save()
            
            # Finalizar ticket (esto crea la venta)
            venta = ticket.finalizar()
        
        return JsonResponse({
            'success': True,
            'venta': {
                'id': venta.id,
                'codigo_venta': venta.codigo_venta,
                'total': float(venta.total)
            }
        })
        
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al finalizar ticket: {str(e)}'})


@login_required
@require_http_methods(["POST"])
def cancelar_ticket(request, ticket_id):
    """Cancela un ticket"""
    try:
        ticket = get_object_or_404(Ticket, id=ticket_id, usuario=request.user)
        
        if ticket.estado == 'finalizado':
            return JsonResponse({'success': False, 'error': 'No se puede cancelar un ticket finalizado'})
        
        ticket.cancelar()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})