from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Producto, Categoria, Proveedor
from .forms import ProductoForm, CategoriaForm, ProveedorForm

# PRODUCTOS
@login_required
def lista_productos(request):
    productos = Producto.objects.filter(estado=1).select_related('categoria', 'proveedor')
    context = {'productos': productos}
    return render(request, 'inventario/lista_productos.html', context)

@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Error al crear el producto. Verifica los datos.')
    else:
        form = ProductoForm()
    return render(request, 'inventario/crear_producto.html', {'form': form})

@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Error al actualizar el producto.')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/editar_producto.html', {'form': form, 'producto': producto})

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
            'categoria': producto.categoria.nombre if producto.categoria else 'Sin categoría',
            'proveedor': producto.proveedor.razon_social if producto.proveedor else 'Sin proveedor',
            'margen_ganancia': round(producto.margen_ganancia, 2),
        }
        return JsonResponse(data)
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

# CATEGORIAS
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
            messages.error(request, 'Error al crear la categoría.')
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

# PROVEEDORES
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
            messages.error(request, 'Error al crear el proveedor.')
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