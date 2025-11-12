from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UsuarioExtendido, RolUsuario

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {user.first_name}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'usuarios/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')

@login_required
def lista_usuarios(request):
    usuarios = UsuarioExtendido.objects.filter(status=1).select_related('user', 'rol')
    return render(request, 'usuarios/lista_usuarios.html', {'usuarios': usuarios})

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        # Crear usuario Django
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Datos extendidos
        dni = request.POST.get('dni')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        rol_id = request.POST.get('rol')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            rol = RolUsuario.objects.get(id=rol_id) if rol_id else None
            
            UsuarioExtendido.objects.create(
                user=user,
                dni=dni,
                phone=phone,
                address=address,
                rol=rol
            )
            
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('lista_usuarios')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    roles = RolUsuario.objects.all()
    return render(request, 'usuarios/crear_usuario.html', {'roles': roles})