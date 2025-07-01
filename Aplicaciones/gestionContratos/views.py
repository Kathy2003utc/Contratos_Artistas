from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from .models import Usuario

def login(request):
    return render(request, "login/login.html")

def cerrarSesion(request):
    request.session.flush()
    return redirect('login')

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
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        rol = request.POST.get('rol')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Validar contraseñas
        if password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'login/registrarUsuario.html')
        
        # Validar unicidad username y email
        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe.")
            return render(request, 'login/registrarUsuario.html')
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "El email ya está registrado.")
            return render(request, 'login/registrarUsuario.html')

        usuario = Usuario(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            telefono=telefono,
            direccion=direccion,
            rol=rol,
            password=make_password(password),
        )

        if rol == 'Artista':
            usuario.facebook_url = request.POST.get('facebook_url', '')
            usuario.x_url = request.POST.get('x_url', '')
            usuario.web_url = request.POST.get('web_url', '')
            if 'portafolio_pdf' in request.FILES:
                usuario.portafolio_pdf = request.FILES['portafolio_pdf']

        if 'foto_perfil' in request.FILES:
            usuario.foto_perfil = request.FILES['foto_perfil']

        usuario.save()
        messages.success(request, "Registro exitoso. Ya puedes iniciar sesión.")
        return redirect('login')

    return render(request, 'login/registrarUsuario.html')

def dashboard_cliente(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    
    contexto = {
        'usuario': usuario,
        'mensaje': 'Bienvenido al panel del cliente',
    }
    return render(request, 'cliente/dashboard.html', contexto)

def dashboard_artista(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    
    contexto = {
        'usuario': usuario,
        'mensaje': 'Bienvenido al panel del artista',
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

        # Campos extra para artista
        if usuario.rol == 'Artista':
            usuario.facebook_url = request.POST.get('facebook_url', '')
            usuario.x_url = request.POST.get('x_url', '')
            usuario.web_url = request.POST.get('web_url', '')

            if request.FILES.get('portafolio_pdf'):
                usuario.portafolio_pdf = request.FILES.get('portafolio_pdf')

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
        messages.success(request, "Perfil eliminado correctamente.")
        return redirect('login')

    return render(request, f"{usuario.rol.lower()}/eliminar_perfil.html", {'usuario': usuario})
