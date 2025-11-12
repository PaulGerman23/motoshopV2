"""
URL Configuration for motoshop_django project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard')),
    path('dashboard/', login_required(TemplateView.as_view(template_name='dashboard.html')), name='dashboard'),
    path('inventario/', include('apps.inventario.urls')),
    path('ventas/', include('apps.ventas.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('proveedores/', include('apps.proveedores.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('reportes/', include('apps.reportes.urls')),
]