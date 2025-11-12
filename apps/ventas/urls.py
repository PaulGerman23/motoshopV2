from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_ventas, name='lista_ventas'),
    path('crear/', views.crear_venta, name='crear_venta'),
    path('detalle/<int:pk>/', views.detalle_venta, name='detalle_venta'),
]