# apps/ventas/models.py - VERSIÓN FINAL CORREGIDA

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.clientes.models import Cliente
from apps.inventario.models import Producto
from decimal import Decimal
from datetime import timedelta, datetime, time

# =====================================================================
# MODELO: VENTA
# =====================================================================

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

    # Pago mixto
    es_pago_mixto = models.BooleanField(default=False)
    monto_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Descuentos
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descuento_monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'ventas'
        ordering = ['-fecha']

    def __str__(self):
        fecha_local = timezone.localtime(self.fecha).strftime('%d/%m/%Y')
        return f"Venta #{self.codigo_venta} - {fecha_local}"

    # CORREGIDO
    def puede_devolverse(self):
        """Evitar errores por timezone con fecha UTC"""
        if self.estado_venta == 0:
            return False
        
        if self.devoluciones.filter(estado__in=['pendiente', 'aprobada']).exists():
            return False
        
        dias_desde_venta = (timezone.localtime() - timezone.localtime(self.fecha)).days
        
        return dias_desde_venta <= 30


# =====================================================================
# MODELO: DETALLE VENTA
# =====================================================================

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(default=1)

    class Meta:
        db_table = 'detalle_ventas'

    def __str__(self):
        return f"{self.producto} - {self.cantidad} unidades"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


# =====================================================================
# MODELO: TICKET
# =====================================================================

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
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Ticket #{self.codigo_ticket} - {self.get_estado_display()}"

    def cancelar(self):
        if self.estado == 'finalizado':
            raise ValueError("No se puede cancelar un ticket finalizado")

        self.estado = 'cancelado'
        self.save()

        AuditoriaMovimiento.registrar(
            usuario=self.usuario,
            accion='ticket_cancelar',
            descripcion=f'Ticket {self.ticket_id} cancelado'
        )

    def finalizar(self):
        """Finaliza ticket y crea venta"""
        from django.db import transaction
        from .models import DetalleVenta, Venta

        if self.estado != 'pendiente':
            raise ValueError("Solo se pueden finalizar tickets pendientes")

        if not self.tipo_pago:
            raise ValueError("Debe especificar un método de pago")

        with transaction.atomic():
            for detalle in self.detalles.filter(activo=True):
                if detalle.producto and detalle.producto.stock < detalle.cantidad:
                    raise ValueError(f'Stock insuficiente para {detalle.producto.descripcion}')

            ultimo_codigo = Venta.objects.order_by('-codigo_venta').first()
            nuevo_codigo = (ultimo_codigo.codigo_venta + 1) if ultimo_codigo else 1000

            venta = Venta.objects.create(
                cliente=self.cliente,
                usuario=self.usuario,
                subtotal=self.subtotal,
                descuento_porcentaje=self.descuento_porcentaje,
                descuento_monto=self.descuento_monto,
                total=self.total,
                tipo_pago=self.tipo_pago,
                es_pago_mixto=(self.tipo_pago == 'mixto'),
                monto_efectivo=self.monto_efectivo,
                monto_tarjeta=self.monto_tarjeta,
                observacion=self.observacion,
                codigo_venta=nuevo_codigo,
                estado_venta=2
            )

            for detalle in self.detalles.filter(activo=True):
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=detalle.producto,
                    cantidad=detalle.cantidad,
                    precio_unitario=detalle.precio_unitario,
                    subtotal=detalle.subtotal
                )
                if detalle.producto:
                    detalle.producto.stock -= detalle.cantidad
                    detalle.producto.save()

            self.estado = 'finalizado'
            self.fecha_finalizacion = timezone.localtime()
            self.venta = venta
            self.save()

            AuditoriaMovimiento.registrar(
                usuario=self.usuario,
                accion='ticket_finalizar',
                descripcion=f'Ticket {self.ticket_id} finalizado → Venta #{nuevo_codigo}',
                venta=venta
            )

            return venta

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

# =====================================================================
# MODELO: CIERRE DE CAJA (CORREGIDO)
# =====================================================================

class CierreCaja(models.Model):
    TURNOS = [
        ('manana', 'Mañana'),
        ('tarde', 'Tarde'),
        ('noche', 'Noche'),
    ]

    fecha = models.DateField(db_index=True)
    turno = models.CharField(max_length=10, choices=TURNOS)
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
        unique_together = ('fecha', 'turno')

    def __str__(self):
        return f"Cierre {self.get_turno_display()} - {self.fecha}"

    # CORREGIDO
    @staticmethod
    def determinar_turno_actual():
        """Determina el turno usando la hora LOCAL."""
        hora_actual = timezone.localtime().time()

        if time(6, 0) <= hora_actual < time(14, 0):
            return 'manana'
        elif time(14, 0) <= hora_actual < time(22, 0):
            return 'tarde'
        else:
            return 'noche'
    @classmethod
    def crear_sin_actividad(cls, fecha, turno, usuario):
        """
        Crea un cierre de caja sin actividad (sin ventas).
        Todos los montos en 0.
        """
        cierre = cls.objects.create(
            fecha=fecha,
            turno=turno,
            usuario=usuario,
            monto_inicial=0,
            total_ventas=0,
            cantidad_ventas=0,
            efectivo_ventas=0,
            debito_ventas=0,
            credito_ventas=0,
            transferencia_ventas=0,
            egresos=0,
            detalle_egresos='',
            monto_final_esperado=0,
            monto_final_real=0,
            diferencia=0,
            observaciones='Cierre sin actividad'
        )
        return cierre
    # CORREGIDO
    @staticmethod
    def obtener_rango_horario_turno(turno):
        rangos = {
            'manana': (time(6, 0), time(14, 0)),
            'tarde': (time(14, 0), time(22, 0)),
            'noche': (time(22, 0), time(6, 0)),
        }
        return rangos[turno]

    # CORREGIDO COMPLETAMENTE
    def calcular_totales(self):
        zona = timezone.get_current_timezone()

        hora_inicio, hora_fin = self.obtener_rango_horario_turno(self.turno)

        if self.turno == 'noche':
            inicio = zona.localize(datetime.combine(self.fecha, hora_inicio))
            fin = zona.localize(datetime.combine(self.fecha + timedelta(days=1), hora_fin))
        else:
            inicio = zona.localize(datetime.combine(self.fecha, hora_inicio))
            fin = zona.localize(datetime.combine(self.fecha, hora_fin))

        ventas_turno = Venta.objects.filter(
            fecha__gte=inicio,
            fecha__lt=fin,
            estado_venta=2
        )

        from django.db.models import Sum

        self.total_ventas = ventas_turno.aggregate(Sum('total'))['total__sum'] or 0
        self.cantidad_ventas = ventas_turno.count()

        self.efectivo_ventas = ventas_turno.filter(tipo_pago='efectivo').aggregate(Sum('total'))['total__sum'] or 0
        self.debito_ventas = ventas_turno.filter(tipo_pago='debito').aggregate(Sum('total'))['total__sum'] or 0
        self.credito_ventas = ventas_turno.filter(tipo_pago='credito').aggregate(Sum('total'))['total__sum'] or 0
        self.transferencia_ventas = ventas_turno.filter(tipo_pago='transferencia').aggregate(Sum('total'))['total__sum'] or 0

        mixtos = ventas_turno.filter(tipo_pago='mixto')
        for v in mixtos:
            self.efectivo_ventas += v.monto_efectivo
            self.debito_ventas += v.monto_tarjeta

        self.monto_final_esperado = self.monto_inicial + self.efectivo_ventas - self.egresos
        self.diferencia = self.monto_final_real - self.monto_final_esperado

        self.save()


# =====================================================================
# MODELOS DE DEVOLUCIONES - CORREGIDO
# =====================================================================

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

    usuario_solicita = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='devoluciones_solicitadas')
    usuario_aprueba = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='devoluciones_aprobadas')

    observaciones_aprobacion = models.TextField(blank=True)

    class Meta:
        db_table = 'devoluciones'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Devolución {self.codigo_devolucion} - Venta #{self.venta_original.codigo_venta}"

    def calcular_total(self):
        self.monto_total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.save()

    def puede_procesarse(self):
        return self.estado == 'aprobada'

    def procesar(self, usuario):
        if not self.puede_procesarse():
            raise ValueError("Solo se pueden procesar devoluciones aprobadas")

        for detalle in self.detalles.all():
            if detalle.producto:
                detalle.producto.stock += detalle.cantidad
                detalle.producto.save()

        ultimo = NotaCredito.objects.order_by('-id').first()
        nuevo_codigo = (ultimo.id + 1) if ultimo else 1000

        nota = NotaCredito.objects.create(
            codigo_nota=f"NC-{nuevo_codigo:06d}",
            devolucion=self,
            venta_original=self.venta_original,
            monto=self.monto_total,
            saldo_disponible=self.monto_total,
            fecha_vencimiento=timezone.localtime().date() + timedelta(days=90)
        )

        self.estado = 'procesada'
        self.fecha_procesamiento = timezone.localtime()
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
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"{self.codigo_nota} - ${self.saldo_disponible} disponible"

    def esta_vigente(self):
        if self.estado in ['vencida', 'cancelada', 'utilizada']:
            return False

        hoy = timezone.localtime().date()

        if hoy > self.fecha_vencimiento:
            self.estado = 'vencida'
            self.save()
            return False

        return self.saldo_disponible > 0

    def aplicar_a_venta(self, venta, monto_aplicado):
        if not self.esta_vigente():
            raise ValueError("Esta nota de crédito no está disponible")

        if monto_aplicado > self.saldo_disponible:
            raise ValueError(f"Monto excede el saldo disponible (${self.saldo_disponible})")

        AplicacionNotaCredito.objects.create(
            nota_credito=self,
            venta=venta,
            monto_aplicado=monto_aplicado
        )

        self.saldo_disponible -= monto_aplicado

        if self.saldo_disponible == 0:
            self.estado = 'utilizada'
            self.fecha_utilizacion_completa = timezone.localtime()
        elif self.saldo_disponible < self.monto:
            self.estado = 'aplicada'

        self.save()

        return True


class AplicacionNotaCredito(models.Model):
    nota_credito = models.ForeignKey(NotaCredito, on_delete=models.CASCADE, related_name='aplicaciones')
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='notas_aplicadas')
    monto_aplicado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_aplicacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'aplicaciones_notas_credito'

    def __str__(self):
        fecha_local = timezone.localtime(self.fecha_aplicacion).strftime("%d/%m/%Y %H:%M")
        return f"{self.nota_credito.codigo_nota} aplicada a Venta #{self.venta.codigo_venta} ({fecha_local})"


# =====================================================================
# MODELO: AUDITORÍA
# =====================================================================

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

    venta = models.ForeignKey(Venta, on_delete=models.SET_NULL, null=True, blank=True)
    devolucion = models.ForeignKey(Devolucion, on_delete=models.SET_NULL, null=True, blank=True)

    descripcion = models.TextField()
    datos_json = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'auditoria_movimientos'
        ordering = ['-fecha']

    def __str__(self):
        fecha_local = timezone.localtime(self.fecha).strftime('%d/%m/%Y %H:%M')
        return f"{self.get_accion_display()} - {self.usuario} - {fecha_local}"

    @staticmethod
    def registrar(usuario, accion, descripcion, venta=None, devolucion=None, datos_adicionales=None, request=None):
        ip = request.META.get('REMOTE_ADDR') if request else None
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500] if request else ''

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
    
    