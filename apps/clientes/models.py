from django.db import models

class Cliente(models.Model):
    CONDICIONES_IVA = [
        ('Responsable Inscripto', 'Responsable Inscripto'),
        ('Monotributista', 'Monotributista'),
        ('Exento', 'Exento'),
        ('Consumidor Final', 'Consumidor Final'),
    ]

    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    codigo_cliente = models.IntegerField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    dni = models.CharField(max_length=10, blank=True, null=True)
    cuit = models.CharField(max_length=13, unique=True, blank=True, null=True)
    condicion_iva = models.CharField(max_length=50, choices=CONDICIONES_IVA)
    estado = models.IntegerField(default=1)

    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"