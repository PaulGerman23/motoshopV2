"""
Script para cargar permisos del sistema MotoShop
Ejecución:
    CMD:        python manage.py shell < cargar_permisos.py
    PowerShell: python cargar_permisos.py
"""

import os
import sys
import django

# ---------------------------------------------
# CONFIGURACIÓN PARA QUE DJANGO SE INICIALICE
# ---------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Agregar el directorio PADRE al path
# Esto permite que Python encuentre "motoshop_django"
sys.path.append(BASE_DIR)
sys.path.append(os.path.dirname(BASE_DIR))

# Settings correctos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "motoshop_django.settings")

# Inicializar Django
django.setup()

# ---------------------------------------------
# IMPORTAR MODELOS
# ---------------------------------------------
from apps.usuarios.models import Permiso, RolUsuario, RolPermiso

print("\n=== CARGANDO PERMISOS DEL SISTEMA ===\n")

# ---------------------------------------------
# LISTA DE PERMISOS
# ---------------------------------------------
permisos_data = [
    {'nombre': 'Ver Dashboard', 'codigo': 'ver_dashboard', 'modulo': 'dashboard', 'descripcion': 'Acceso al panel principal'},

    # Productos
    {'nombre': 'Ver Productos', 'codigo': 'ver_productos', 'modulo': 'productos', 'descripcion': 'Ver listado de productos'},
    {'nombre': 'Crear Productos', 'codigo': 'crear_productos', 'modulo': 'productos', 'descripcion': 'Crear nuevos productos'},
    {'nombre': 'Editar Productos', 'codigo': 'editar_productos', 'modulo': 'productos', 'descripcion': 'Modificar productos existentes'},
    {'nombre': 'Eliminar Productos', 'codigo': 'eliminar_productos', 'modulo': 'productos', 'descripcion': 'Eliminar productos'},

    # Categorías
    {'nombre': 'Ver Categorías', 'codigo': 'ver_categorias', 'modulo': 'categorias', 'descripcion': 'Ver listado de categorías'},
    {'nombre': 'Crear Categorías', 'codigo': 'crear_categorias', 'modulo': 'categorias', 'descripcion': 'Crear nuevas categorías'},
    {'nombre': 'Editar Categorías', 'codigo': 'editar_categorias', 'modulo': 'categorias', 'descripcion': 'Modificar categorías'},

    # Proveedores
    {'nombre': 'Ver Proveedores', 'codigo': 'ver_proveedores', 'modulo': 'proveedores', 'descripcion': 'Ver listado de proveedores'},
    {'nombre': 'Crear Proveedores', 'codigo': 'crear_proveedores', 'modulo': 'proveedores', 'descripcion': 'Crear nuevos proveedores'},
    {'nombre': 'Editar Proveedores', 'codigo': 'editar_proveedores', 'modulo': 'proveedores', 'descripcion': 'Modificar proveedores'},
    {'nombre': 'Eliminar Proveedores', 'codigo': 'eliminar_proveedores', 'modulo': 'proveedores', 'descripcion': 'Eliminar proveedores'},

    # Ventas
    {'nombre': 'Ver Ventas', 'codigo': 'ver_ventas', 'modulo': 'ventas', 'descripcion': 'Ver historial de ventas'},
    {'nombre': 'Crear Ventas', 'codigo': 'crear_ventas', 'modulo': 'ventas', 'descripcion': 'Realizar nuevas ventas'},
    {'nombre': 'Ver Detalle Ventas', 'codigo': 'ver_detalle_ventas', 'modulo': 'ventas', 'descripcion': 'Ver detalles de ventas'},
    {'nombre': 'Anular Ventas', 'codigo': 'anular_ventas', 'modulo': 'ventas', 'descripcion': 'Anular ventas realizadas'},

    # Clientes
    {'nombre': 'Ver Clientes', 'codigo': 'ver_clientes', 'modulo': 'clientes', 'descripcion': 'Ver listado de clientes'},
    {'nombre': 'Crear Clientes', 'codigo': 'crear_clientes', 'modulo': 'clientes', 'descripcion': 'Crear nuevos clientes'},
    {'nombre': 'Editar Clientes', 'codigo': 'editar_clientes', 'modulo': 'clientes', 'descripcion': 'Modificar clientes'},
    {'nombre': 'Eliminar Clientes', 'codigo': 'eliminar_clientes', 'modulo': 'clientes', 'descripcion': 'Eliminar clientes'},

    # Usuarios
    {'nombre': 'Ver Usuarios', 'codigo': 'ver_usuarios', 'modulo': 'usuarios', 'descripcion': 'Ver listado de usuarios'},
    {'nombre': 'Crear Usuarios', 'codigo': 'crear_usuarios', 'modulo': 'usuarios', 'descripcion': 'Crear nuevos usuarios'},
    {'nombre': 'Editar Usuarios', 'codigo': 'editar_usuarios', 'modulo': 'usuarios', 'descripcion': 'Modificar usuarios'},
    {'nombre': 'Eliminar Usuarios', 'codigo': 'eliminar_usuarios', 'modulo': 'usuarios', 'descripcion': 'Eliminar usuarios'},

    # Reportes
    {'nombre': 'Ver Reportes', 'codigo': 'ver_reportes', 'modulo': 'reportes', 'descripcion': 'Ver reportes y estadísticas'},
    {'nombre': 'Exportar Reportes', 'codigo': 'exportar_reportes', 'modulo': 'reportes', 'descripcion': 'Exportar reportes'},
]

print("1. Creando permisos...\n")

for perm_data in permisos_data:
    permiso, created = Permiso.objects.get_or_create(
        codigo=perm_data["codigo"],
        defaults=perm_data
    )
    print(f"{'✓' if created else '-'} {perm_data['nombre']}")

print("\n2. Asignando permisos a roles...\n")

# ADMIN
try:
    rol_admin = RolUsuario.objects.get(tipo='admin')
    for permiso in Permiso.objects.all():
        RolPermiso.objects.get_or_create(rol=rol_admin, permiso=permiso)
    print("  ✓ Admin: permisos asignados")
except RolUsuario.DoesNotExist:
    print("  ⚠ Rol 'admin' no existe")

# VENTAS
try:
    rol_ventas = RolUsuario.objects.get(tipo='ventas')
    codigos_ventas = [
        'ver_dashboard',
        'ver_productos',
        'ver_categorias',
        'ver_ventas', 'crear_ventas', 'ver_detalle_ventas',
        'ver_clientes', 'crear_clientes', 'editar_clientes',
    ]
    for codigo in codigos_ventas:
        permiso = Permiso.objects.get(codigo=codigo)
        RolPermiso.objects.get_or_create(rol=rol_ventas, permiso=permiso)
    print("  ✓ Ventas: permisos asignados")
except RolUsuario.DoesNotExist:
    print("  ⚠ Rol 'ventas' no existe")

# CAJA
try:
    rol_caja = RolUsuario.objects.get(tipo='caja')
    codigos_caja = [
        'ver_dashboard',
        'ver_productos',
        'ver_ventas', 'crear_ventas', 'ver_detalle_ventas',
        'ver_clientes', 'crear_clientes'
    ]
    for codigo in codigos_caja:
        permiso = Permiso.objects.get(codigo=codigo)
        RolPermiso.objects.get_or_create(rol=rol_caja, permiso=permiso)
    print("  ✓ Caja: permisos asignados")
except RolUsuario.DoesNotExist:
    print("  ⚠ Rol 'caja' no existe")

print("\n=== COMPLETADO ===\n")
