from django.contrib import admin
from .models import Categoria, Proveedor, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estado']
    search_fields = ['nombre']

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['razon_social', 'codigo_proveedor', 'cuit', 'condicion_iva', 'estado']
    search_fields = ['razon_social', 'cuit']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descripcion', 'precio_costo', 'precio_venta', 'stock', 'categoria', 'estado']
    search_fields = ['codigo', 'descripcion']
    list_filter = ['categoria', 'estado']