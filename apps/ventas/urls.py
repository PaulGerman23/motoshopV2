# apps/ventas/urls.py - VERSIÓN SIMPLIFICADA
from django.urls import path
from . import views, views_cierre

urlpatterns = [
    # Ventas normales
    path('', views.lista_ventas, name='lista_ventas'),
    path('crear/', views.crear_venta, name='crear_venta'),
    path('detalle/<int:pk>/', views.detalle_venta, name='detalle_venta'),
    path('anular/<int:pk>/', views.anular_venta, name='anular_venta'),
    
    # Cierre de caja
    path('cierres/', views_cierre.lista_cierres, name='lista_cierres'),
    path('cierres/crear/', views_cierre.crear_cierre, name='crear_cierre'),
    path('cierres/<int:cierre_id>/', views_cierre.detalle_cierre, name='detalle_cierre'),
    path('cierres/<int:cierre_id>/recalcular/', views_cierre.recalcular_cierre, name='recalcular_cierre'),
    path('cierres/sin-actividad/', views_cierre.registrar_cierre_sin_actividad, name='cierre_sin_actividad'),
    path('caja-actual/', views_cierre.caja_actual, name='caja_actual'),
]