# apps/ventas/migrations/0002_agregar_turno_cierrecaja.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0001_initial'),
    ]

    operations = [
        # Eliminar restricción única anterior
        migrations.AlterUniqueTogether(
            name='cierrecaja',
            unique_together=set(),
        ),
        
        # Agregar campo turno
        migrations.AddField(
            model_name='cierrecaja',
            name='turno',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('manana', 'Mañana'),
                    ('tarde', 'Tarde'),
                    ('noche', 'Noche')
                ],
                default='manana',
                help_text='Turno del cierre: Mañana (06:00-14:00), Tarde (14:00-22:00), Noche (22:00-06:00)'
            ),
        ),
        
        # Nueva restricción única por fecha y turno
        migrations.AlterUniqueTogether(
            name='cierrecaja',
            unique_together={('fecha', 'turno')},
        ),
    ]