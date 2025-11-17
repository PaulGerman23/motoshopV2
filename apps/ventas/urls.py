# apps/ventas/urls.py - REEMPLAZAR COMPLETAMENTE

from django.urls import path
from . import views, views_tickets, views_cierre, views_exportacion

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
    
    # Exportaciones
    path('exportar/venta/<int:venta_id>/pdf/', views_exportacion.exportar_venta_pdf, name='exportar_venta_pdf'),
    path('exportar/ventas/excel/', views_exportacion.exportar_ventas_excel, name='exportar_ventas_excel'),
    path('exportar/cierre/<int:cierre_id>/pdf/', views_exportacion.exportar_cierre_pdf, name='exportar_cierre_pdf'),
]