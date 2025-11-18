# Crear archivo: diagnosticar_caja.py en la raíz del proyecto
# Ejecutar con: python manage.py shell < diagnosticar_caja.py

from apps.ventas.models import CierreCaja, Venta
from django.utils import timezone
from datetime import datetime, timedelta, time

print("=" * 80)
print("DIAGNÓSTICO DEL SISTEMA DE CIERRE DE CAJA")
print("=" * 80)

# 1. Verificar hora actual y turno
hora_actual = timezone.now()
print(f"\n1. HORA ACTUAL DEL SISTEMA:")
print(f"   Fecha/Hora: {hora_actual}")
print(f"   Hora: {hora_actual.time()}")
print(f"   Fecha: {hora_actual.date()}")

turno_actual = CierreCaja.determinar_turno_actual()
print(f"   Turno detectado: {turno_actual} ({dict(CierreCaja.TURNOS)[turno_actual]})")

# 2. Verificar cierres existentes
print(f"\n2. CIERRES EXISTENTES:")
cierres = CierreCaja.objects.all().order_by('-fecha', '-turno')[:5]
if cierres:
    for cierre in cierres:
        print(f"   - {cierre.fecha} | Turno: {cierre.get_turno_display()} | Usuario: {cierre.usuario}")
else:
    print("   No hay cierres registrados")

# 3. Verificar cierre del día actual
hoy = hora_actual.date()
cierre_hoy = CierreCaja.objects.filter(fecha=hoy, turno=turno_actual).first()
print(f"\n3. CIERRE DEL DÍA ACTUAL ({hoy}):")
if cierre_hoy:
    print(f"   ⚠️ YA EXISTE un cierre para el turno {cierre_hoy.get_turno_display()}")
    print(f"   Creado por: {cierre_hoy.usuario}")
    print(f"   Total ventas: ${cierre_hoy.total_ventas}")
else:
    print(f"   ✓ NO hay cierre para el turno actual ({turno_actual})")

# 4. Verificar ventas del turno actual
hora_inicio, hora_fin = CierreCaja.obtener_rango_horario_turno(turno_actual)
print(f"\n4. RANGO HORARIO DEL TURNO ACTUAL:")
print(f"   Inicio: {hora_inicio}")
print(f"   Fin: {hora_fin}")

if turno_actual == 'noche':
    datetime_inicio = datetime.combine(hoy, hora_inicio)
    datetime_fin = datetime.combine(hoy + timedelta(days=1), hora_fin)
else:
    datetime_inicio = datetime.combine(hoy, hora_inicio)
    datetime_fin = datetime.combine(hoy, hora_fin)

datetime_inicio = timezone.make_aware(datetime_inicio)
datetime_fin = timezone.make_aware(datetime_fin)

print(f"   Rango completo: {datetime_inicio} hasta {datetime_fin}")

# 5. Contar ventas en el rango
ventas_turno = Venta.objects.filter(
    fecha__gte=datetime_inicio,
    fecha__lt=datetime_fin,
    estado_venta=2
)

print(f"\n5. VENTAS EN EL TURNO ACTUAL:")
print(f"   Total ventas: {ventas_turno.count()}")
if ventas_turno.exists():
    total = sum(v.total for v in ventas_turno)
    print(f"   Monto total: ${total}")
    print(f"   Última venta: {ventas_turno.order_by('-fecha').first().fecha}")
    
    # Mostrar últimas 5 ventas
    print(f"\n   Últimas 5 ventas:")
    for venta in ventas_turno.order_by('-fecha')[:5]:
        print(f"   - Venta #{venta.codigo_venta} | {venta.fecha} | ${venta.total} | {venta.get_tipo_pago_display()}")
else:
    print("   ⚠️ NO hay ventas en este turno")

# 6. Verificar TODAS las ventas de hoy
ventas_hoy = Venta.objects.filter(
    fecha__date=hoy,
    estado_venta=2
)

print(f"\n6. TODAS LAS VENTAS DEL DÍA ({hoy}):")
print(f"   Total ventas del día: {ventas_hoy.count()}")
if ventas_hoy.exists():
    print(f"   Monto total del día: ${sum(v.total for v in ventas_hoy)}")
    print(f"\n   Detalle de ventas:")
    for venta in ventas_hoy.order_by('fecha'):
        print(f"   - #{venta.codigo_venta} | {venta.fecha.time()} | ${venta.total} | {venta.get_tipo_pago_display()}")

# 7. Diagnóstico de problemas
print(f"\n" + "=" * 80)
print("DIAGNÓSTICO:")
print("=" * 80)

if not ventas_turno.exists() and ventas_hoy.exists():
    print("❌ PROBLEMA DETECTADO: Hay ventas del día pero NO se detectan en el turno actual")
    print("\nPosibles causas:")
    print("1. Las ventas están fuera del rango horario del turno actual")
    print("2. Problema con la zona horaria (timezone)")
    print("3. El turno se determinó incorrectamente")
    
    print("\n📋 RECOMENDACIONES:")
    print("1. Verifica que la hora del sistema sea correcta")
    print("2. Verifica el timezone en settings.py: TIME_ZONE = 'America/Argentina/Buenos_Aires'")
    print("3. Si es necesario, recalcula los cierres existentes")

elif cierre_hoy:
    print("⚠️ Ya existe un cierre para el turno actual")
    print("   Esto puede estar bloqueando la creación de un nuevo cierre")
    
    print("\n📋 SOLUCIÓN:")
    print("   Si necesitas crear un nuevo cierre, elimina el cierre existente:")
    print(f"   >>> cierre = CierreCaja.objects.get(id={cierre_hoy.id})")
    print(f"   >>> cierre.delete()")

elif ventas_turno.exists():
    print("✓ TODO FUNCIONA CORRECTAMENTE")
    print(f"  Hay {ventas_turno.count()} ventas en el turno actual")

else:
    print("ℹ️ No hay ventas en el turno actual, lo cual es normal si recién comienza el turno")

print("\n" + "=" * 80)