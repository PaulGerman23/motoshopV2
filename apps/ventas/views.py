from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Venta, DetalleVenta
from apps.clientes.models import Cliente
from apps.inventario.models import Producto
import json

@login_required
def lista_ventas(request):
    ventas = Venta.objects.filter(estado=1).select_related('cliente', 'usuario')
    return render(request, 'ventas/lista_ventas.html', {'ventas': ventas})

@login_required
def crear_venta(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obtener datos del formulario
                cliente_id = request.POST.get('cliente')
                tipo_pago = request.POST.get('tipo_pago')
                observacion = request.POST.get('observacion', '')
                
                # Obtener productos del JSON
                productos_json = request.POST.get('productos')
                productos = json.loads(productos_json)
                
                # Calcular total
                total = sum(float(p['subtotal']) for p in productos)
                
                # Generar código de venta
                ultimo_codigo = Venta.objects.order_by('-codigo_venta').first()
                nuevo_codigo = (ultimo_codigo.codigo_venta + 1) if ultimo_codigo else 1
                
                # Crear venta
                venta = Venta.objects.create(
                    cliente_id=cliente_id if cliente_id else None,
                    usuario=request.user,
                    total=total,
                    tipo_pago=tipo_pago,
                    observacion=observacion,
                    codigo_venta=nuevo_codigo,
                    estado_venta=2  # Pagado
                )
                
                # Crear detalles y actualizar stock
                for prod in productos:
                    producto = Producto.objects.get(id=prod['producto_id'])
                    cantidad = int(prod['cantidad'])
                    
                    # Verificar stock
                    if producto.stock < cantidad:
                        raise Exception(f'Stock insuficiente para {producto.descripcion}')
                    
                    # Crear detalle
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio_venta,
                        subtotal=float(prod['subtotal'])
                    )
                    
                    # Actualizar stock
                    producto.stock -= cantidad
                    producto.save()
                
                messages.success(request, f'Venta #{nuevo_codigo} registrada exitosamente.')
                return redirect('lista_ventas')
                
        except Exception as e:
            messages.error(request, f'Error al registrar la venta: {str(e)}')
    
    clientes = Cliente.objects.filter(estado=1)
    productos = Producto.objects.filter(estado=1, stock__gt=0)
    return render(request, 'ventas/crear_venta.html', {
        'clientes': clientes,
        'productos': productos
    })

@login_required
def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    detalles = venta.detalles.filter(status=1).select_related('producto')
    return render(request, 'ventas/detalle_venta.html', {
        'venta': venta,
        'detalles': detalles
    })