from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente
from .forms import ClienteForm

@login_required
def lista_clientes(request):
    clientes = Cliente.objects.filter(estado=1)
    return render(request, 'clientes/lista_clientes.html', {'clientes': clientes})

@login_required
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'clientes/crear_cliente.html', {'form': form})

@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/editar_cliente.html', {'form': form, 'cliente': cliente})