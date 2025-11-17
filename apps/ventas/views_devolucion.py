# apps/ventas/views_devolucion.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal

from .models import (
    Venta, DetalleVenta, Devolucion, DetalleDevolucion, 
    NotaCredito, AuditoriaMovimiento
)


@login_required
def lista_devoluciones(request):
    """Lista todas las devoluciones"""
    estado_filter = request.GET.get('estado', '')
    
    devoluciones = Devolucion.objects.select_related(
        'venta_original', 
        'usuario_solicita', 
        'usuario_aprueba'
    ).order_by('-fecha_solicitud')
    
    if estado_filter:
        devoluciones = devoluciones.filter(estado=estado_filter)
    
    # Estadísticas
    stats = {
        'total': devoluciones.count(),
        'pendientes': devoluciones.filter(estado='pendiente').count(),
        'aprobadas': devoluciones.filter(estado='aprobada').count(),
        'procesadas': devoluciones.filter(estado='procesada').count(),
        'rechazadas': devoluciones.filter(estado='rechazada').count(),
    }
    
    context = {
        'devoluciones': devoluciones[:50],  # Últimas 50
        'stats': stats,
        'estado_actual': estado_filter
    }
    
    return render(request, 'ventas/lista_devoluciones.html', context)


@login_required
def crear_devolucion(request, venta_id):
    """Crea una nueva devolución"""
    venta = get_object_or_404(Venta, id=venta_id)
    
    # Verificar si la venta puede ser devuelta
    if not venta.puede_devolverse():
        messages.error(request, 'Esta venta no puede ser devuelta.')
        return redirect('detalle_venta', pk=venta_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                motivo = request.POST.get('motivo')
                descripcion_motivo = request.POST.get('descripcion_motivo')
                
                # Generar código de devolución
                ultimo_codigo = Devolucion.objects.order_by('-id').first()
                nuevo_codigo = (ultimo_codigo.id + 1) if ultimo_codigo else 1000
                
                # Crear devolución
                devolucion = Devolucion.objects.create(
                    venta_original=venta,
                    codigo_devolucion=f"DEV-{nuevo_codigo:06d}",
                    motivo=motivo,
                    descripcion_motivo=descripcion_motivo,
                    usuario_solicita=request.user
                )
                
                # Procesar productos a devolver
                productos_seleccionados = request.POST.getlist('producto_id')
                
                if not productos_seleccionados:
                    raise ValueError("Debe seleccionar al menos un producto para devolver")
                
                for producto_id in productos_seleccionados:
                    cantidad = int(request.POST.get(f'cantidad_{producto_id}', 0))
                    
                    if cantidad <= 0:
                        continue
                    
                    # Buscar el detalle de venta original
                    detalle_original = DetalleVenta.objects.get(
                        venta=venta,
                        producto_id=producto_id
                    )
                    
                    # Validar cantidad
                    if cantidad > detalle_original.cantidad:
                        raise ValueError(
                            f"La cantidad a devolver no puede ser mayor a la cantidad original"
                        )
                    
                    # Crear detalle de devolución
                    DetalleDevolucion.objects.create(
                        devolucion=devolucion,
                        producto=detalle_original.producto,
                        descripcion_producto=detalle_original.producto.descripcion if detalle_original.producto else "Producto eliminado",
                        cantidad=cantidad,
                        precio_unitario=detalle_original.precio_unitario,
                        motivo_especifico=request.POST.get(f'motivo_especifico_{producto_id}', '')
                    )
                
                # Calcular total
                devolucion.calcular_total()
                
                # Registrar auditoría
                AuditoriaMovimiento.registrar(
                    usuario=request.user,
                    accion='devolucion_crear',
                    descripcion=f'Devolución creada para venta #{venta.codigo_venta}',
                    venta=venta,
                    devolucion=devolucion,
                    datos_adicionales={
                        'codigo_devolucion': devolucion.codigo_devolucion,
                        'motivo': motivo,
                        'monto': float(devolucion.monto_total)
                    },
                    request=request
                )
                
                messages.success(
                    request, 
                    f'Devolución {devolucion.codigo_devolucion} creada exitosamente. Pendiente de aprobación.'
                )
                return redirect('detalle_devolucion', devolucion_id=devolucion.id)
                
        except Exception as e:
            messages.error(request, f'Error al crear la devolución: {str(e)}')
    
    # GET - Mostrar formulario
    detalles = venta.detalles.filter(status=1).select_related('producto')
    
    context = {
        'venta': venta,
        'detalles': detalles
    }
    
    return render(request, 'ventas/crear_devolucion.html', context)


@login_required
def detalle_devolucion(request, devolucion_id):
    """Muestra el detalle de una devolución"""
    devolucion = get_object_or_404(
        Devolucion.objects.select_related('venta_original', 'usuario_solicita', 'usuario_aprueba'),
        id=devolucion_id
    )
    
    detalles = devolucion.detalles.select_related('producto').all()
    
    # Verificar si tiene nota de crédito
    nota_credito = None
    if hasattr(devolucion, 'nota_credito'):
        nota_credito = devolucion.nota_credito
    
    context = {
        'devolucion': devolucion,
        'detalles': detalles,
        'nota_credito': nota_credito
    }
    
    return render(request, 'ventas/detalle_devolucion.html', context)


@login_required
def aprobar_devolucion(request, devolucion_id):
    """Aprueba una devolución"""
    devolucion = get_object_or_404(Devolucion, id=devolucion_id)
    
    if devolucion.estado != 'pendiente':
        messages.error(request, 'Solo se pueden aprobar devoluciones pendientes')
        return redirect('detalle_devolucion', devolucion_id=devolucion_id)
    
    if request.method == 'POST':
        observaciones = request.POST.get('observaciones_aprobacion', '')
        
        devolucion.estado = 'aprobada'
        devolucion.usuario_aprueba = request.user
        devolucion.observaciones_aprobacion = observaciones
        devolucion.save()
        
        # Registrar auditoría
        AuditoriaMovimiento.registrar(
            usuario=request.user,
            accion='devolucion_aprobar',
            descripcion=f'Devolución {devolucion.codigo_devolucion} aprobada',
            devolucion=devolucion,
            venta=devolucion.venta_original,
            request=request
        )
        
        messages.success(request, 'Devolución aprobada exitosamente')
        return redirect('detalle_devolucion', devolucion_id=devolucion_id)
    
    return redirect('detalle_devolucion', devolucion_id=devolucion_id)


@login_required
def rechazar_devolucion(request, devolucion_id):
    """Rechaza una devolución"""
    devolucion = get_object_or_404(Devolucion, id=devolucion_id)
    
    if devolucion.estado != 'pendiente':
        messages.error(request, 'Solo se pueden rechazar devoluciones pendientes')
        return redirect('detalle_devolucion', devolucion_id=devolucion_id)
    
    if request.method == 'POST':
        observaciones = request.POST.get('observaciones_rechazo', '')
        
        devolucion.estado = 'rechazada'
        devolucion.usuario_aprueba = request.user
        devolucion.observaciones_aprobacion = observaciones
        devolucion.save()
        
        # Registrar auditoría
        AuditoriaMovimiento.registrar(
            usuario=request.user,
            accion='devolucion_rechazar',
            descripcion=f'Devolución {devolucion.codigo_devolucion} rechazada',
            devolucion=devolucion,
            venta=devolucion.venta_original,
            datos_adicionales={'motivo_rechazo': observaciones},
            request=request
        )
        
        messages.warning(request, 'Devolución rechazada')
        return redirect('detalle_devolucion', devolucion_id=devolucion_id)
    
    return redirect('detalle_devolucion', devolucion_id=devolucion_id)


@login_required
def procesar_devolucion(request, devolucion_id):
    """Procesa una devolución aprobada y genera nota de crédito"""
    devolucion = get_object_or_404(Devolucion, id=devolucion_id)
    
    if not devolucion.puede_procesarse():
        messages.error(request, 'Esta devolución no puede ser procesada')
        return redirect('detalle_devolucion', devolucion_id=devolucion_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Procesar devolución
                nota_credito = devolucion.procesar(request.user)
                
                # Registrar auditoría
                AuditoriaMovimiento.registrar(
                    usuario=request.user,
                    accion='devolucion_procesar',
                    descripcion=f'Devolución {devolucion.codigo_devolucion} procesada. Nota de crédito {nota_credito.codigo_nota} generada',
                    devolucion=devolucion,
                    venta=devolucion.venta_original,
                    datos_adicionales={
                        'nota_credito': nota_credito.codigo_nota,
                        'monto': float(nota_credito.monto)
                    },
                    request=request
                )
                
                messages.success(
                    request, 
                    f'Devolución procesada. Nota de crédito {nota_credito.codigo_nota} generada por ${nota_credito.monto}'
                )
                return redirect('detalle_nota_credito', nota_id=nota_credito.id)
                
        except Exception as e:
            messages.error(request, f'Error al procesar la devolución: {str(e)}')
    
    return redirect('detalle_devolucion', devolucion_id=devolucion_id)


# ================================================
# VISTAS PARA NOTAS DE CRÉDITO
# ================================================

@login_required
def lista_notas_credito(request):
    """Lista todas las notas de crédito"""
    estado_filter = request.GET.get('estado', '')
    
    notas = NotaCredito.objects.select_related(
        'devolucion', 
        'venta_original'
    ).order_by('-fecha_emision')
    
    if estado_filter:
        notas = notas.filter(estado=estado_filter)
    
    # Solo mostrar vigentes por defecto
    if not estado_filter:
        notas = notas.exclude(estado__in=['vencida', 'utilizada', 'cancelada'])
    
    context = {
        'notas': notas[:50],
        'estado_actual': estado_filter
    }
    
    return render(request, 'ventas/lista_notas_credito.html', context)


@login_required
def detalle_nota_credito(request, nota_id):
    """Muestra el detalle de una nota de crédito"""
    nota = get_object_or_404(
        NotaCredito.objects.select_related('devolucion', 'venta_original'),
        id=nota_id
    )
    
    # Obtener aplicaciones
    aplicaciones = nota.aplicaciones.select_related('venta').order_by('-fecha_aplicacion')
    
    context = {
        'nota': nota,
        'aplicaciones': aplicaciones,
        'vigente': nota.esta_vigente()
    }
    
    return render(request, 'ventas/detalle_nota_credito.html', context)


@login_required
def aplicar_nota_credito(request, nota_id):
    """Aplica una nota de crédito a una venta"""
    nota = get_object_or_404(NotaCredito, id=nota_id)
    
    if not nota.esta_vigente():
        return JsonResponse({
            'success': False,
            'error': 'Esta nota de crédito no está vigente'
        })
    
    if request.method == 'POST':
        try:
            venta_id = request.POST.get('venta_id')
            monto_aplicar = Decimal(request.POST.get('monto_aplicar', '0'))
            
            venta = Venta.objects.get(id=venta_id)
            
            # Aplicar nota
            nota.aplicar_a_venta(venta, monto_aplicar)
            
            # Registrar auditoría
            AuditoriaMovimiento.registrar(
                usuario=request.user,
                accion='nota_credito_aplicar',
                descripcion=f'Nota de crédito {nota.codigo_nota} aplicada a venta #{venta.codigo_venta}',
                venta=venta,
                datos_adicionales={
                    'nota_credito': nota.codigo_nota,
                    'monto_aplicado': float(monto_aplicar),
                    'saldo_restante': float(nota.saldo_disponible)
                },
                request=request
            )
            
            return JsonResponse({
                'success': True,
                'saldo_restante': float(nota.saldo_disponible),
                'mensaje': f'Nota de crédito aplicada exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# ================================================
# VISTA PARA AUDITORÍA
# ================================================

@login_required
def auditoria_movimientos(request):
    """Muestra el registro de auditoría"""
    from datetime import datetime, timedelta
    
    # Filtros
    accion_filter = request.GET.get('accion', '')
    usuario_filter = request.GET.get('usuario', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    movimientos = AuditoriaMovimiento.objects.select_related('usuario', 'venta', 'devolucion')
    
    if accion_filter:
        movimientos = movimientos.filter(accion=accion_filter)
    
    if usuario_filter:
        movimientos = movimientos.filter(usuario_id=usuario_filter)
    
    if fecha_desde:
        movimientos = movimientos.filter(fecha__gte=fecha_desde)
    
    if fecha_hasta:
        movimientos = movimientos.filter(fecha__lte=fecha_hasta)
    
    # Por defecto mostrar últimos 7 días
    if not fecha_desde and not fecha_hasta:
        hace_7_dias = datetime.now() - timedelta(days=7)
        movimientos = movimientos.filter(fecha__gte=hace_7_dias)
    
    movimientos = movimientos.order_by('-fecha')[:100]
    
    # Obtener usuarios para filtro
    from django.contrib.auth.models import User
    usuarios = User.objects.filter(is_active=True).order_by('username')
    
    context = {
        'movimientos': movimientos,
        'usuarios': usuarios,
        'acciones': AuditoriaMovimiento.TIPOS_ACCION
    }
    
    return render(request, 'ventas/auditoria_movimientos.html', context)