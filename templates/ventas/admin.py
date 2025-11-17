from django.contrib import admin
from .models import (
    Venta, DetalleVenta, Ticket, DetalleTicket, 
    CierreCaja, Devolucion, DetalleDevolucion, 
    NotaCredito, AuditoriaMovimiento
)

@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    list_display = ['codigo_devolucion', 'venta_original', 'estado', 'monto_total', 'fecha_solicitud']
    list_filter = ['estado', 'motivo']
    search_fields = ['codigo_devolucion']
    readonly_fields = ['codigo_devolucion', 'fecha_solicitud', 'fecha_procesamiento']

@admin.register(NotaCredito)
class NotaCreditoAdmin(admin.ModelAdmin):
    list_display = ['codigo_nota', 'monto', 'saldo_disponible', 'estado', 'fecha_emision']
    list_filter = ['estado']
    search_fields = ['codigo_nota']
    readonly_fields = ['codigo_nota', 'fecha_emision']

@admin.register(AuditoriaMovimiento)
class AuditoriaMovimientoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'accion', 'fecha', 'descripcion']
    list_filter = ['accion', 'fecha']
    search_fields = ['descripcion']
    readonly_fields = ['usuario', 'accion', 'fecha', 'ip_address']