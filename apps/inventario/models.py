# apps/inventario/models.py

from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    estado = models.IntegerField(default=1)

    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    CONDICIONES_IVA = [
        ('Responsable Inscripto', 'Responsable Inscripto'),
        ('Monotributista', 'Monotributista'),
        ('Exento', 'Exento'),
        ('Consumidor Final', 'Consumidor Final'),
    ]

    razon_social = models.CharField(max_length=200)
    codigo_proveedor = models.IntegerField(unique=True)
    cuit = models.CharField(max_length=13, unique=True)
    nombre_contacto = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    condicion_iva = models.CharField(max_length=50, choices=CONDICIONES_IVA)
    estado = models.IntegerField(default=1)

    class Meta:
        db_table = 'proveedores'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.razon_social


class Producto(models.Model):
    codigo = models.IntegerField(unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5, help_text='Stock mínimo para alertas')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.IntegerField(default=1)

    class Meta:
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"

    @property
    def margen_ganancia(self):
        """Calcula el margen de ganancia en porcentaje"""
        if self.precio_costo > 0:
            return ((self.precio_venta - self.precio_costo) / self.precio_costo) * 100
        return 0
    
    @property
    def tiene_stock_bajo(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.stock <= self.stock_minimo
    
    @property
    def nivel_stock(self):
        """Retorna el nivel de stock: 'bajo', 'medio' o 'alto'"""
        if self.stock <= self.stock_minimo:
            return 'bajo'
        elif self.stock <= (self.stock_minimo * 3):
            return 'medio'
        else:
            return 'alto'