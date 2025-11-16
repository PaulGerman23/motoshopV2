# apps/inventario/views.py - CORREGIDO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models  # ← IMPORTACIÓN AGREGADA
from .models import Producto, Categoria, Proveedor
from .forms import ProductoForm, CategoriaForm, ProveedorForm

@login_required
def lista_productos(request):
    productos = Producto.objects.filter(estado=1).select_related('categoria', 'proveedor')
    
    # Calcular estadísticas
    productos_stock_bajo = productos.filter(stock__lte=models.F('stock_minimo')).count()
    
    context = {
        'productos': productos,
        'productos_stock_bajo': productos_stock_bajo,
    }
    return render(request, 'inventario/lista_productos.html', context)

@login_required
def crear_producto(request):
    if request.method == 'POST':
        # Generar código automático si no viene
        codigo = request.POST.get('codigo')
        if not codigo:
            ultimo_producto = Producto.objects.order_by('-codigo').first()
            codigo = (ultimo_producto.codigo + 1) if ultimo_producto else 1000
        
        try:
            producto = Producto.objects.create(
                codigo=codigo,
                descripcion=request.POST.get('descripcion'),
                precio_costo=request.POST.get('precio_costo'),
                precio_venta=request.POST.get('precio_venta'),
                stock=request.POST.get('stock', 0),
                stock_minimo=request.POST.get('stock_minimo', 5),
                categoria_id=request.POST.get('categoria') if request.POST.get('categoria') else None,
                proveedor_id=request.POST.get('proveedor') if request.POST.get('proveedor') else None,
                estado=request.POST.get('estado', 1)
            )
            messages.success(request, f'Producto #{producto.codigo} creado exitosamente.')
            return redirect('lista_productos')
        except Exception as e:
            messages.error(request, f'Error al crear el producto: {str(e)}')
            return redirect('lista_productos')
    
    # Si es GET, redirigir a la lista (el modal se abre desde ahí)
    return redirect('lista_productos')

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        try:
            producto.codigo = request.POST.get('codigo', producto.codigo)
            producto.descripcion = request.POST.get('descripcion')
            producto.precio_costo = request.POST.get('precio_costo')
            producto.precio_venta = request.POST.get('precio_venta')
            producto.stock = request.POST.get('stock')
            producto.stock_minimo = request.POST.get('stock_minimo', 5)
            producto.estado = request.POST.get('estado', 1)
            
            categoria_id = request.POST.get('categoria')
            producto.categoria_id = categoria_id if categoria_id else None
            
            proveedor_id = request.POST.get('proveedor')
            producto.proveedor_id = proveedor_id if proveedor_id else None
            
            producto.save()
            
            messages.success(request, f'Producto #{producto.codigo} actualizado exitosamente.')
            return redirect('lista_productos')
        except Exception as e:
            messages.error(request, f'Error al actualizar el producto: {str(e)}')
    
    return redirect('lista_productos')

@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        # Eliminación lógica (cambiar estado a 0)
        producto.estado = 0
        producto.save()
        messages.success(request, f'Producto "{producto.descripcion}" eliminado exitosamente.')
        return redirect('lista_productos')
    
    # Si es GET, mostrar página de confirmación
    return render(request, 'inventario/eliminar_producto.html', {'producto': producto})

@login_required
def detalle_producto_json(request, pk):
    """API endpoint para obtener detalles del producto en JSON"""
    try:
        producto = Producto.objects.get(pk=pk, estado=1)
        data = {
            'id': producto.id,
            'codigo': producto.codigo,
            'descripcion': producto.descripcion,
            'precio_costo': str(producto.precio_costo),
            'precio_venta': str(producto.precio_venta),
            'stock': producto.stock,
            'stock_minimo': producto.stock_minimo,
            'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
            'proveedor': producto.proveedor.razon_social if producto.proveedor else 'Sin proveedor',
            'margen_ganancia': round(producto.margen_ganancia, 2),
            'nivel_stock': producto.nivel_stock,
            'tiene_stock_bajo': producto.tiene_stock_bajo,
        }
        return JsonResponse(data)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

@login_required
def obtener_siguiente_codigo(request):
    """API endpoint para obtener el siguiente código disponible"""
    ultimo_producto = Producto.objects.order_by('-codigo').first()
    siguiente_codigo = (ultimo_producto.codigo + 1) if ultimo_producto else 1000
    return JsonResponse({'codigo': siguiente_codigo})

# === VISTAS PARA CATEGORÍAS ===

@login_required
def lista_categorias(request):
    categorias = Categoria.objects.filter(estado=1)
    return render(request, 'inventario/lista_categorias.html', {'categorias': categorias})

@login_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'inventario/crear_categoria.html', {'form': form})

@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'inventario/editar_categoria.html', {'form': form, 'categoria': categoria})

# === VISTAS PARA PROVEEDORES ===

@login_required
def lista_proveedores(request):
    proveedores = Proveedor.objects.filter(estado=1)
    return render(request, 'inventario/lista_proveedores.html', {'proveedores': proveedores})

@login_required
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado exitosamente.')
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'inventario/crear_proveedor.html', {'form': form})

@login_required
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado exitosamente.')
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'inventario/editar_proveedor.html', {'form': form, 'proveedor': proveedor})