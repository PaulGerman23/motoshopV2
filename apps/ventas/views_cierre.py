# apps/ventas/views_cierre.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import CierreCaja, Venta


@login_required
def lista_cierres(request):
    """Lista todos los cierres de caja"""
    cierres = CierreCaja.objects.select_related('usuario').order_by('-fecha')[:30]
    
    # Verificar si hay caja abierta hoy
    hoy = timezone.now().date()
    cierre_hoy = CierreCaja.objects.filter(fecha=hoy, usuario=request.user).first()
    
    context = {
        'cierres': cierres,
        'tiene_cierre_hoy': cierre_hoy is not None
    }
    
    return render(request, 'ventas/lista_cierres.html', context)


@login_required
def crear_cierre(request):
    """Crea un nuevo cierre de caja"""
    hoy = timezone.now().date()
    
    # Verificar si ya existe un cierre para hoy
    if CierreCaja.objects.filter(fecha=hoy, usuario=request.user).exists():
        messages.warning(request, 'Ya existe un cierre de caja para el día de hoy')
        return redirect('lista_cierres')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                monto_inicial = Decimal(request.POST.get('monto_inicial', '0'))
                monto_final_real = Decimal(request.POST.get('monto_final_real', '0'))
                egresos = Decimal(request.POST.get('egresos', '0'))
                detalle_egresos = request.POST.get('detalle_egresos', '')
                observaciones = request.POST.get('observaciones', '')
                
                # Crear cierre
                cierre = CierreCaja.objects.create(
                    fecha=hoy,
                    usuario=request.user,
                    monto_inicial=monto_inicial,
                    monto_final_real=monto_final_real,
                    egresos=egresos,
                    detalle_egresos=detalle_egresos,
                    observaciones=observaciones
                )
                
                # Calcular totales automáticamente
                cierre.calcular_totales()
                
                messages.success(request, 'Cierre de caja creado exitosamente')
                return redirect('detalle_cierre', cierre_id=cierre.id)
                
        except Exception as e:
            messages.error(request, f'Error al crear el cierre: {str(e)}')
    
    # Calcular datos previos para mostrar en el formulario
    ventas_hoy = Venta.objects.filter(
        fecha__date=hoy,
        estado_venta=2
    )
    
    context = {
        'fecha': hoy,
        'total_ventas_previo': ventas_hoy.aggregate(Sum('total'))['total__sum'] or 0,
        'cantidad_ventas_previo': ventas_hoy.count(),
        'efectivo_ventas_previo': ventas_hoy.filter(tipo_pago='efectivo').aggregate(Sum('total'))['total__sum'] or 0,
    }
    
    return render(request, 'ventas/crear_cierre.html', context)


@login_required
def detalle_cierre(request, cierre_id):
    """Muestra el detalle de un cierre de caja"""
    cierre = get_object_or_404(CierreCaja, id=cierre_id)
    
    # Obtener ventas del día
    ventas = Venta.objects.filter(
        fecha__date=cierre.fecha,
        estado_venta=2
    ).select_related('cliente', 'usuario').order_by('-fecha')
    
    context = {
        'cierre': cierre,
        'ventas': ventas
    }
    
    return render(request, 'ventas/detalle_cierre.html', context)


@login_required
def caja_actual(request):
    """Muestra el estado actual de la caja del día"""
    hoy = timezone.now().date()
    
    # Buscar cierre del día
    cierre = CierreCaja.objects.filter(fecha=hoy, usuario=request.user).first()
    
    # Calcular ventas del día
    ventas_hoy = Venta.objects.filter(
        fecha__date=hoy,
        estado_venta=2
    )
    
    total_ventas = ventas_hoy.aggregate(Sum('total'))['total__sum'] or Decimal('0')
    cantidad_ventas = ventas_hoy.count()
    
    # Desglose por método de pago
    efectivo = ventas_hoy.filter(tipo_pago='efectivo').aggregate(Sum('total'))['total__sum'] or Decimal('0')
    debito = ventas_hoy.filter(tipo_pago='debito').aggregate(Sum('total'))['total__sum'] or Decimal('0')
    credito = ventas_hoy.filter(tipo_pago='credito').aggregate(Sum('total'))['total__sum'] or Decimal('0')
    transferencia = ventas_hoy.filter(tipo_pago='transferencia').aggregate(Sum('total'))['total__sum'] or Decimal('0')
    
    # Ventas por hora (últimas 12 horas)
    ahora = timezone.now()
    hace_12_horas = ahora - timedelta(hours=12)
    
    ventas_recientes = Venta.objects.filter(
        fecha__gte=hace_12_horas,
        fecha__lte=ahora,
        estado_venta=2
    ).order_by('-fecha')[:10]
    
    context = {
        'cierre': cierre,
        'total_ventas': total_ventas,
        'cantidad_ventas': cantidad_ventas,
        'efectivo': efectivo,
        'debito': debito,
        'credito': credito,
        'transferencia': transferencia,
        'ventas_recientes': ventas_recientes,
        'tiene_cierre': cierre is not None
    }
    
    return render(request, 'ventas/caja_actual.html', context)


@login_required
def recalcular_cierre(request, cierre_id):
    """Recalcula los totales de un cierre"""
    if request.method == 'POST':
        try:
            cierre = get_object_or_404(CierreCaja, id=cierre_id, usuario=request.user)
            cierre.calcular_totales()
            messages.success(request, 'Totales recalculados correctamente')
        except Exception as e:
            messages.error(request, f'Error al recalcular: {str(e)}')
    
    return redirect('detalle_cierre', cierre_id=cierre_id)