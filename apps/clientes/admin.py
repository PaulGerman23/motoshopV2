from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['codigo_cliente', 'nombre', 'apellido', 'dni', 'telefono', 'condicion_iva', 'estado']
    search_fields = ['nombre', 'apellido', 'dni', 'cuit']