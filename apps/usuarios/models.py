from django.db import models
from django.contrib.auth.models import User


# ============================================================
# ROLES
# ============================================================

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


# ============================================================
# PERMISOS
# ============================================================

class Permiso(models.Model):
    """
    Permisos específicos de módulos del sistema
    """
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    modulo = models.CharField(max_length=50)

    class Meta:
        db_table = 'permisos'
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        ordering = ['modulo', 'nombre']

    def __str__(self):
        return f"{self.modulo} - {self.nombre}"


# ============================================================
# ROLES ↔ PERMISOS (INTERMEDIA)
# ============================================================

class RolPermiso(models.Model):
    rol = models.ForeignKey(RolUsuario, on_delete=models.CASCADE, related_name='permisos')
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)

    class Meta:
        db_table = 'rol_permisos'
        unique_together = ('rol', 'permiso')
        verbose_name = 'Permiso de Rol'
        verbose_name_plural = 'Permisos de Roles'

    def __str__(self):
        return f"{self.rol} - {self.permiso}"


# ============================================================
# USUARIO EXTENDIDO
# ============================================================

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

    def tiene_permiso(self, codigo_permiso):
        if not self.rol:
            return False

        if self.rol.tipo == 'superadmin':
            return True

        return RolPermiso.objects.filter(
            rol=self.rol,
            permiso__codigo=codigo_permiso
        ).exists()

    def obtener_permisos(self):
        if not self.rol:
            return []

        if self.rol.tipo == 'superadmin':
            return Permiso.objects.all()

        return Permiso.objects.filter(
            rolpermiso__rol=self.rol
        ).distinct()
