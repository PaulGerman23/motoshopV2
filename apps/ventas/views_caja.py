# apps/ventas/views_caja.py - ARCHIVO NUEVO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal

from .models import Caja, Venta, AuditoriaMovimiento


# ======================================================
#  APERTURA DE CAJA
# ======================================================

@login_required
def abrir_caja(request):
    """Abre una nueva caja para el usuario"""
    # Verificar que no tenga caja abierta
    if Caja.tiene_caja_abierta(request.user):
        messages.warning(request, 'Ya tienes una caja abierta.')
        return redirect('caja_actual')
    
    if request.method == 'POST':
        try:
            monto_inicial = Decimal(request.POST.get('monto_inicial', '0'))
            observaciones = request.POST.get('observaciones_apertura', '')
            
            if monto_inicial < 0:
                raise ValueError('El monto inicial no puede ser negativo')
            
            caja = Caja.objects.create(
                usuario=request.user,
                monto_inicial=monto_inicial,
                observaciones_apertura=observaciones,
                estado='abierta'
            )
            
            # Registrar en auditoría
            AuditoriaMovimiento.registrar(
                usuario=request.user,
                accion='caja_abrir',
                descripcion=f'Caja #{caja.id} abierta con monto inicial ${monto_inicial}',
                datos_adicionales={
                    'caja_id': caja.id,
                    'monto_inicial': float(monto_inicial)
                },
                request=request
            )
            
            messages.success(request, f'Caja abierta correctamente con ${monto_inicial}')
            
            # Si viene de crear_venta, redirigir allá
            next_url = request.POST.get('next', 'caja_actual')
            return redirect(next_url)
            
        except Exception as e:
            messages.error(request, f'Error al abrir la caja: {str(e)}')
    
    # GET - Mostrar modal/formulario
    next_url = request.GET.get('next', 'caja_actual')
    return render(request, 'ventas/abrir_caja.html', {'next_url': next_url})


# ======================================================
#  CAJA ACTUAL
# ======================================================

@login_required
def caja_actual(request):
    """Muestra la caja actual del usuario"""
    caja = Caja.obtener_caja_abierta(request.user)
    
    if not caja:
        return render(request, 'ventas/caja_actual.html', {
            'tiene_caja': False,
            'mensaje': 'No tienes una caja abierta actualmente.'
        })
    
    # Calcular totales actualizados
    caja.calcular_totales()
    
    # Obtener ventas recientes de esta caja
    ventas_recientes = caja.ventas.filter(
        estado_venta__in=[1, 2]
    ).select_related('cliente', 'usuario').order_by('-fecha')[:10]
    
    context = {
        'tiene_caja': True,
        'caja': caja,
        'total_efectivo': caja.total_efectivo,
        'total_debito': caja.total_debito,
        'total_credito': caja.total_credito,
        'total_transferencia': caja.total_transferencia,
        'total_mixto': caja.total_mixto,
        'total_ventas': caja.total_ventas,
        'cantidad_ventas': caja.cantidad_ventas,
        'ventas_recientes': ventas_recientes,
    }
    
    return render(request, 'ventas/caja_actual.html', context)


# ======================================================
#  CERRAR CAJA
# ======================================================

@login_required
def cerrar_caja(request):
    """Muestra el formulario de cierre de caja"""
    caja = Caja.obtener_caja_abierta(request.user)
    
    if not caja:
        messages.error(request, 'No tienes una caja abierta para cerrar.')
        return redirect('caja_actual')
    
    # Recalcular totales antes de mostrar
    caja.calcular_totales()
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                monto_final_real = Decimal(request.POST.get('monto_final_real', '0'))
                egresos = Decimal(request.POST.get('egresos', '0'))
                detalle_egresos = request.POST.get('detalle_egresos', '')
                observaciones_cierre = request.POST.get('observaciones_cierre', '')
                
                if monto_final_real < 0:
                    raise ValueError('El monto final no puede ser negativo')
                
                if egresos < 0:
                    raise ValueError('Los egresos no pueden ser negativos')
                
                # Cerrar la caja
                caja.cerrar(
                    monto_final_real=monto_final_real,
                    observaciones_cierre=observaciones_cierre,
                    egresos=egresos,
                    detalle_egresos=detalle_egresos
                )
                
                messages.success(request, f'Caja #{caja.id} cerrada correctamente.')
                return redirect('detalle_caja', caja_id=caja.id)
                
        except Exception as e:
            messages.error(request, f'Error al cerrar la caja: {str(e)}')
    
    # GET
    context = {
        'caja': caja,
        'monto_esperado': caja.monto_inicial + caja.total_efectivo - caja.egresos,
    }
    
    return render(request, 'ventas/cerrar_caja.html', context)


# ======================================================
#  HISTORIAL DE CAJAS
# ======================================================

@login_required
def historial_cajas(request):
    """Muestra el historial de cajas"""
    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    usuario_id = request.GET.get('usuario')
    
    cajas = Caja.objects.select_related('usuario').order_by('-fecha_apertura')
    
    if fecha_desde:
        cajas = cajas.filter(fecha_apertura__date__gte=fecha_desde)
    
    if fecha_hasta:
        cajas = cajas.filter(fecha_apertura__date__lte=fecha_hasta)
    
    if usuario_id:
        cajas = cajas.filter(usuario_id=usuario_id)
    
    # Paginación (opcional)
    cajas = cajas[:50]  # Últimas 50
    
    # Obtener usuarios para filtro
    from django.contrib.auth.models import User
    usuarios = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    context = {
        'cajas': cajas,
        'usuarios': usuarios,
    }
    
    return render(request, 'ventas/historial_cajas.html', context)


# ======================================================
#  DETALLE DE CAJA
# ======================================================

@login_required
def detalle_caja(request, caja_id):
    """Muestra el detalle completo de una caja"""
    caja = get_object_or_404(Caja, id=caja_id)
    
    # Verificar permisos (opcional: solo el dueño o admin)
    if caja.usuario != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para ver esta caja.')
        return redirect('historial_cajas')
    
    # Obtener todas las ventas de esta caja
    ventas = caja.ventas.filter(
        estado_venta__in=[1, 2]
    ).select_related('cliente', 'usuario').order_by('-fecha')
    
    context = {
        'caja': caja,
        'ventas': ventas,
    }
    
    return render(request, 'ventas/detalle_caja.html', context)


# ======================================================
#  RECALCULAR CAJA
# ======================================================

@login_required
def recalcular_caja(request, caja_id):
    """Recalcula los totales de una caja"""
    if request.method == 'POST':
        try:
            caja = get_object_or_404(Caja, id=caja_id)
            
            # Verificar permisos
            if caja.usuario != request.user and not request.user.is_staff:
                messages.error(request, 'No tienes permiso para recalcular esta caja.')
                return redirect('historial_cajas')
            
            caja.calcular_totales()
            messages.success(request, 'Totales recalculados correctamente.')
            
        except Exception as e:
            messages.error(request, f'Error al recalcular: {str(e)}')
    
    return redirect('detalle_caja', caja_id=caja_id)


# ======================================================
#  API: VERIFICAR CAJA ABIERTA
# ======================================================

@login_required
def api_verificar_caja(request):
    """API para verificar si el usuario tiene caja abierta"""
    tiene_caja = Caja.tiene_caja_abierta(request.user)
    
    if tiene_caja:
        caja = Caja.obtener_caja_abierta(request.user)
        return JsonResponse({
            'tiene_caja': True,
            'caja_id': caja.id,
            'monto_inicial': float(caja.monto_inicial),
            'fecha_apertura': caja.fecha_apertura.strftime('%d/%m/%Y %H:%M')
        })
    else:
        return JsonResponse({'tiene_caja': False})