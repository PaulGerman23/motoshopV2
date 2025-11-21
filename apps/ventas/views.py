# apps/ventas/views.py - VERSIÓN CORREGIDA SIN MODELO CAJA

from .models import Venta, DetalleVenta, AuditoriaMovimiento
from apps.clientes.models import Cliente
from apps.inventario.models import Producto
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from decimal import Decimal
import json


@login_required
def lista_ventas(request):
    """Lista todas las ventas"""
    ventas = Venta.objects.filter(estado=1).select_related('cliente', 'usuario').order_by('-fecha')
    return render(request, 'ventas/lista_ventas.html', {'ventas': ventas})


@login_required
def crear_venta(request):
    """Crea una nueva venta"""
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obtener datos del formulario
                cliente_id = request.POST.get('cliente')
                tipo_pago = request.POST.get('tipo_pago')
                observacion = request.POST.get('observacion', '')
                
                # Validar tipo de pago
                tipos_validos = ['efectivo', 'debito', 'credito', 'transferencia', 'mixto']
                if tipo_pago not in tipos_validos:
                    raise ValueError('Método de pago inválido')
                
                # Obtener productos del JSON
                productos_json = request.POST.get('productos')
                if not productos_json:
                    raise ValueError('No hay productos en el carrito')
                
                productos = json.loads(productos_json)
                
                if not productos:
                    raise ValueError('El carrito está vacío')
                
                # Obtener descuento
                descuento_json = request.POST.get('descuento', '{}')
                descuento = json.loads(descuento_json)
                
                # Calcular subtotal
                subtotal = Decimal('0')
                for prod in productos:
                    subtotal += Decimal(str(prod['subtotal']))
                
                # Calcular descuento
                descuento_monto = Decimal('0')
                descuento_porcentaje = Decimal('0')
                
                if descuento.get('tipo') == 'porcentaje':
                    descuento_porcentaje = Decimal(str(descuento.get('valor', 0)))
                    descuento_monto = subtotal * (descuento_porcentaje / 100)
                elif descuento.get('tipo') == 'monto':
                    descuento_monto = Decimal(str(descuento.get('valor', 0)))
                
                # Calcular total
                total = subtotal - descuento_monto
                
                if total <= 0:
                    raise ValueError('El total debe ser mayor a 0')
                
                # Validar pago mixto
                es_pago_mixto = False
                monto_efectivo = Decimal('0')
                monto_tarjeta = Decimal('0')
                
                if tipo_pago == 'mixto':
                    es_pago_mixto = True
                    monto_efectivo = Decimal(str(request.POST.get('monto_efectivo', 0)))
                    monto_tarjeta = Decimal(str(request.POST.get('monto_tarjeta', 0)))
                    
                    if monto_efectivo + monto_tarjeta != total:
                        raise ValueError(f'Los montos del pago mixto deben sumar ${total}')
                
                # Generar código de venta
                ultimo_codigo = Venta.objects.order_by('-codigo_venta').first()
                nuevo_codigo = (ultimo_codigo.codigo_venta + 1) if ultimo_codigo else 1000
                
                # Crear venta
                venta = Venta.objects.create(
                    cliente_id=cliente_id if cliente_id else None,
                    usuario=request.user,
                    subtotal=subtotal,
                    descuento_porcentaje=descuento_porcentaje,
                    descuento_monto=descuento_monto,
                    total=total,
                    tipo_pago=tipo_pago,
                    es_pago_mixto=es_pago_mixto,
                    monto_efectivo=monto_efectivo,
                    monto_tarjeta=monto_tarjeta,
                    observacion=observacion,
                    codigo_venta=nuevo_codigo,
                    estado_venta=2  # Pagado
                )
                
                # Crear detalles y actualizar stock
                for prod in productos:
                    producto = Producto.objects.select_for_update().get(id=prod['producto_id'])
                    cantidad = int(prod['cantidad'])
                    
                    if producto.stock < cantidad:
                        raise ValueError(f'Stock insuficiente para {producto.descripcion}. Stock actual: {producto.stock}')
                    
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=Decimal(str(prod['precio'])),
                        subtotal=Decimal(str(prod['subtotal']))
                    )
                    
                    producto.stock -= cantidad
                    producto.save()
                
                # Registrar auditoría
                AuditoriaMovimiento.registrar(
                    usuario=request.user,
                    accion='venta_crear',
                    descripcion=f'Venta #{nuevo_codigo} creada por ${total}',
                    venta=venta,
                    datos_adicionales={
                        'codigo_venta': nuevo_codigo,
                        'total': float(total),
                        'tipo_pago': tipo_pago,
                        'cantidad_productos': len(productos),
                        'es_pago_mixto': es_pago_mixto
                    },
                    request=request
                )
                
                messages.success(request, f'Venta #{nuevo_codigo} registrada exitosamente.')
                return redirect('detalle_venta', pk=venta.id)
                
        except ValueError as e:
            messages.error(request, str(e))
        except json.JSONDecodeError:
            messages.error(request, 'Error al procesar los datos del carrito')
        except Producto.DoesNotExist:
            messages.error(request, 'Uno o más productos no existen')
        except Exception as e:
            messages.error(request, f'Error al registrar la venta: {str(e)}')
    
    # GET request
    clientes = Cliente.objects.filter(estado=1).order_by('nombre')
    productos = Producto.objects.filter(estado=1, stock__gt=0).select_related('categoria', 'proveedor').order_by('descripcion')
    
    return render(request, 'ventas/crear_venta.html', {
        'clientes': clientes,
        'productos': productos
    })


@login_required
def detalle_venta(request, pk):
    """Muestra el detalle de una venta"""
    venta = get_object_or_404(Venta, pk=pk)
    detalles = venta.detalles.filter(status=1).select_related('producto')
    
    return render(request, 'ventas/detalle_venta.html', {
        'venta': venta,
        'detalles': detalles
    })


@login_required
def anular_venta(request, pk):
    """Anula una venta y restaura el stock"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                venta = get_object_or_404(Venta, pk=pk)
                
                if venta.estado_venta == 0:
                    messages.warning(request, 'Esta venta ya está anulada')
                    return redirect('detalle_venta', pk=pk)
                
                # Restaurar stock
                for detalle in venta.detalles.filter(status=1):
                    if detalle.producto:
                        producto = Producto.objects.select_for_update().get(id=detalle.producto.id)
                        producto.stock += detalle.cantidad
                        producto.save()
                
                # Anular venta
                venta.estado_venta = 0
                venta.save()
                
                messages.success(request, f'Venta #{venta.codigo_venta} anulada correctamente')
                return redirect('lista_ventas')
                
        except Exception as e:
            messages.error(request, f'Error al anular la venta: {str(e)}')
    
    return redirect('detalle_venta', pk=pk)