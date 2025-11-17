# apps/ventas/migrations/0002_tickets_cierrecaja.py
# Ejecutar: python manage.py makemigrations
# Luego: python manage.py migrate

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0001_initial'),
        ('clientes', '0001_initial'),
        ('inventario', '0002_producto_stock_minimo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Actualizar choices de tipo_pago en Venta
        migrations.AlterField(
            model_name='venta',
            name='tipo_pago',
            field=models.CharField(
                choices=[
                    ('efectivo', 'Efectivo'),
                    ('debito', 'Tarjeta de Débito'),
                    ('credito', 'Tarjeta de Crédito'),
                    ('transferencia', 'Transferencia'),
                    ('mixto', 'Pago Mixto')
                ],
                max_length=50
            ),
        ),
        
        # Crear modelo Ticket
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_id', models.CharField(db_index=True, max_length=20, unique=True)),
                ('codigo_ticket', models.IntegerField(unique=True)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('descuento', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('descuento_porcentaje', models.DecimalField(decimal_places=2, default=0, help_text='Descuento en %', max_digits=5)),
                ('descuento_monto', models.DecimalField(decimal_places=2, default=0, help_text='Descuento en $', max_digits=10)),
                ('tipo_pago', models.CharField(blank=True, choices=[('efectivo', 'Efectivo'), ('debito', 'Tarjeta de Débito'), ('credito', 'Tarjeta de Crédito'), ('transferencia', 'Transferencia'), ('mixto', 'Pago Mixto')], max_length=20)),
                ('monto_efectivo', models.DecimalField(decimal_places=2, default=0, help_text='Para pagos mixtos', max_digits=10)),
                ('monto_tarjeta', models.DecimalField(decimal_places=2, default=0, help_text='Para pagos mixtos', max_digits=10)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('finalizado', 'Finalizado'), ('cancelado', 'Cancelado')], db_index=True, default='pendiente', max_length=20)),
                ('observacion', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('fecha_finalizacion', models.DateTimeField(blank=True, null=True)),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='clientes.cliente')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets', to=settings.AUTH_USER_MODEL)),
                ('venta', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ticket_original', to='ventas.venta')),
            ],
            options={
                'verbose_name': 'Ticket',
                'verbose_name_plural': 'Tickets',
                'db_table': 'tickets',
                'ordering': ['-fecha_creacion'],
            },
        ),
        
        # Crear modelo DetalleTicket
        migrations.CreateModel(
            name='DetalleTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(help_text='Copia de la descripción', max_length=500)),
                ('cantidad', models.IntegerField()),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('activo', models.BooleanField(default=True, help_text='Para eliminación lógica')),
                ('producto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventario.producto')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='ventas.ticket')),
            ],
            options={
                'verbose_name': 'Detalle de Ticket',
                'verbose_name_plural': 'Detalles de Tickets',
                'db_table': 'detalle_tickets',
            },
        ),
        
        # Crear modelo CierreCaja
        migrations.CreateModel(
            name='CierreCaja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(db_index=True)),
                ('monto_inicial', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_ventas', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cantidad_ventas', models.IntegerField(default=0)),
                ('efectivo_ventas', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('debito_ventas', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('credito_ventas', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('transferencia_ventas', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('egresos', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('detalle_egresos', models.TextField(blank=True)),
                ('monto_final_esperado', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('monto_final_real', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('diferencia', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('observaciones', models.TextField(blank=True)),
                ('fecha_cierre', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cierre de Caja',
                'verbose_name_plural': 'Cierres de Caja',
                'db_table': 'cierres_caja',
                'ordering': ['-fecha'],
                'unique_together': {('fecha', 'usuario')},
            },
        ),
        
        # Agregar índices
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['estado', 'usuario'], name='tickets_estado_usuario_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['fecha_creacion'], name='tickets_fecha_creacion_idx'),
        ),
    ]