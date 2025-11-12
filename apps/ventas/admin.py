from django.contrib import admin
from .models import Venta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['codigo_venta', 'fecha', 'cliente', 'usuario', 'total', 'tipo_pago', 'estado_venta']
    list_filter = ['fecha', 'tipo_pago', 'estado_venta']
    search_fields = ['codigo_venta']
    inlines = [DetalleVentaInline]