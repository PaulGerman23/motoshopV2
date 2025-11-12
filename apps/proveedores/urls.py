from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_proveedores, name='lista_proveedores'),
    path('crear/', views.crear_proveedor, name='crear_proveedor'),
]