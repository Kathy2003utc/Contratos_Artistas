from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from .models import Usuario, Evento

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



# Listar eventos del cliente actual
def listar_eventos(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    cliente = Usuario.objects.get(id=usuario_id)
    eventos = Evento.objects.filter(cliente=cliente).order_by('fecha')
    return render(request, 'cliente/eventos/lista_eventos.html', {'eventos': eventos})

# Mostrar formulario para crear evento
def crear_evento(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        fecha = request.POST.get('fecha')
        ubicacion = request.POST.get('ubicacion')

        cliente = Usuario.objects.get(id=usuario_id)
        Evento.objects.create(
            cliente=cliente,
            titulo=titulo,
            descripcion=descripcion,
            fecha=fecha,
            ubicacion=ubicacion
        )
        messages.success(request, "Evento creado exitosamente.")
        return redirect('listar_eventos')

    return render(request, 'cliente/eventos/crear_evento.html')

# Mostrar formulario para editar un evento
def editar_evento(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    evento = get_object_or_404(Evento, id=id, cliente_id=usuario_id)

    if request.method == 'POST':
        evento.titulo = request.POST.get('titulo')
        evento.descripcion = request.POST.get('descripcion')
        evento.fecha = request.POST.get('fecha')
        evento.ubicacion = request.POST.get('ubicacion')
        evento.save()
        messages.success(request, "Evento actualizado correctamente.")
        return redirect('listar_eventos')

    return render(request, 'cliente/eventos/editar_evento.html', {'evento': evento})

# Eliminar evento
def eliminar_evento(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    evento = get_object_or_404(Evento, id=id, cliente_id=usuario_id)
    evento.delete()
    messages.success(request, "Evento eliminado correctamente.")
    return redirect('listar_eventos')

def eventos_artista(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if usuario.rol != 'Artista':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('dashboard_artista')

    eventos = Evento.objects.all()

    return render(request, 'artista/eventos/lista_eventos.html', {'eventos': eventos})
