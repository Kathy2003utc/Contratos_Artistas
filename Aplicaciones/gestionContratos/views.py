from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from .models import Usuario

def login(request):
    return render(request, "login/login.html")

def cerrarSesion(request):
    request.session.flush()
    return redirect('/')

def registro(request):
    return render(request, 'login/registrarUsuario.html')

def iniciarSesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(username=username)

            if check_password(password, usuario.password):
                if usuario.bloqueado:
                    messages.error(request, "Usuario bloqueado.")
                    return render(request, 'login/login.html')

                # Guardar datos en sesión
                request.session['usuario_id'] = usuario.id
                request.session['usuario_rol'] = usuario.rol
                request.session['usuario_username'] = usuario.username

                # Redirección según rol
                if usuario.rol == 'Administrador':
                    return redirect('/administrador')
                elif usuario.rol == 'Cliente':
                    return redirect('dashboard_cliente')
                elif usuario.rol == 'Artista':
                    return redirect('dashboard_artista')
                else:
                    messages.error(request, "Rol desconocido.")
                    return render(request, 'login/login.html')
            else:
                messages.error(request, "Contraseña incorrecta.")
                return render(request, 'login/login.html')

        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
            return render(request, 'login/login.html')

    return render(request, 'login/login.html')

def registrarUsuario(request):
    if request.method == 'POST':
        # ... (igual que antes)
        pass

    return render(request, 'login/registrarUsuario.html')

# --- Nuevas vistas dashboard

def dashboard_cliente(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    
    # Ejemplo de datos que podrías mostrar
    contexto = {
        'usuario': usuario,
        'mensaje': 'Bienvenido al panel del cliente',
        # agrega más datos específicos para cliente aquí
    }
    return render(request, 'cliente/dashboard.html', contexto)


def dashboard_artista(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    
    # Ejemplo de datos para artista
    contexto = {
        'usuario': usuario,
        'mensaje': 'Bienvenido al panel del artista',
        # agrega datos específicos para artista, como portafolio, redes sociales, etc.
    }
    return render(request, 'artista/dashboard.html', contexto)

def ver_perfil(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    return render(request, f"{usuario.rol.lower()}/perfil.html", {'usuario': usuario})

def editar_perfil(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name')
        usuario.last_name = request.POST.get('last_name')
        usuario.email = request.POST.get('email')
        usuario.telefono = request.POST.get('telefono')
        usuario.direccion = request.POST.get('direccion')

        if request.FILES.get('foto_perfil'):
            usuario.foto_perfil = request.FILES.get('foto_perfil')

        usuario.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect('ver_perfil')

    return render(request, f"{usuario.rol.lower()}/editar_perfil.html", {'usuario': usuario})

def eliminar_perfil(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if request.method == 'POST':
        usuario.delete()
        request.session.flush()
        return redirect('login')

    return render(request, f"{usuario.rol.lower()}/eliminar_perfil.html", {'usuario': usuario})
