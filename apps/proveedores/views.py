from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.inventario.models import Proveedor
from apps.inventario.forms import ProveedorForm

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