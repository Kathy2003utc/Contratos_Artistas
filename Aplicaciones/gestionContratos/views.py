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
                    return redirect('/cliente/dashboard')
                elif usuario.rol == 'Artista':
                    return redirect('/artista/dashboard')
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
        # Comunes
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        rol = request.POST.get('rol')
        foto_perfil = request.FILES.get('foto_perfil')

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'login/registrarUsuario.html')

        # Si es artista, obtener campos adicionales
        portafolio_pdf = request.FILES.get('portafolio_pdf') if rol == 'Artista' else None
        facebook_url = request.POST.get('facebook_url') if rol == 'Artista' else None
        x_url = request.POST.get('x_url') if rol == 'Artista' else None
        web_url = request.POST.get('web_url') if rol == 'Artista' else None

        # Crear usuario
        usuario = Usuario(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            telefono=telefono,
            direccion=direccion,
            rol=rol,
            foto_perfil=foto_perfil,
            password=make_password(password),
            portafolio_pdf=portafolio_pdf,
            facebook_url=facebook_url,
            x_url=x_url,
            web_url=web_url
        )

        usuario.save()
        messages.success(request, "Usuario registrado exitosamente.")
        return redirect('/login')

    return render(request, 'login/registrarUsuario.html')
