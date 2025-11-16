"""
Script para cargar datos de prueba en MotoShop Django
Ejecutar: python manage.py shell < cargar_datos_prueba.py
"""

from django.contrib.auth.models import User
from apps.usuarios.models import RolUsuario, UsuarioExtendido
from apps.inventario.models import Categoria, Proveedor, Producto
from apps.clientes.models import Cliente
from apps.ventas.models import Venta, DetalleVenta
from decimal import Decimal

print("=== INICIANDO CARGA DE DATOS DE PRUEBA ===\n")

# 1. CREAR ROLES
print("1. Creando roles de usuario...")
roles_data = [
    ('superadmin', 'Super Admin'),
    ('admin', 'Administrador'),
    ('ventas', 'Ventas'),
    ('caja', 'Caja'),
]

for tipo, nombre in roles_data:
    rol, created = RolUsuario.objects.get_or_create(tipo=tipo)
    if created:
        print(f"  ✓ Rol creado: {nombre}")
    else:
        print(f"  - Rol ya existe: {nombre}")

# 2. CREAR USUARIOS
print("\n2. Creando usuarios...")
# Usuario Admin
if not User.objects.filter(username='admin').exists():
    user_admin = User.objects.create_user(
        username='admin',
        email='admin@motoshop.com',
        password='admin123',
        first_name='Administrador',
        last_name='Sistema',
        is_staff=True,
        is_superuser=True
    )
    UsuarioExtendido.objects.create(
        user=user_admin,
        dni='12345678',
        phone='387-1234567',
        rol=RolUsuario.objects.get(tipo='superadmin'),
        status=1
    )
    print("  ✓ Usuario admin creado (admin/admin123)")
else:
    print("  - Usuario admin ya existe")

# Usuario Vendedor
if not User.objects.filter(username='vendedor').exists():
    user_vendedor = User.objects.create_user(
        username='vendedor',
        email='vendedor@motoshop.com',
        password='vendedor123',
        first_name='Juan',
        last_name='Pérez'
    )
    UsuarioExtendido.objects.create(
        user=user_vendedor,
        dni='87654321',
        phone='387-7654321',
        rol=RolUsuario.objects.get(tipo='ventas'),
        status=1
    )
    print("  ✓ Usuario vendedor creado (vendedor/vendedor123)")
else:
    print("  - Usuario vendedor ya existe")

# 3. CREAR CATEGORÍAS
print("\n3. Creando categorías...")
categorias_data = [
    'Filtros',
    'Frenos',
    'Aceites',
    'Transmisión',
    'Suspensión',
    'Motor',
    'Eléctrico',
    'Escape',
    'Neumáticos',
    'Accesorios',
    'Iluminación',
    'Carrocería'
]

for nombre in categorias_data:
    categoria, created = Categoria.objects.get_or_create(
        nombre=nombre,
        defaults={'estado': 1}
    )
    if created:
        print(f"  ✓ Categoría creada: {nombre}")

# 4. CREAR PROVEEDORES
print("\n4. Creando proveedores...")
proveedores_data = [
    {
        'razon_social': 'Repuestos del Norte SA',
        'codigo_proveedor': 1001,
        'cuit': '30-12345678-9',
        'nombre_contacto': 'Carlos Méndez',
        'telefono': '387-4001122',
        'email': 'ventas@repuestosnorte.com',
        'direccion': 'Av. Belgrano 1234, Salta',
        'condicion_iva': 'Responsable Inscripto',
    },
    {
        'razon_social': 'Distribuidora Motoshop SRL',
        'codigo_proveedor': 1002,
        'cuit': '30-98765432-1',
        'nombre_contacto': 'María González',
        'telefono': '387-4003344',
        'email': 'info@distrimoto.com',
        'direccion': 'Calle Caseros 567, Salta',
        'condicion_iva': 'Responsable Inscripto',
    },
    {
        'razon_social': 'Auto Partes Express',
        'codigo_proveedor': 1003,
        'cuit': '30-55555555-5',
        'nombre_contacto': 'Roberto Díaz',
        'telefono': '387-4005566',
        'email': 'contacto@autopartes.com',
        'direccion': 'Ruta 9 Km 1200, Salta',
        'condicion_iva': 'Responsable Inscripto',
    }
]

for data in proveedores_data:
    proveedor, created = Proveedor.objects.get_or_create(
        codigo_proveedor=data['codigo_proveedor'],
        defaults=data
    )
    if created:
        print(f"  ✓ Proveedor creado: {data['razon_social']}")

# 5. CREAR PRODUCTOS
print("\n5. Creando productos...")
productos_data = [
    # Filtros
    {'codigo': 1, 'descripcion': 'Filtro de Aceite Mann W719/30', 'precio_costo': 2500, 'precio_venta': 3500, 'stock': 25, 'categoria': 'Filtros', 'proveedor': 1001},
    {'codigo': 2, 'descripcion': 'Filtro de Aire K&N 33-2304', 'precio_costo': 8500, 'precio_venta': 12000, 'stock': 15, 'categoria': 'Filtros', 'proveedor': 1001},
    {'codigo': 3, 'descripcion': 'Filtro de Combustible Bosch F026403006', 'precio_costo': 3200, 'precio_venta': 4500, 'stock': 30, 'categoria': 'Filtros', 'proveedor': 1002},
    
    # Frenos
    {'codigo': 4, 'descripcion': 'Pastillas de Freno Delanteras Brembo P85020', 'precio_costo': 12000, 'precio_venta': 17000, 'stock': 20, 'categoria': 'Frenos', 'proveedor': 1002},
    {'codigo': 5, 'descripcion': 'Disco de Freno Ventilado 280mm', 'precio_costo': 15000, 'precio_venta': 21000, 'stock': 12, 'categoria': 'Frenos', 'proveedor': 1002},
    {'codigo': 6, 'descripcion': 'Líquido de Frenos DOT 4 ATE 1L', 'precio_costo': 1800, 'precio_venta': 2800, 'stock': 50, 'categoria': 'Frenos', 'proveedor': 1003},
    
    # Aceites
    {'codigo': 7, 'descripcion': 'Aceite Motor Castrol 10W40 4L', 'precio_costo': 8500, 'precio_venta': 12500, 'stock': 40, 'categoria': 'Aceites', 'proveedor': 1001},
    {'codigo': 8, 'descripcion': 'Aceite Sintético Mobil 1 5W30 4L', 'precio_costo': 15000, 'precio_venta': 22000, 'stock': 25, 'categoria': 'Aceites', 'proveedor': 1001},
    
    # Transmisión
    {'codigo': 9, 'descripcion': 'Cadena de Transmisión RK 520', 'precio_costo': 18000, 'precio_venta': 25000, 'stock': 8, 'categoria': 'Transmisión', 'proveedor': 1002},
    {'codigo': 10, 'descripcion': 'Kit de Embrague LUK RepSet', 'precio_costo': 35000, 'precio_venta': 48000, 'stock': 5, 'categoria': 'Transmisión', 'proveedor': 1002},
    
    # Suspensión
    {'codigo': 11, 'descripcion': 'Amortiguador Delantero Monroe G8088', 'precio_costo': 22000, 'precio_venta': 32000, 'stock': 10, 'categoria': 'Suspensión', 'proveedor': 1003},
    {'codigo': 12, 'descripcion': 'Espirales Delanteros Cofap', 'precio_costo': 12000, 'precio_venta': 17500, 'stock': 14, 'categoria': 'Suspensión', 'proveedor': 1003},
    
    # Motor
    {'codigo': 13, 'descripcion': 'Bujía NGK Iridium IFR6T11', 'precio_costo': 4500, 'precio_venta': 6500, 'stock': 60, 'categoria': 'Motor', 'proveedor': 1001},
    {'codigo': 14, 'descripcion': 'Correa de Distribución Gates 5494XS', 'precio_costo': 8000, 'precio_venta': 11500, 'stock': 18, 'categoria': 'Motor', 'proveedor': 1002},
    
    # Eléctrico
    {'codigo': 15, 'descripcion': 'Batería Moura 12V 60Ah', 'precio_costo': 45000, 'precio_venta': 65000, 'stock': 8, 'categoria': 'Eléctrico', 'proveedor': 1003},
    {'codigo': 16, 'descripcion': 'Alternador Bosch 120A', 'precio_costo': 85000, 'precio_venta': 120000, 'stock': 4, 'categoria': 'Eléctrico', 'proveedor': 1003},
    
    # Stock bajo
    {'codigo': 17, 'descripcion': 'Sensor de Oxígeno Bosch LSU 4.9', 'precio_costo': 35000, 'precio_venta': 48000, 'stock': 3, 'categoria': 'Eléctrico', 'proveedor': 1002},
    {'codigo': 18, 'descripcion': 'Bomba de Combustible Walbro 255', 'precio_costo': 52000, 'precio_venta': 75000, 'stock': 2, 'categoria': 'Motor', 'proveedor': 1001},
]

for data in productos_data:
    categoria = Categoria.objects.get(nombre=data['categoria'])
    proveedor = Proveedor.objects.get(codigo_proveedor=data['proveedor'])
    
    producto, created = Producto.objects.get_or_create(
        codigo=data['codigo'],
        defaults={
            'descripcion': data['descripcion'],
            'precio_costo': Decimal(str(data['precio_costo'])),
            'precio_venta': Decimal(str(data['precio_venta'])),
            'stock': data['stock'],
            'categoria': categoria,
            'proveedor': proveedor,
            'estado': 1
        }
    )
    if created:
        print(f"  ✓ Producto #{data['codigo']}: {data['descripcion'][:40]}...")

# 6. CREAR CLIENTES
print("\n6. Creando clientes...")
clientes_data = [
    {
        'nombre': 'Juan Carlos',
        'apellido': 'Rodríguez',
        'codigo_cliente': 1,
        'telefono': '387-5551234',
        'email': 'jrodriguez@email.com',
        'direccion': 'Av. San Martín 456, Salta',
        'dni': '30123456',
        'cuit': '20-30123456-7',
        'condicion_iva': 'Responsable Inscripto',
    },
    {
        'nombre': 'María Eugenia',
        'apellido': 'Fernández',
        'codigo_cliente': 2,
        'telefono': '387-5555678',
        'email': 'mfernandez@email.com',
        'direccion': 'Calle Mitre 123, Salta',
        'dni': '28765432',
        'cuit': '27-28765432-3',
        'condicion_iva': 'Monotributista',
    },
    {
        'nombre': 'Roberto Carlos',
        'apellido': 'López',
        'codigo_cliente': 3,
        'telefono': '387-5559012',
        'email': 'rlopez@email.com',
        'direccion': 'Pasaje Los Alamos 789, Salta',
        'dni': '35987654',
        'condicion_iva': 'Consumidor Final',
    },
    {
        'nombre': 'Ana María',
        'apellido': 'Gómez',
        'codigo_cliente': 4,
        'telefono': '387-5553456',
        'email': 'agomez@email.com',
        'direccion': 'Barrio Norte, Manzana 10, Salta',
        'dni': '32456789',
        'condicion_iva': 'Consumidor Final',
    },
    {
        'nombre': 'Sergio Daniel',
        'apellido': 'Martínez',
        'codigo_cliente': 5,
        'telefono': '387-5557890',
        'email': 'smartinez@email.com',
        'direccion': 'Ruta 51 Km 5, Salta',
        'dni': '29876543',
        'cuit': '20-29876543-9',
        'condicion_iva': 'Monotributista',
    }
]

for data in clientes_data:
    cliente, created = Cliente.objects.get_or_create(
        codigo_cliente=data['codigo_cliente'],
        defaults=data
    )
    if created:
        print(f"  ✓ Cliente #{data['codigo_cliente']}: {data['nombre']} {data['apellido']}")

# 7. CREAR VENTAS DE PRUEBA
print("\n7. Creando ventas de prueba...")
from datetime import datetime, timedelta
import random

vendedor = User.objects.get(username='vendedor')
clientes_list = list(Cliente.objects.all())

ventas_data = [
    {
        'fecha_dias_atras': 0,
        'cliente': random.choice(clientes_list),
        'productos': [
            {'producto_codigo': 1, 'cantidad': 2},
            {'producto_codigo': 7, 'cantidad': 1},
        ],
        'tipo_pago': 'efectivo',
    },
    {
        'fecha_dias_atras': 1,
        'cliente': random.choice(clientes_list),
        'productos': [
            {'producto_codigo': 4, 'cantidad': 1},
            {'producto_codigo': 6, 'cantidad': 2},
        ],
        'tipo_pago': 'tarjeta',
    },
    {
        'fecha_dias_atras': 2,
        'cliente': random.choice(clientes_list),
        'productos': [
            {'producto_codigo': 13, 'cantidad': 4},
        ],
        'tipo_pago': 'transferencia',
    },
    {
        'fecha_dias_atras': 3,
        'cliente': None,  # Consumidor final
        'productos': [
            {'producto_codigo': 3, 'cantidad': 1},
            {'producto_codigo': 8, 'cantidad': 1},
        ],
        'tipo_pago': 'efectivo',
    },
]

ultimo_codigo = Venta.objects.order_by('-codigo_venta').first()
codigo_venta = (ultimo_codigo.codigo_venta + 1) if ultimo_codigo else 1000

for i, venta_data in enumerate(ventas_data):
    total = Decimal('0')
    productos_venta = []
    
    # Calcular total y preparar productos
    for prod_data in venta_data['productos']:
        producto = Producto.objects.get(codigo=prod_data['producto_codigo'])
        cantidad = prod_data['cantidad']
        subtotal = producto.precio_venta * cantidad
        total += subtotal
        productos_venta.append({
            'producto': producto,
            'cantidad': cantidad,
            'precio_unitario': producto.precio_venta,
            'subtotal': subtotal
        })
    
    # Crear venta
    fecha_venta = datetime.now() - timedelta(days=venta_data['fecha_dias_atras'])
    
    venta = Venta.objects.create(
        cliente=venta_data['cliente'],
        usuario=vendedor,
        total=total,
        tipo_pago=venta_data['tipo_pago'],
        codigo_venta=codigo_venta + i,
        estado=1,
        estado_venta=2  # Pagado
    )
    venta.fecha = fecha_venta
    venta.save()
    
    # Crear detalles
    for prod in productos_venta:
        DetalleVenta.objects.create(
            venta=venta,
            producto=prod['producto'],
            cantidad=prod['cantidad'],
            precio_unitario=prod['precio_unitario'],
            subtotal=prod['subtotal'],
            status=1
        )
    
    print(f"  ✓ Venta #{venta.codigo_venta} creada - Total: ${total}")

print("\n=== CARGA DE DATOS COMPLETADA ===")
print("\nRESUMEN:")
print(f"  • Roles: {RolUsuario.objects.count()}")
print(f"  • Usuarios: {User.objects.count()}")
print(f"  • Categorías: {Categoria.objects.count()}")
print(f"  • Proveedores: {Proveedor.objects.count()}")
print(f"  • Productos: {Producto.objects.count()}")
print(f"  • Clientes: {Cliente.objects.count()}")
print(f"  • Ventas: {Venta.objects.count()}")

print("\n=== CREDENCIALES DE ACCESO ===")
print("  Admin: admin / admin123")
print("  Vendedor: vendedor / vendedor123")