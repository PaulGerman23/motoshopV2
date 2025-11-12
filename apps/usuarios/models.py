from django.db import models
from django.contrib.auth.models import User

class RolUsuario(models.Model):
    TIPOS_ROL = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Administrador'),
        ('ventas', 'Ventas'),
        ('caja', 'Caja'),
    ]

    tipo = models.CharField(max_length=50, unique=True, choices=TIPOS_ROL)

    class Meta:
        db_table = 'rol_usuarios'
        verbose_name = 'Rol de Usuario'
        verbose_name_plural = 'Roles de Usuarios'

    def __str__(self):
        return self.get_tipo_display()


class UsuarioExtendido(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    dni = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    rol = models.ForeignKey(RolUsuario, on_delete=models.SET_NULL, null=True)
    status = models.IntegerField(default=1)

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario Extendido'
        verbose_name_plural = 'Usuarios Extendidos'

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def nombre_completo(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def es_admin(self):
        return self.rol and self.rol.tipo in ['superadmin', 'admin']