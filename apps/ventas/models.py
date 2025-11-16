from django.db import models
from django.contrib.auth.models import User
from apps.clientes.models import Cliente
from apps.inventario.models import Producto
from decimal import Decimal

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

        
class Ticket(models.Model):
    """
    Modelo para ventas en espera / tickets pendientes
    Permite guardar carritos temporalmente y recuperarlos después
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('debito', 'Tarjeta de Débito'),
        ('credito', 'Tarjeta de Crédito'),
        ('transferencia', 'Transferencia'),
        ('mixto', 'Pago Mixto'),
    ]
    
    # Identificación
    ticket_id = models.CharField(max_length=20, unique=True, db_index=True)
    codigo_ticket = models.IntegerField(unique=True)
    
    # Relaciones
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tickets')
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Descuento
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Descuento en %')
    descuento_monto = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Descuento en $')
    
    # Pago
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES, blank=True)
    monto_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Para pagos mixtos')
    monto_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Para pagos mixtos')
    
    # Estado y control
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', db_index=True)
    observacion = models.TextField(blank=True, null=True)
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    
    # Venta asociada (cuando se finaliza)
    venta = models.OneToOneField(Venta, on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_original')
    
    class Meta:
        db_table = 'tickets'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado', 'usuario']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return f"Ticket #{self.codigo_ticket} - {self.get_estado_display()}"
    
    def calcular_totales(self):
        """Calcula subtotal, descuento y total del ticket"""
        detalles = self.detalles.filter(activo=True)
        self.subtotal = sum(d.subtotal for d in detalles)
        
        # Aplicar descuento
        if self.descuento_porcentaje > 0:
            self.descuento = self.subtotal * (self.descuento_porcentaje / 100)
        else:
            self.descuento = self.descuento_monto
        
        self.total = self.subtotal - self.descuento
        self.save()
    
    def finalizar(self):
        """Convierte el ticket en una venta definitiva"""
        from django.utils import timezone
        
        if self.estado != 'pendiente':
            raise ValueError("Solo se pueden finalizar tickets pendientes")
        
        if not self.tipo_pago:
            raise ValueError("Debe especificar un método de pago")
        
        # Crear venta
        ultimo_codigo = Venta.objects.order_by('-codigo_venta').first()
        nuevo_codigo = (ultimo_codigo.codigo_venta + 1) if ultimo_codigo else 1000
        
        venta = Venta.objects.create(
            cliente=self.cliente,
            usuario=self.usuario,
            total=self.total,
            tipo_pago=self.tipo_pago,
            observacion=self.observacion,
            codigo_venta=nuevo_codigo,
            estado_venta=2  # Pagado
        )
        
        # Crear detalles de venta y descontar stock
        for detalle in self.detalles.filter(activo=True):
            DetalleVenta.objects.create(
                venta=venta,
                producto=detalle.producto,
                cantidad=detalle.cantidad,
                precio_unitario=detalle.precio_unitario,
                subtotal=detalle.subtotal
            )
            
            # Descontar stock
            producto = detalle.producto
            if producto.stock < detalle.cantidad:
                raise ValueError(f"Stock insuficiente para {producto.descripcion}")
            producto.stock -= detalle.cantidad
            producto.save()
        
        # Actualizar ticket
        self.estado = 'finalizado'
        self.venta = venta
        self.fecha_finalizacion = timezone.now()
        self.save()
        
        return venta
    
    def cancelar(self):
        """Cancela el ticket (no restaura stock)"""
        if self.estado == 'finalizado':
            raise ValueError("No se puede cancelar un ticket finalizado")
        
        self.estado = 'cancelado'
        self.save()


class DetalleTicket(models.Model):
    """Detalles de productos en el ticket"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    
    # Datos del producto al momento del ticket
    descripcion = models.CharField(max_length=500, help_text='Copia de la descripción')
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    activo = models.BooleanField(default=True, help_text='Para eliminación lógica')
    
    class Meta:
        db_table = 'detalle_tickets'
        verbose_name = 'Detalle de Ticket'
        verbose_name_plural = 'Detalles de Tickets'
    
    def __str__(self):
        return f"{self.descripcion} x {self.cantidad}"
    
    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class CierreCaja(models.Model):
    """Modelo para cierre diario de caja"""
    fecha = models.DateField(db_index=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Montos iniciales
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Ventas del día
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_ventas = models.IntegerField(default=0)
    
    # Desglose por método de pago
    efectivo_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    debito_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credito_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transferencia_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Egresos
    egresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    detalle_egresos = models.TextField(blank=True)
    
    # Totales finales
    monto_final_esperado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_final_real = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Control
    observaciones = models.TextField(blank=True)
    fecha_cierre = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cierres_caja'
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'
        ordering = ['-fecha']
        unique_together = ('fecha', 'usuario')
    
    def __str__(self):
        return f"Cierre {self.fecha} - {self.usuario}"
    
    def calcular_totales(self):
        """Calcula los totales del cierre"""
        from django.db.models import Sum, Count
        
        # Obtener ventas del día
        ventas_dia = Venta.objects.filter(
            fecha__date=self.fecha,
            estado_venta=2  # Solo pagadas
        )
        
        self.total_ventas = ventas_dia.aggregate(Sum('total'))['total__sum'] or 0
        self.cantidad_ventas = ventas_dia.count()
        
        # Desglose por método de pago
        self.efectivo_ventas = ventas_dia.filter(tipo_pago='efectivo').aggregate(Sum('total'))['total__sum'] or 0
        self.debito_ventas = ventas_dia.filter(tipo_pago='debito').aggregate(Sum('total'))['total__sum'] or 0
        self.credito_ventas = ventas_dia.filter(tipo_pago='credito').aggregate(Sum('total'))['total__sum'] or 0
        self.transferencia_ventas = ventas_dia.filter(tipo_pago='transferencia').aggregate(Sum('total'))['total__sum'] or 0
        
        # Calcular monto final esperado
        self.monto_final_esperado = self.monto_inicial + self.efectivo_ventas - self.egresos
        
        # Calcular diferencia
        self.diferencia = self.monto_final_real - self.monto_final_esperado
        
        self.save()