from django.db import models
from django.contrib.auth.models import User
from .models import Venta, DetalleVenta
from apps.inventario.models import Producto
from decimal import Decimal

class Devolucion(models.Model):
    MOTIVOS = [
        ('defecto', 'Producto Defectuoso'),
        ('error', 'Error en la Venta'),
        ('cliente', 'Solicitud del Cliente'),
        ('otro', 'Otro Motivo'),
    ]
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('procesada', 'Procesada'),
    ]
    
    venta_original = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='devoluciones')
    codigo_devolucion = models.CharField(max_length=20, unique=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    
    motivo = models.CharField(max_length=20, choices=MOTIVOS)
    descripcion_motivo = models.TextField()
    
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    
    usuario_solicita = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='devoluciones_solicitadas')
    usuario_aprueba = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='devoluciones_aprobadas')
    
    class Meta:
        db_table = 'devoluciones'
        verbose_name = 'Devolución'
        verbose_name_plural = 'Devoluciones'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Devolución {self.codigo_devolucion} - Venta #{self.venta_original.codigo_venta}"
    
    def procesar_devolucion(self):
        """Procesa la devolución: restaura stock y genera nota de crédito"""
        if self.estado != 'aprobada':
            raise ValueError("Solo se pueden procesar devoluciones aprobadas")
        
        # Restaurar stock de productos devueltos
        for detalle in self.detalles.all():
            if detalle.producto:
                detalle.producto.stock += detalle.cantidad
                detalle.producto.save()
        
        # Generar nota de crédito
        NotaCredito.objects.create(
            devolucion=self,
            venta_original=self.venta_original,
            monto=self.monto_total,
            estado='emitida'
        )
        
        self.estado = 'procesada'
        self.fecha_procesamiento = timezone.now()
        self.save()


class DetalleDevolucion(models.Model):
    devolucion = models.ForeignKey(Devolucion, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'detalle_devoluciones'
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class NotaCredito(models.Model):
    ESTADOS = [
        ('emitida', 'Emitida'),
        ('aplicada', 'Aplicada'),
        ('vencida', 'Vencida'),
    ]
    
    codigo_nota = models.CharField(max_length=20, unique=True)
    devolucion = models.OneToOneField(Devolucion, on_delete=models.CASCADE, related_name='nota_credito')
    venta_original = models.ForeignKey(Venta, on_delete=models.CASCADE)
    
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_disponible = models.DecimalField(max_digits=10, decimal_places=2)
    
    fecha_emision = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    fecha_aplicacion = models.DateTimeField(null=True, blank=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='emitida')
    
    class Meta:
        db_table = 'notas_credito'
        verbose_name = 'Nota de Crédito'
        verbose_name_plural = 'Notas de Crédito'
    
    def __str__(self):
        return f"NC-{self.codigo_nota} - ${self.monto}"
    
    def aplicar_a_venta(self, venta, monto_aplicado):
        """Aplica la nota de crédito a una nueva venta"""
        if self.estado != 'emitida':
            raise ValueError("Esta nota de crédito no está disponible")
        
        if monto_aplicado > self.saldo_disponible:
            raise ValueError("Monto excede el saldo disponible")
        
        self.saldo_disponible -= monto_aplicado
        
        if self.saldo_disponible == 0:
            self.estado = 'aplicada'
            self.fecha_aplicacion = timezone.now()
        
        self.save()