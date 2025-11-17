# apps/reportes/urls.py - ACTUALIZADO

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='reportes'),
    path('ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('stock/', views.reporte_stock, name='reporte_stock'),
    path('clientes/', views.reporte_clientes, name='reporte_clientes'),
]

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from apps.ventas.models import Venta, DetalleVenta
from apps.inventario.models import Producto
from apps.clientes.models import Cliente


@login_required
def index(request):
    """Vista principal de reportes con acceso a todos los reportes"""
    return render(request, 'reportes/index.html')


@login_required
def reporte_ventas(request):
    """Reporte de ventas por período con filtros"""
    # Obtener parámetros de filtro
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    tipo_pago = request.GET.get('tipo_pago', '')
    
    # Fechas por defecto: último mes
    if not fecha_desde:
        fecha_desde = (timezone.now() - timedelta(days=30)).date()
    else:
        fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    
    if not fecha_hasta:
        fecha_hasta = timezone.now().date()
    else:
        fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    
    # Filtrar ventas
    ventas = Venta.objects.filter(
        fecha__date__gte=fecha_desde,
        fecha__date__lte=fecha_hasta,
        estado_venta__in=[1, 2]  # Pendiente y Pagado
    ).select_related('cliente', 'usuario')
    
    if tipo_pago:
        ventas = ventas.filter(tipo_pago=tipo_pago)
    
    # Calcular estadísticas
    total_ventas = ventas.aggregate(Sum('total'))['total__sum'] or Decimal('0')
    cantidad_ventas = ventas.count()
    promedio_venta = ventas.aggregate(Avg('total'))['total__avg'] or Decimal('0')
    
    # Ventas por método de pago
    ventas_por_metodo = {
        'efectivo': ventas.filter(tipo_pago='efectivo').aggregate(
            total=Sum('total'), cantidad=Count('id')
        ),
        'debito': ventas.filter(tipo_pago='debito').aggregate(
            total=Sum('total'), cantidad=Count('id')
        ),
        'credito': ventas.filter(tipo_pago='credito').aggregate(
            total=Sum('total'), cantidad=Count('id')
        ),
        'transferencia': ventas.filter(tipo_pago='transferencia').aggregate(
            total=Sum('total'), cantidad=Count('id')
        ),
        'mixto': ventas.filter(tipo_pago='mixto').aggregate(
            total=Sum('total'), cantidad=Count('id')
        ),
    }
    
    # Ventas por día (para gráfico)
    ventas_por_dia = ventas.extra(
        select={'dia': 'date(fecha)'}
    ).values('dia').annotate(
        total=Sum('total'),
        cantidad=Count('id')
    ).order_by('dia')
    
    # Top 10 productos más vendidos en el período
    productos_mas_vendidos = DetalleVenta.objects.filter(
        venta__fecha__date__gte=fecha_desde,
        venta__fecha__date__lte=fecha_hasta,
        venta__estado_venta__in=[1, 2]
    ).values(
        'producto__descripcion',
        'producto__codigo'
    ).annotate(
        cantidad_vendida=Sum('cantidad'),
        total_vendido=Sum(F('cantidad') * F('precio_unitario'))
    ).order_by('-cantidad_vendida')[:10]
    
    # Top 10 clientes por monto
    clientes_top = ventas.filter(
        cliente__isnull=False
    ).values(
        'cliente__nombre',
        'cliente__apellido'
    ).annotate(
        total_comprado=Sum('total'),
        cantidad_compras=Count('id')
    ).order_by('-total_comprado')[:10]
    
    context = {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'tipo_pago': tipo_pago,
        'total_ventas': total_ventas,
        'cantidad_ventas': cantidad_ventas,
        'promedio_venta': promedio_venta,
        'ventas_por_metodo': ventas_por_metodo,
        'ventas_por_dia': list(ventas_por_dia),
        'productos_mas_vendidos': productos_mas_vendidos,
        'clientes_top': clientes_top,
        'ventas': ventas[:50],  # Últimas 50 ventas
    }
    
    return render(request, 'reportes/reporte_ventas.html', context)


@login_required
def reporte_stock(request):
    """Reporte de inventario y stock"""
    # Obtener filtros
    categoria_id = request.GET.get('categoria')
    nivel_stock = request.GET.get('nivel_stock', '')  # bajo, medio, alto
    
    productos = Producto.objects.filter(estado=1).select_related('categoria', 'proveedor')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    # Filtrar por nivel de stock
    if nivel_stock == 'bajo':
        productos = productos.filter(stock__lte=F('stock_minimo'))
    elif nivel_stock == 'medio':
        productos = productos.filter(
            stock__gt=F('stock_minimo'),
            stock__lte=F('stock_minimo') * 3
        )
    elif nivel_stock == 'alto':
        productos = productos.filter(stock__gt=F('stock_minimo') * 3)
    
    # Estadísticas generales
    total_productos = productos.count()
    productos_stock_bajo = productos.filter(stock__lte=F('stock_minimo')).count()
    productos_sin_stock = productos.filter(stock=0).count()
    
    # Valor total del inventario
    valor_inventario = sum(
        (p.stock * p.precio_costo) for p in productos
    )
    
    valor_venta_potencial = sum(
        (p.stock * p.precio_venta) for p in productos
    )
    
    ganancia_potencial = valor_venta_potencial - valor_inventario
    
    # Productos con alerta de stock
    productos_alertas = productos.filter(
        Q(stock__lte=F('stock_minimo')) | Q(stock=0)
    ).order_by('stock')
    
    # Productos más valiosos (por valor en inventario)
    productos_valiosos = sorted(
        productos,
        key=lambda p: p.stock * p.precio_costo,
        reverse=True
    )[:10]
    
    # Categorías para filtro
    from apps.inventario.models import Categoria
    categorias = Categoria.objects.filter(estado=1)
    
    context = {
        'productos': productos,
        'total_productos': total_productos,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_sin_stock': productos_sin_stock,
        'valor_inventario': valor_inventario,
        'valor_venta_potencial': valor_venta_potencial,
        'ganancia_potencial': ganancia_potencial,
        'productos_alertas': productos_alertas,
        'productos_valiosos': productos_valiosos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id,
        'nivel_stock': nivel_stock,
    }
    
    return render(request, 'reportes/reporte_stock.html', context)


@login_required
def reporte_clientes(request):
    """Reporte de análisis de clientes"""
    clientes = Cliente.objects.filter(estado=1)
    
    # Estadísticas generales
    total_clientes = clientes.count()
    
    # Clientes con compras
    clientes_con_compras = clientes.filter(
        venta__isnull=False
    ).distinct().count()
    
    # Clientes sin compras
    clientes_sin_compras = total_clientes - clientes_con_compras
    
    # Top clientes por monto total
    clientes_top_monto = clientes.annotate(
        total_comprado=Sum('venta__total'),
        cantidad_compras=Count('venta')
    ).filter(
        total_comprado__isnull=False
    ).order_by('-total_comprado')[:10]
    
    # Top clientes por frecuencia
    clientes_top_frecuencia = clientes.annotate(
        cantidad_compras=Count('venta')
    ).filter(
        cantidad_compras__gt=0
    ).order_by('-cantidad_compras')[:10]
    
    # Análisis por condición IVA
    clientes_por_iva = clientes.values('condicion_iva').annotate(
        cantidad=Count('id'),
        total_vendido=Sum('venta__total')
    ).order_by('-cantidad')
    
    # Clientes recientes (últimos 30 días)
    hace_30_dias = timezone.now() - timedelta(days=30)
    # Nota: necesitarías agregar fecha_registro al modelo Cliente
    # clientes_nuevos = clientes.filter(fecha_registro__gte=hace_30_dias).count()
    
    # Valor promedio de compra por cliente
    valor_promedio = Venta.objects.filter(
        cliente__isnull=False,
        estado_venta__in=[1, 2]
    ).aggregate(Avg('total'))['total__avg'] or Decimal('0')
    
    context = {
        'total_clientes': total_clientes,
        'clientes_con_compras': clientes_con_compras,
        'clientes_sin_compras': clientes_sin_compras,
        'clientes_top_monto': clientes_top_monto,
        'clientes_top_frecuencia': clientes_top_frecuencia,
        'clientes_por_iva': clientes_por_iva,
        'valor_promedio': valor_promedio,
    }
    
    return render(request, 'reportes/reporte_clientes.html', context)