# apps/ventas/urls.py - REEMPLAZAR COMPLETAMENTE

from django.urls import path
from . import views, views_tickets, views_cierre, views_exportacion, views_devolucion

urlpatterns = [
    # Ventas normales
    path('', views.lista_ventas, name='lista_ventas'),
    path('crear/', views.crear_venta, name='crear_venta'),
    path('detalle/<int:pk>/', views.detalle_venta, name='detalle_venta'),
    path('anular/<int:pk>/', views.anular_venta, name='anular_venta'),
    
    # Tickets (ventas en espera)
    path('tickets/guardar/', views_tickets.guardar_ticket, name='guardar_ticket'),
    path('tickets/lista/', views_tickets.lista_tickets, name='lista_tickets'),
    path('tickets/<int:ticket_id>/recuperar/', views_tickets.recuperar_ticket, name='recuperar_ticket'),
    path('tickets/<int:ticket_id>/finalizar/', views_tickets.finalizar_ticket, name='finalizar_ticket'),
    path('tickets/<int:ticket_id>/cancelar/', views_tickets.cancelar_ticket, name='cancelar_ticket'),
    
    # Cierre de caja
    path('cierres/', views_cierre.lista_cierres, name='lista_cierres'),
    path('cierres/crear/', views_cierre.crear_cierre, name='crear_cierre'),
    path('cierres/<int:cierre_id>/', views_cierre.detalle_cierre, name='detalle_cierre'),
    path('cierres/<int:cierre_id>/recalcular/', views_cierre.recalcular_cierre, name='recalcular_cierre'),
    path('caja-actual/', views_cierre.caja_actual, name='caja_actual'),
    
    # Devoluciones
    path('devoluciones/', views_devolucion.lista_devoluciones, name='lista_devoluciones'),
    path('devoluciones/crear/<int:venta_id>/', views_devolucion.crear_devolucion, name='crear_devolucion'),
    path('devoluciones/<int:devolucion_id>/', views_devolucion.detalle_devolucion, name='detalle_devolucion'),
    path('devoluciones/<int:devolucion_id>/aprobar/', views_devolucion.aprobar_devolucion, name='aprobar_devolucion'),
    path('devoluciones/<int:devolucion_id>/rechazar/', views_devolucion.rechazar_devolucion, name='rechazar_devolucion'),
    path('devoluciones/<int:devolucion_id>/procesar/', views_devolucion.procesar_devolucion, name='procesar_devolucion'),
    
    # Notas de Crédito
    path('notas-credito/', views_devolucion.lista_notas_credito, name='lista_notas_credito'),
    path('notas-credito/<int:nota_id>/', views_devolucion.detalle_nota_credito, name='detalle_nota_credito'),
    path('notas-credito/<int:nota_id>/aplicar/', views_devolucion.aplicar_nota_credito, name='aplicar_nota_credito'),
    
    # Auditoría
    path('auditoria/', views_devolucion.auditoria_movimientos, name='auditoria_movimientos'),
    
    # Cierre de caja
    path('cierres/', views_cierre.lista_cierres, name='lista_cierres'),
    path('cierres/crear/', views_cierre.crear_cierre, name='crear_cierre'),
    path('cierres/<int:cierre_id>/', views_cierre.detalle_cierre, name='detalle_cierre'),
    path('cierres/<int:cierre_id>/recalcular/', views_cierre.recalcular_cierre, name='recalcular_cierre'),
    path('cierres/sin-actividad/', views_cierre.registrar_cierre_sin_actividad, name='cierre_sin_actividad'),  # ← NUEVA LÍNEA
    path('caja-actual/', views_cierre.caja_actual, name='caja_actual'),
    
    # Exportaciones
    path('exportar/venta/<int:venta_id>/pdf/', views_exportacion.exportar_venta_pdf, name='exportar_venta_pdf'),
    path('exportar/ventas/excel/', views_exportacion.exportar_ventas_excel, name='exportar_ventas_excel'),
    path('exportar/cierre/<int:cierre_id>/pdf/', views_exportacion.exportar_cierre_pdf, name='exportar_cierre_pdf'),
]