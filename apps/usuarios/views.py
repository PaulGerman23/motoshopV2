from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from .models import UsuarioExtendido, RolUsuario, Permiso, RolPermiso
from functools import wraps

# Decorador para verificar permisos
def permiso_requerido(codigo_permiso):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                if hasattr(request.user, 'perfil') and request.user.perfil.tiene_permiso(codigo_permiso):
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'No tienes permisos para acceder a esta sección.')
                    return redirect('dashboard')
            except:
                messages.error(request, 'Error al verificar permisos.')
                return redirect('dashboard')
        return _wrapped_view
    return decorator


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Verificar que el usuario tenga perfil y esté activo
            try:
                if user.perfil.status == 1:
                    login(request, user)
                    messages.success(request, f'Bienvenido {user.first_name}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Tu cuenta está inactiva. Contacta al administrador.')
            except UsuarioExtendido.DoesNotExist:
                messages.error(request, 'Tu cuenta no está configurada correctamente.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'usuarios/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')


@login_required
@permiso_requerido('ver_usuarios')
def lista_usuarios(request):
    usuarios = UsuarioExtendido.objects.filter(status=1).select_related('user', 'rol')
    
    # Obtener estadísticas
    total_usuarios = usuarios.count()
    usuarios_activos = usuarios.filter(user__is_active=True).count()
    
    context = {
        'usuarios': usuarios,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
    }
    return render(request, 'usuarios/lista_usuarios.html', context)


@login_required
@permiso_requerido('crear_usuarios')
def crear_usuario(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Datos del usuario Django
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
                
                # Validar que el username no exista
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'El nombre de usuario ya existe.')
                    return redirect('crear_usuario')
                
                # Validar que el DNI no exista
                if UsuarioExtendido.objects.filter(dni=dni).exists():
                    messages.error(request, 'El DNI ya está registrado.')
                    return redirect('crear_usuario')
                
                # Crear usuario Django
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True
                )
                
                # Crear perfil extendido
                rol = RolUsuario.objects.get(id=rol_id) if rol_id else None
                
                UsuarioExtendido.objects.create(
                    user=user,
                    dni=dni,
                    phone=phone,
                    address=address,
                    rol=rol,
                    status=1
                )
                
                messages.success(request, f'Usuario {username} creado exitosamente.')
                return redirect('lista_usuarios')
                
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            return redirect('crear_usuario')
    
    # GET request
    roles = RolUsuario.objects.all()
    return render(request, 'usuarios/crear_usuario.html', {'roles': roles})


@login_required
@permiso_requerido('editar_usuarios')
def editar_usuario(request, pk):
    usuario_ext = get_object_or_404(UsuarioExtendido, pk=pk)
    user = usuario_ext.user
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Actualizar usuario Django
                user.first_name = request.POST.get('first_name')
                user.last_name = request.POST.get('last_name')
                user.email = request.POST.get('email')
                
                # Cambiar contraseña solo si se proporciona
                new_password = request.POST.get('password')
                if new_password:
                    user.set_password(new_password)
                
                user.save()
                
                # Actualizar perfil extendido
                usuario_ext.dni = request.POST.get('dni')
                usuario_ext.phone = request.POST.get('phone')
                usuario_ext.address = request.POST.get('address')
                
                rol_id = request.POST.get('rol')
                usuario_ext.rol = RolUsuario.objects.get(id=rol_id) if rol_id else None
                
                usuario_ext.save()
                
                messages.success(request, 'Usuario actualizado exitosamente.')
                return redirect('lista_usuarios')
                
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
    
    roles = RolUsuario.objects.all()
    context = {
        'usuario': usuario_ext,
        'roles': roles,
    }
    return render(request, 'usuarios/editar_usuario.html', context)


@login_required
@permiso_requerido('eliminar_usuarios')
def eliminar_usuario(request, pk):
    usuario_ext = get_object_or_404(UsuarioExtendido, pk=pk)
    
    # No permitir eliminar al propio usuario
    if request.user.id == usuario_ext.user.id:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('lista_usuarios')
    
    if request.method == 'POST':
        usuario_ext.status = 0
        usuario_ext.user.is_active = False
        usuario_ext.save()
        usuario_ext.user.save()
        
        messages.success(request, f'Usuario {usuario_ext.user.username} eliminado exitosamente.')
        return redirect('lista_usuarios')
    
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario_ext})


@login_required
@permiso_requerido('ver_usuarios')
def gestionar_permisos_rol(request, rol_id):
    rol = get_object_or_404(RolUsuario, pk=rol_id)
    
    if request.method == 'POST':
        # Obtener permisos seleccionados
        permisos_ids = request.POST.getlist('permisos')
        
        # Eliminar permisos actuales
        RolPermiso.objects.filter(rol=rol).delete()
        
        # Asignar nuevos permisos
        for permiso_id in permisos_ids:
            permiso = Permiso.objects.get(id=permiso_id)
            RolPermiso.objects.create(rol=rol, permiso=permiso)
        
        messages.success(request, f'Permisos del rol {rol} actualizados exitosamente.')
        return redirect('lista_usuarios')
    
    # Agrupar permisos por módulo
    permisos_por_modulo = {}
    for permiso in Permiso.objects.all():
        if permiso.modulo not in permisos_por_modulo:
            permisos_por_modulo[permiso.modulo] = []
        permisos_por_modulo[permiso.modulo].append(permiso)
    
    # Obtener permisos actuales del rol
    permisos_actuales = RolPermiso.objects.filter(rol=rol).values_list('permiso_id', flat=True)
    
    context = {
        'rol': rol,
        'permisos_por_modulo': permisos_por_modulo,
        'permisos_actuales': list(permisos_actuales),
    }
    return render(request, 'usuarios/gestionar_permisos.html', context)


@login_required
def cambiar_password(request):
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual')
        password_nuevo = request.POST.get('password_nuevo')
        password_confirmacion = request.POST.get('password_confirmacion')
        
        # Verificar contraseña actual
        if not request.user.check_password(password_actual):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return redirect('cambiar_password')
        
        # Verificar que las contraseñas coincidan
        if password_nuevo != password_confirmacion:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('cambiar_password')
        
        # Cambiar contraseña
        request.user.set_password(password_nuevo)
        request.user.save()
        
        # Re-autenticar al usuario
        login(request, request.user)
        
        messages.success(request, 'Contraseña cambiada exitosamente.')
        return redirect('dashboard')
    
    return render(request, 'usuarios/cambiar_password.html')