# apps/ventas/models.py - REEMPLAZAR COMPLETAMENTE

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.clientes.models import Cliente
from apps.inventario.models import Producto
from decimal import Decimal
from datetime import timedelta
from datetime import time



class Venta(models.Model):
    TIPO_PAGO = [
        ('efectivo', 'Efectivo'),
        ('debito', 'Tarjeta de Débito'),
        ('credito', 'Tarjeta de Crédito'),
        ('transferencia', 'Transferencia'),
        ('mixto', 'Pago Mixto'),
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
    
    # Pagos mixtos
    es_pago_mixto = models.BooleanField(default=False)
    monto_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0, 
                                          help_text='Monto pagado en efectivo (pago mixto)')
    monto_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         help_text='Monto pagado con tarjeta (pago mixto)')
    
    # Descuentos
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descuento_monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):
        return f"Venta #{self.codigo_venta} - {self.fecha.strftime('%d/%m/%Y')}"
    
    def puede_devolverse(self):
        """Verifica si la venta puede ser devuelta"""
        if self.estado_venta == 0:  # Ya anulada
            return False
        
        # Verificar si tiene devoluciones pendientes o aprobadas
        if self.devoluciones.filter(estado__in=['pendiente', 'aprobada']).exists():
            return False
        
        # Verificar plazo (ej: 30 días)
        dias_desde_venta = (timezone.now() - self.fecha).days
        if dias_desde_venta > 30:
            return False
        
        return True


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
    
    ticket_id = models.CharField(max_length=20, unique=True, db_index=True)
    codigo_ticket = models.IntegerField(unique=True)
    
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tickets')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descuento_monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES, blank=True)
    monto_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', db_index=True)
    observacion = models.TextField(blank=True, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    
    venta = models.OneToOneField(Venta, on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_original')
    
    class Meta:
        db_table = 'tickets'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Ticket #{self.codigo_ticket} - {self.get_estado_display()}"


class DetalleTicket(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    descripcion = models.CharField(max_length=500)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'detalle_tickets'


class CierreCaja(models.Model):
    TURNOS = [
        ('manana', 'Mañana'),
        ('tarde', 'Tarde'),
        ('noche', 'Noche'),
    ]
    
    fecha = models.DateField(db_index=True)
    turno = models.CharField(
        max_length=10, 
        choices=TURNOS, 
        default='manana',
        help_text='Turno del cierre: Mañana (06:00-14:00), Tarde (14:00-22:00), Noche (22:00-06:00)'
    )
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_ventas = models.IntegerField(default=0)
    
    efectivo_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    debito_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credito_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transferencia_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    egresos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    detalle_egresos = models.TextField(blank=True)
    
    monto_final_esperado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_final_real = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    observaciones = models.TextField(blank=True)
    fecha_cierre = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cierres_caja'
        unique_together = ('fecha', 'turno')  # CAMBIO: ahora por fecha y turno
        verbose_name = 'Cierre de Caja'
        verbose_name_plural = 'Cierres de Caja'

    def __str__(self):
        return f"Cierre {self.get_turno_display()} - {self.fecha}"

    @staticmethod
    def determinar_turno_actual():
        """Determina el turno según la hora actual"""
        hora_actual = timezone.now().time()
        
        if time(6, 0) <= hora_actual < time(14, 0):
            return 'manana'
        elif time(14, 0) <= hora_actual < time(22, 0):
            return 'tarde'
        else:  # 22:00 - 06:00
            return 'noche'
    
    @staticmethod
    def obtener_rango_horario_turno(turno):
        """Retorna el rango horario de un turno"""
        rangos = {
            'manana': (time(6, 0), time(14, 0)),
            'tarde': (time(14, 0), time(22, 0)),
            'noche': (time(22, 0), time(6, 0))
        }
        return rangos.get(turno, (time(0, 0), time(23, 59)))

    def calcular_totales(self):
        """Calcula los totales considerando el turno"""
        from django.db.models import Sum
        from datetime import datetime, timedelta
        
        # Obtener rango horario del turno
        hora_inicio, hora_fin = self.obtener_rango_horario_turno(self.turno)
        
        # Crear datetime para el inicio y fin del turno
        if self.turno == 'noche':
            # El turno noche cruza la medianoche
            if hora_inicio > hora_fin:
                # Desde las 22:00 del día hasta las 06:00 del día siguiente
                datetime_inicio = datetime.combine(self.fecha, hora_inicio)
                datetime_fin = datetime.combine(self.fecha + timedelta(days=1), hora_fin)
            else:
                datetime_inicio = datetime.combine(self.fecha, hora_inicio)
                datetime_fin = datetime.combine(self.fecha, hora_fin)
        else:
            datetime_inicio = datetime.combine(self.fecha, hora_inicio)
            datetime_fin = datetime.combine(self.fecha, hora_fin)
        
        # Filtrar ventas por rango horario
        from .models import Venta
        ventas_turno = Venta.objects.filter(
            fecha__gte=datetime_inicio,
            fecha__lt=datetime_fin,
            estado_venta=2
        )
        
        self.total_ventas = ventas_turno.aggregate(Sum('total'))['total__sum'] or 0
        self.cantidad_ventas = ventas_turno.count()
        
        self.efectivo_ventas = ventas_turno.filter(tipo_pago='efectivo').aggregate(Sum('total'))['total__sum'] or 0
        self.debito_ventas = ventas_turno.filter(tipo_pago='debito').aggregate(Sum('total'))['total__sum'] or 0
        self.credito_ventas = ventas_turno.filter(tipo_pago='credito').aggregate(Sum('total'))['total__sum'] or 0
        self.transferencia_ventas = ventas_turno.filter(tipo_pago='transferencia').aggregate(Sum('total'))['total__sum'] or 0
        
        self.monto_final_esperado = self.monto_inicial + self.efectivo_ventas - self.egresos
        self.diferencia = self.monto_final_real - self.monto_final_esperado
        
        self.save()

# ================================================
# MODELOS PARA DEVOLUCIONES Y NOTAS DE CRÉDITO
# ================================================

class Devolucion(models.Model):
    MOTIVOS = [
        ('defecto', 'Producto Defectuoso'),
        ('error', 'Error en la Venta'),
        ('cliente', 'Solicitud del Cliente'),
        ('garantia', 'Garantía'),
        ('otro', 'Otro Motivo'),
    ]
    
    ESTADOS = [
        ('pendiente', 'Pendiente de Aprobación'),
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
    
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente', db_index=True)
    
    usuario_solicita = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                          related_name='devoluciones_solicitadas')
    usuario_aprueba = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                         related_name='devoluciones_aprobadas')
    
    observaciones_aprobacion = models.TextField(blank=True)
    
    class Meta:
        db_table = 'devoluciones'
        verbose_name = 'Devolución'
        verbose_name_plural = 'Devoluciones'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Devolución {self.codigo_devolucion} - Venta #{self.venta_original.codigo_venta}"
    
    def calcular_total(self):
        """Calcula el total de la devolución"""
        self.monto_total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.save()
    
    def puede_procesarse(self):
        """Verifica si la devolución puede ser procesada"""
        return self.estado == 'aprobada'
    
    def procesar(self, usuario):
        """Procesa la devolución: restaura stock y genera nota de crédito"""
        if not self.puede_procesarse():
            raise ValueError("Solo se pueden procesar devoluciones aprobadas")
        
        # Restaurar stock
        for detalle in self.detalles.all():
            if detalle.producto:
                detalle.producto.stock += detalle.cantidad
                detalle.producto.save()
        
        # Generar nota de crédito
        ultimo_codigo = NotaCredito.objects.order_by('-id').first()
        nuevo_codigo = (ultimo_codigo.id + 1) if ultimo_codigo else 1000
        
        nota = NotaCredito.objects.create(
            codigo_nota=f"NC-{nuevo_codigo:06d}",
            devolucion=self,
            venta_original=self.venta_original,
            monto=self.monto_total,
            saldo_disponible=self.monto_total,
            fecha_vencimiento=timezone.now().date() + timedelta(days=90)  # 90 días de validez
        )
        
        self.estado = 'procesada'
        self.fecha_procesamiento = timezone.now()
        self.save()
        
        return nota


class DetalleDevolucion(models.Model):
    devolucion = models.ForeignKey(Devolucion, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    descripcion_producto = models.CharField(max_length=500)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    motivo_especifico = models.TextField(blank=True)
    
    class Meta:
        db_table = 'detalle_devoluciones'
        verbose_name = 'Detalle de Devolución'
        verbose_name_plural = 'Detalles de Devoluciones'
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class NotaCredito(models.Model):
    ESTADOS = [
        ('emitida', 'Emitida'),
        ('aplicada', 'Aplicada Parcialmente'),
        ('utilizada', 'Utilizada Completamente'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]
    
    codigo_nota = models.CharField(max_length=20, unique=True, db_index=True)
    devolucion = models.OneToOneField(Devolucion, on_delete=models.CASCADE, related_name='nota_credito')
    venta_original = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='notas_credito')
    
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_disponible = models.DecimalField(max_digits=10, decimal_places=2)
    
    fecha_emision = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    fecha_utilizacion_completa = models.DateTimeField(null=True, blank=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='emitida', db_index=True)
    
    class Meta:
        db_table = 'notas_credito'
        verbose_name = 'Nota de Crédito'
        verbose_name_plural = 'Notas de Crédito'
        ordering = ['-fecha_emision']
    
    def __str__(self):
        return f"{self.codigo_nota} - ${self.saldo_disponible} disponible"
    
    def esta_vigente(self):
        """Verifica si la nota está vigente"""
        if self.estado in ['vencida', 'cancelada', 'utilizada']:
            return False
        
        if timezone.now().date() > self.fecha_vencimiento:
            self.estado = 'vencida'
            self.save()
            return False
        
        return self.saldo_disponible > 0
    
    def aplicar_a_venta(self, venta, monto_aplicado):
        """Aplica la nota de crédito a una nueva venta"""
        if not self.esta_vigente():
            raise ValueError("Esta nota de crédito no está disponible")
        
        if monto_aplicado > self.saldo_disponible:
            raise ValueError(f"Monto excede el saldo disponible (${self.saldo_disponible})")
        
        # Crear registro de aplicación
        AplicacionNotaCredito.objects.create(
            nota_credito=self,
            venta=venta,
            monto_aplicado=monto_aplicado
        )
        
        # Actualizar saldo
        self.saldo_disponible -= monto_aplicado
        
        if self.saldo_disponible == 0:
            self.estado = 'utilizada'
            self.fecha_utilizacion_completa = timezone.now()
        elif self.saldo_disponible < self.monto:
            self.estado = 'aplicada'
        
        self.save()
        
        return True


class AplicacionNotaCredito(models.Model):
    """Registro de aplicaciones de notas de crédito"""
    nota_credito = models.ForeignKey(NotaCredito, on_delete=models.CASCADE, related_name='aplicaciones')
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='notas_aplicadas')
    monto_aplicado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_aplicacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'aplicaciones_notas_credito'
        verbose_name = 'Aplicación de Nota de Crédito'
        verbose_name_plural = 'Aplicaciones de Notas de Crédito'
    
    def __str__(self):
        return f"{self.nota_credito.codigo_nota} aplicada a Venta #{self.venta.codigo_venta}"


# ================================================
# MODELO PARA AUDITORÍA
# ================================================

class AuditoriaMovimiento(models.Model):
    TIPOS_ACCION = [
        ('venta_crear', 'Crear Venta'),
        ('venta_anular', 'Anular Venta'),
        ('venta_modificar', 'Modificar Venta'),
        ('devolucion_crear', 'Crear Devolución'),
        ('devolucion_aprobar', 'Aprobar Devolución'),
        ('devolucion_rechazar', 'Rechazar Devolución'),
        ('devolucion_procesar', 'Procesar Devolución'),
        ('nota_credito_emitir', 'Emitir Nota Crédito'),
        ('nota_credito_aplicar', 'Aplicar Nota Crédito'),
        ('cierre_caja', 'Cierre de Caja'),
        ('ticket_crear', 'Crear Ticket'),
        ('ticket_finalizar', 'Finalizar Ticket'),
        ('ticket_cancelar', 'Cancelar Ticket'),
        ('producto_crear', 'Crear Producto'),
        ('producto_modificar', 'Modificar Producto'),
        ('stock_ajustar', 'Ajustar Stock'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=50, choices=TIPOS_ACCION, db_index=True)
    
    # Referencias opcionales
    venta = models.ForeignKey(Venta, on_delete=models.SET_NULL, null=True, blank=True)
    devolucion = models.ForeignKey(Devolucion, on_delete=models.SET_NULL, null=True, blank=True)
    
    descripcion = models.TextField()
    datos_json = models.JSONField(default=dict, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'auditoria_movimientos'
        verbose_name = 'Auditoría de Movimiento'
        verbose_name_plural = 'Auditoría de Movimientos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_accion_display()} - {self.usuario} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
    
    @staticmethod
    def registrar(usuario, accion, descripcion, venta=None, devolucion=None, datos_adicionales=None, request=None):
        """Método estático para registrar auditoría fácilmente"""
        ip = None
        user_agent = ''
        
        if request:
            ip = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        return AuditoriaMovimiento.objects.create(
            usuario=usuario,
            accion=accion,
            descripcion=descripcion,
            venta=venta,
            devolucion=devolucion,
            datos_json=datos_adicionales or {},
            ip_address=ip,
            user_agent=user_agent
        )