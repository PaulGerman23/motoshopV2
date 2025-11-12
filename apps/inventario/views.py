from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/editar_producto.html', {'form': form, 'producto': producto})

@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.estado = 0
        producto.save()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('lista_productos')
    return render(request, 'inventario/eliminar_producto.html', {'producto': producto})

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
        form = CategoriaForm()
    return render(request, 'inventario/crear_categoria.html', {'form': form})

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
        form = ProveedorForm()
    return render(request, 'inventario/crear_proveedor.html', {'form': form})