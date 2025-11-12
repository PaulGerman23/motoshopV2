from django.db import models
from django.contrib.auth.models import User
from apps.clientes.models import Cliente
from apps.inventario.models import Producto

class Venta(models.Model):
    TIPO_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('mercadopago', 'Mercado Pago'),
    ]

    ESTADO_VENTA = [
        (0, 'Anulado'),
        (1, 'Pendiente'),
        (2, 'Pagado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_pago = models.CharField(max_length=50, choices=TIPO_PAGO)
    observacion = models.TextField(blank=True, null=True)
    codigo_venta = models.IntegerField(unique=True)
    estado = models.IntegerField(default=1)
    estado_venta = models.IntegerField(default=1, choices=ESTADO_VENTA)

    class Meta:
        db_table = 'ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Venta #{self.codigo_venta} - {self.fecha.strftime('%d/%m/%Y')}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(default=1)

    class Meta:
        db_table = 'detalle_ventas'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Ventas'

    def __str__(self):
        return f"{self.producto} - {self.cantidad} unidades"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)