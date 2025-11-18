# apps/ventas/views_cierre.py - VERSIÓN FINAL CORREGIDA

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import CierreCaja, Venta


# ======================================================
#  LISTA DE CIERRES
# ======================================================
@login_required
def lista_cierres(request):
    cierres = CierreCaja.objects.select_related('usuario').order_by('-fecha', '-turno')[:30]

    hoy = timezone.localtime().date()  # ← CORREGIDO
    turno_actual = CierreCaja.determinar_turno_actual()
    cierre_hoy = CierreCaja.objects.filter(fecha=hoy, turno=turno_actual).first()

    context = {
        'cierres': cierres,
        'tiene_cierre_hoy': cierre_hoy is not None
    }

    return render(request, 'ventas/lista_cierres.html', context)


# ======================================================
#  CREAR CIERRE
# ======================================================
@login_required
def crear_cierre(request):
    hoy = timezone.localtime().date()  # ← CORREGIDO
    turno_actual = CierreCaja.determinar_turno_actual()

    # Verificar cierre previo
    if CierreCaja.objects.filter(fecha=hoy, turno=turno_actual).exists():
        messages.warning(request, f'Ya existe un cierre de caja para el turno {dict(CierreCaja.TURNOS)[turno_actual]} de hoy')
        return redirect('lista_cierres')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                monto_inicial = Decimal(request.POST.get('monto_inicial', '0'))
                monto_final_real = Decimal(request.POST.get('monto_final_real', '0'))
                egresos = Decimal(request.POST.get('egresos', '0'))
                detalle_egresos = request.POST.get('detalle_egresos', '')
                observaciones = request.POST.get('observaciones', '')

                cierre = CierreCaja.objects.create(
                    fecha=hoy,
                    turno=turno_actual,
                    usuario=request.user,
                    monto_inicial=monto_inicial,
                    monto_final_real=monto_final_real,
                    egresos=egresos,
                    detalle_egresos=detalle_egresos,
                    observaciones=observaciones
                )

                cierre.calcular_totales()
                messages.success(request, f'Cierre de caja del turno {cierre.get_turno_display()} creado exitosamente')
                return redirect('detalle_cierre', cierre_id=cierre.id)

        except Exception as e:
            messages.error(request, f'Error al crear el cierre: {str(e)}')

    # GET — obtener datos previos
    hora_inicio, hora_fin = CierreCaja.obtener_rango_horario_turno(turno_actual)
    datetime_inicio, datetime_fin = _obtener_rango_datetime_turno(hoy, turno_actual, hora_inicio, hora_fin)

    ventas_turno = Venta.objects.filter(
        fecha__gte=datetime_inicio,
        fecha__lt=datetime_fin,
        estado_venta=2
    )

    context = {
        'fecha': hoy,
        'turno_actual': turno_actual,
        'turno_nombre': dict(CierreCaja.TURNOS)[turno_actual],
        'total_ventas_previo': ventas_turno.aggregate(Sum('total'))['total__sum'] or 0,
        'cantidad_ventas_previo': ventas_turno.count(),
        'efectivo_ventas_previo': ventas_turno.filter(tipo_pago='efectivo').aggregate(Sum('total'))['total__sum'] or 0,
    }

    return render(request, 'ventas/crear_cierre.html', context)


# ======================================================
#  DETALLE DE CIERRE
# ======================================================
@login_required
def detalle_cierre(request, cierre_id):
    cierre = get_object_or_404(CierreCaja, id=cierre_id)

    hora_inicio, hora_fin = CierreCaja.obtener_rango_horario_turno(cierre.turno)
    datetime_inicio, datetime_fin = _obtener_rango_datetime_turno(cierre.fecha, cierre.turno, hora_inicio, hora_fin)

    ventas = Venta.objects.filter(
        fecha__gte=datetime_inicio,
        fecha__lt=datetime_fin,
        estado_venta=2
    ).select_related('cliente', 'usuario').order_by('-fecha')

    return render(request, 'ventas/detalle_cierre.html', {'cierre': cierre, 'ventas': ventas})


# ======================================================
#  CAJA ACTUAL
# ======================================================
@login_required
def caja_actual(request):
    hoy = timezone.localtime().date()  # ← CORREGIDO
    turno_actual = CierreCaja.determinar_turno_actual()

    cierre = CierreCaja.objects.filter(fecha=hoy, turno=turno_actual).first()

    hora_inicio, hora_fin = CierreCaja.obtener_rango_horario_turno(turno_actual)
    datetime_inicio, datetime_fin = _obtener_rango_datetime_turno(hoy, turno_actual, hora_inicio, hora_fin)

    ventas_turno = Venta.objects.filter(
        fecha__gte=datetime_inicio,
        fecha__lt=datetime_fin,
        estado_venta=2
    )

    total_ventas = ventas_turno.aggregate(Sum('total'))['total__sum'] or Decimal('0')
    cantidad_ventas = ventas_turno.count()

    efectivo = ventas_turno.filter(tipo_pago='efectivo').aggregate(Sum('total'))['total__sum'] or Decimal('0')
    debito = ventas_turno.filter(tipo_pago='debito').aggregate(Sum('total'))['total__sum'] or Decimal('0')
    credito = ventas_turno.filter(tipo_pago='credito').aggregate(Sum('total'))['total__sum'] or Decimal('0')
    transferencia = ventas_turno.filter(tipo_pago='transferencia').aggregate(Sum('total'))['total__sum'] or Decimal('0')

    # pagos mixtos
    pagos_mixtos = ventas_turno.filter(tipo_pago='mixto')
    for pago in pagos_mixtos:
        efectivo += pago.monto_efectivo
        debito += pago.monto_tarjeta

    ventas_recientes = ventas_turno.select_related('cliente', 'usuario').order_by('-fecha')[:10]

    turnos_info = {
        'manana': 'Mañana (06:00 - 14:00)',
        'tarde': 'Tarde (14:00 - 22:00)',
        'noche': 'Noche (22:00 - 06:00)'
    }

    context = {
        'fecha': hoy,
        'turno_actual': turno_actual,
        'turno_nombre': turnos_info[turno_actual],
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


# ======================================================
#  RE-CALCULAR CIERRE
# ======================================================
@login_required
def recalcular_cierre(request, cierre_id):
    if request.method == 'POST':
        try:
            cierre = get_object_or_404(CierreCaja, id=cierre_id)

            if cierre.usuario != request.user and not request.user.is_staff:
                messages.error(request, 'No tienes permisos para recalcular este cierre')
                return redirect('detalle_cierre', cierre_id=cierre_id)

            cierre.calcular_totales()
            messages.success(request, 'Totales recalculados correctamente')

        except Exception as e:
            messages.error(request, f'Error al recalcular: {str(e)}')

    return redirect('detalle_cierre', cierre_id=cierre_id)


# ======================================================
#  FUNCIÓN AUXILIAR — DEFINITIVA
# ======================================================
def _obtener_rango_datetime_turno(fecha, turno, hora_inicio, hora_fin):
    """
    Devuelve datetime aware usando zoneinfo (compatible con Python 3.9+)
    """
    from django.utils import timezone
    zona = timezone.get_current_timezone()

    # Crear datetime naive
    if turno == 'noche':
        datetime_inicio = datetime.combine(fecha, hora_inicio)
        datetime_fin = datetime.combine(fecha + timedelta(days=1), hora_fin)
    else:
        datetime_inicio = datetime.combine(fecha, hora_inicio)
        datetime_fin = datetime.combine(fecha, hora_fin)

    # Convertir a aware usando zoneinfo (NO localize!)
    datetime_inicio = datetime_inicio.replace(tzinfo=zona)
    datetime_fin = datetime_fin.replace(tzinfo=zona)

    return datetime_inicio, datetime_fin
