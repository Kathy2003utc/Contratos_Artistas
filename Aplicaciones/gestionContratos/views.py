from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from .models import Usuario, Evento, Contrato, Pago, RegistroSesion
from .models import VerificacionCorreo, TerminosCondiciones
from django.core.mail import send_mail
import random
from django.conf import settings
from django.utils import timezone
import json
from django.contrib.auth.decorators import login_required
from Aplicaciones.gestionContratos.models import Usuario, Mensaje, Reseña


# ------------------------ LOGIN ------------------------

def login(request):
    return render(request, "login/login.html")

def cerrarSesion(request):
    registro_sesion_id = request.session.get('registro_sesion_id')
    if registro_sesion_id:
        try:
            registro = RegistroSesion.objects.get(id=registro_sesion_id)
            registro.fecha_logout = timezone.now()
            registro.save()
        except RegistroSesion.DoesNotExist:
            pass

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

                if not usuario.verificado:
                    messages.error(request, "Debes verificar tu correo antes de iniciar sesión.")
                    return render(request, 'login/login.html')

                # Registrar inicio de sesión
                user_agent = request.META.get('HTTP_USER_AGENT', '')  # Obtener user agent
                registro_sesion = RegistroSesion.objects.create(
                    usuario=usuario,
                    user_agent=user_agent,
                    exitoso=True
                )
                
                # Guardar id del registro en sesión para usarlo en logout
                request.session['registro_sesion_id'] = registro_sesion.id

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


def generar_codigo():
    return str(random.randint(100000, 999999))

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

        # Crear código de verificación
        codigo = generar_codigo()
        VerificacionCorreo.objects.create(usuario=usuario, codigo=codigo)

        # Enviar correo
        send_mail(
            subject='Verifica tu correo',
            message=f'Tu código de verificación es: {codigo}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[usuario.email],
            fail_silently=False,
        )

        try:
            send_mail(
                subject='Verifica tu correo',
                message=f'Tu código de verificación es: {codigo}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
        except Exception as e:
            print("Error enviando correo:", e)  # Esto se verá en la consola
            messages.error(request, "No se pudo enviar el correo de verificación.")
            return render(request, 'login/registrarUsuario.html')  # Muestra de nuevo el formulario

        return redirect('verificar_correo', usuario_id=usuario.id)

    return render(request, 'login/registrarUsuario.html')


def verificarCorreo(request, usuario_id):
    usuario = Usuario.objects.get(id=usuario_id)

    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        try:
            verificacion = VerificacionCorreo.objects.filter(usuario=usuario, expirado=False).latest('creado_en')
            if verificacion.codigo == codigo:
                if verificacion.esta_expirado():
                    messages.error(request, "El código ha expirado.")
                else:
                    usuario.verificado = True
                    usuario.save()
                    verificacion.expirado = True
                    verificacion.save()
                    messages.success(request, "Correo verificado con éxito.")
                    return redirect('login')
            else:
                messages.error(request, "Código incorrecto.")
        except VerificacionCorreo.DoesNotExist:
            messages.error(request, "No se encontró un código válido.")

    return render(request, 'login/verificar_correo.html', {'usuario': usuario})

def reenviar_codigo(request, usuario_id):
    usuario = Usuario.objects.get(id=usuario_id)
    codigo = generar_codigo()
    VerificacionCorreo.objects.create(usuario=usuario, codigo=codigo)

    send_mail(
        subject='Nuevo código de verificación',
        message=f'Tu nuevo código es: {codigo}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[usuario.email],
        fail_silently=False,
    )

    messages.success(request, "Nuevo código enviado.")
    return redirect('verificar_correo', usuario_id=usuario.id)


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

def dashboard_administrador(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if usuario.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder al panel de administrador.")
        return redirect('login')

    # Conteos para mostrar datos reales
    total_usuarios = Usuario.objects.count()
    total_eventos = Evento.objects.count()
    total_contratos = Contrato.objects.count()

    contexto = {
        'usuario': usuario,
        'mensaje': 'Bienvenido al panel del administrador',
        'total_usuarios': total_usuarios,
        'total_eventos': total_eventos,
        'total_contratos': total_contratos,
    }
    return render(request, 'administrador/dashboard.html', contexto)

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


# ------------------------ LISTA DE EVENTOS EN CLIENTES ------------------------

# Listar eventos del cliente actual
def listar_eventos(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    cliente = Usuario.objects.get(id=usuario_id)
    eventos = Evento.objects.filter(cliente=cliente).order_by('id')
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

    # Verificar si hay contratos aceptados asociados al evento
    contratos_aceptados = Contrato.objects.filter(evento=evento, estado='Aceptado')

    if contratos_aceptados.exists():
        messages.error(request, "No puedes eliminar este evento porque tiene un contrato aceptado.")
        return redirect('listar_eventos')

    evento.delete()
    messages.success(request, "Evento eliminado correctamente.")
    return redirect('listar_eventos')

# Visualizacion de eventos para artista
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

# Visualizacion de eventos para admin
def listar_eventos_admin(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if usuario.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    eventos = Evento.objects.all().order_by('id')

    return render(request, 'administrador/eventos/lista_eventos.html', {
        'usuario': usuario,
        'eventos': eventos,
    })


def listar_contratos_cliente(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    cliente = get_object_or_404(Usuario, id=usuario_id, rol='Cliente')
    contratos = Contrato.objects.filter(evento__cliente=cliente).order_by('id')

    return render(request, 'cliente/contratos/lista_contratos.html', {
        'usuario': cliente,
        'contratos': contratos
    })

def crear_contrato_cliente(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    cliente = get_object_or_404(Usuario, id=usuario_id, rol='Cliente')

    if request.method == 'POST':
        evento_id        = request.POST.get('evento')
        artista_id       = request.POST.get('artista')
        fecha_inicio     = request.POST.get('fecha_inicio')  or None
        fecha_fin        = request.POST.get('fecha_fin')     or None
        costo            = request.POST.get('costo')         or None
        pdf = request.FILES.get('pdf')
        observaciones    = request.POST.get('observaciones')

        evento  = get_object_or_404(Evento, id=evento_id,  cliente=cliente)
        artista = get_object_or_404(Usuario, id=artista_id, rol='Artista')

        Contrato.objects.create(
            evento         = evento,
            artista        = artista,
            estado         = 'Pendiente',
            fecha_inicio   = fecha_inicio,
            fecha_fin      = fecha_fin,
            costo          = costo if costo not in ('', None) else None,
            pdf=pdf,
            observaciones  = observaciones
        )
        messages.success(request, "Contrato creado exitosamente.")
        return redirect('listar_contratos')

    eventos  = Evento.objects.filter(cliente=cliente)
    artistas = Usuario.objects.filter(rol='Artista')

    return render(request, 'cliente/contratos/crear_contrato.html', {
        'eventos': eventos,
        'artistas': artistas
    })

def editar_contrato_cliente(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    cliente  = get_object_or_404(Usuario, id=usuario_id, rol='Cliente')
    contrato = get_object_or_404(Contrato, id=id, evento__cliente=cliente)

    if contrato.estado == 'Aceptado':
        messages.error(request, "No puedes editar un contrato que ya fue aceptado por el artista.")
        return redirect('listar_contratos')

    if request.method == 'POST':
        evento_id     = request.POST.get('evento')
        artista_id    = request.POST.get('artista')
        fecha_inicio  = request.POST.get('fecha_inicio')  or None
        fecha_fin     = request.POST.get('fecha_fin')     or None
        costo         = request.POST.get('costo')         or None
        observaciones = request.POST.get('observaciones')

        contrato.evento        = get_object_or_404(Evento, id=evento_id,  cliente=cliente)
        contrato.artista       = get_object_or_404(Usuario, id=artista_id, rol='Artista')
        contrato.fecha_inicio  = fecha_inicio
        contrato.fecha_fin     = fecha_fin
        contrato.costo         = costo if costo not in ('', None) else None
        contrato.observaciones = observaciones
        contrato.save()

        messages.success(request, "Contrato actualizado correctamente.")
        return redirect('listar_contratos')

    eventos  = Evento.objects.filter(cliente=cliente)
    artistas = Usuario.objects.filter(rol='Artista')

    return render(request, 'cliente/contratos/editar_contrato.html', {
        'contrato': contrato,
        'eventos': eventos,
        'artistas': artistas
    })

def eliminar_contrato_cliente(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    cliente = get_object_or_404(Usuario, id=usuario_id, rol='Cliente')
    contrato = get_object_or_404(Contrato, id=id, evento__cliente=cliente)

    # Bloquear eliminación si contrato aceptado
    if contrato.estado == 'Aceptado':
        messages.error(request, "No puedes eliminar un contrato que ya fue aceptado por el artista.")
        return redirect('listar_contratos')

    if request.method == 'POST':
        contrato.delete()
        messages.success(request, "Contrato eliminado correctamente.")
        return redirect('listar_contratos')
    else:
        messages.error(request, "Método no permitido para eliminar contrato.")
        return redirect('listar_contratos')


# Visualizacion de contratos para artista
def listar_contratos_artista(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    artista = get_object_or_404(Usuario, id=usuario_id, rol='Artista')
    contratos = Contrato.objects.filter(artista=artista).order_by('id')

    return render(request, 'artista/contratos/lista_contratos.html', {
        'usuario': artista,
        'contratos': contratos,
    })

# editar el estado de un contrato para artista
def editar_estado_contrato_artista(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    artista = get_object_or_404(Usuario, id=usuario_id, rol='Artista')
    contrato = get_object_or_404(Contrato, id=id, artista=artista)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in ['Pendiente', 'Aceptado', 'Rechazado']:
            contrato.estado = nuevo_estado
            contrato.save()
            messages.success(request, "Estado del contrato actualizado correctamente.")
            return redirect('contratos_artista')  # Ajusta la url según tus urls.py
        else:
            messages.error(request, "Estado inválido.")

    return render(request, 'artista/contratos/editar_contrato.html', {
        'usuario': artista,
        'contrato': contrato
    })

# aceptar o rechazar un contrato para artista
def accion_contrato_artista(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    artista = get_object_or_404(Usuario, id=usuario_id, rol='Artista')
    contrato = get_object_or_404(Contrato, id=id, artista=artista)

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'aceptar':
            contrato.estado = 'Aceptado'
        elif accion == 'rechazar':
            contrato.estado = 'Rechazado'
        else:
            messages.error(request, "Acción no válida.")
            return redirect('contratos_artista')

        contrato.save()
        messages.success(request, f"Contrato {accion}do exitosamente.")
        return redirect('contratos_artista')

    return redirect('contratos_artista')


def registrar_pago(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    cliente = get_object_or_404(Usuario, id=usuario_id, rol='Cliente')
    contratos_aceptados = Contrato.objects.filter(evento__cliente=cliente, estado='Aceptado')

    if request.method == 'POST':
        contrato_id  = request.POST.get('contrato')
        comprobante  = request.FILES.get('comprobante_imagen')

        # El monto llega readonly, pero por seguridad tomamos el costo directamente del contrato
        contrato = get_object_or_404(Contrato, id=contrato_id, evento__cliente=cliente, estado='Aceptado')
        monto    = contrato.costo  # ignoramos el valor manipulado en el POST

        if not comprobante:
            messages.error(request, "El comprobante es obligatorio.")
            return redirect('registrar_pago')

        Pago.objects.create(
            contrato            = contrato,
            cliente             = cliente,
            artista             = contrato.artista,
            monto               = monto,
            comprobante_imagen  = comprobante
        )
        messages.success(request, "Pago registrado exitosamente.")
        return redirect('listar_pagos')

    return render(request, 'cliente/pagos/registrar_pago.html', {
        'contratos': contratos_aceptados
    })


def listar_pagos_cliente(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    cliente = get_object_or_404(Usuario, id=usuario_id, rol='Cliente')
    pagos = Pago.objects.filter(cliente=cliente).order_by('-fecha_pago')

    return render(request, 'cliente/pagos/lista_pagos.html', {
        'pagos': pagos
    })

def editar_pago(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    pago = get_object_or_404(Pago, id=id, cliente_id=usuario_id)
    contratos_aceptados = Contrato.objects.filter(evento__cliente_id=usuario_id, estado='Aceptado')

    if request.method == 'POST':
        contrato_id = request.POST.get('contrato')
        contrato = get_object_or_404(Contrato, id=contrato_id, evento__cliente_id=usuario_id, estado='Aceptado')

        # Actualiza campos
        pago.contrato = contrato
        pago.artista = contrato.artista
        pago.monto = contrato.costo

        if 'comprobante_imagen' in request.FILES:
            pago.comprobante_imagen = request.FILES['comprobante_imagen']

        pago.save()
        messages.success(request, "Pago actualizado correctamente.")
        return redirect('listar_pagos')

    return render(request, 'cliente/pagos/editar_pago.html', {
        'pago': pago,
        'contratos': contratos_aceptados
    })

def eliminar_pago(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    pago = get_object_or_404(Pago, id=id, cliente_id=usuario_id)

    if request.method == 'POST':
        pago.delete()
        messages.success(request, "Pago eliminado correctamente.")
        return redirect('listar_pagos')

    messages.error(request, "Acción no permitida.")
    return redirect('listar_pagos')

#vizualizar pagos como artista
def listar_pagos_artista(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    artista = get_object_or_404(Usuario, id=usuario_id, rol='Artista')
    # Filtrar pagos donde el artista es el usuario logueado
    pagos = Pago.objects.filter(artista=artista).order_by('-fecha_pago')

    return render(request, 'artista/pagos/lista_pagos.html', {
        'pagos': pagos
    })


# visualizacion del registro de sesiones de usuario para administrador
def listar_registros_sesion(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if usuario.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    registros = RegistroSesion.objects.select_related('usuario').order_by('id')

    return render(request, 'administrador/sesiones/lista_sesiones.html', {
        'registros': registros
    })

# visualizacion de calendario para administrador
def calendario(request):
    contratos = Contrato.objects.select_related('evento', 'artista', 'evento__cliente').all()
    eventos_list = []

    for contrato in contratos:
        eventos_list.append({
            'id': contrato.evento.id,
            'title': f"{contrato.evento.titulo} - Cliente: {contrato.evento.cliente.username} - Artista: {contrato.artista.username}",
            'start': contrato.evento.fecha.isoformat(),
        })

    return render(request, "administrador/calendario/calendario.html", {'temas_json': json.dumps(eventos_list)})

#visualizacion del evento registrado en el calendario
def verEvento(request, id):
    evento = get_object_or_404(Evento, id=id)
    contratos = Contrato.objects.filter(evento=evento) 
    artistas = Usuario.objects.filter(rol='Artista')
    clientes = Usuario.objects.filter(rol='Cliente')

    if request.method == 'POST':
        evento.cliente_id = request.POST.get('cliente')
        evento.titulo = request.POST.get('titulo')
        evento.descripcion = request.POST.get('descripcion')
        evento.fecha = request.POST.get('fecha')
        evento.ubicacion = request.POST.get('ubicacion')
        evento.save()

        return redirect('calendario')

    return render(request, "administrador/calendario/verEvento.html", {
        'evento': evento,
        'contratos': contratos,
        'artistas': artistas,
        'clientes': clientes
    })


# visualizacion del listado de artistas para Administrador
def listar_artistas(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    artistas = Usuario.objects.filter(rol='Artista')

    return render(request, 'administrador/usuarios/lista_artistas.html', {
        'usuario': usuario,
        'artistas': artistas
    })

# visualizacion del listado de clientes para Administrador
def listar_clientes(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    clientes = Usuario.objects.filter(rol='Cliente')

    return render(request, 'administrador/usuarios/lista_clientes.html', {
        'usuario': usuario,
        'clientes': clientes
    })

# visualizar la tabla de terminos y condiciones
def listar_terminos_condiciones(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    terminos = TerminosCondiciones.objects.order_by('fecha_publicacion')

    return render(request, 'administrador/terminos_condiciones/lista_terminos.html', {
        'usuario': usuario,
        'terminos': terminos,
    })

# Crear un termino o condicion por el administrador
def crear_terminos_condiciones(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    if request.method == 'POST':
        version = request.POST.get('version')
        texto = request.POST.get('texto')

        # Validar que no exista la versión repetida (tu modelo tiene unique=True en version)
        if TerminosCondiciones.objects.filter(version=version).exists():
            messages.error(request, f"La versión {version} ya existe.")
            return render(request, 'administrador/terminos_condiciones/crear_terminos.html')

        TerminosCondiciones.objects.create(
            version=version,
            texto=texto
        )
        messages.success(request, "Términos y Condiciones creado exitosamente.")
        return redirect('listar_terminos')

    return render(request, 'administrador/terminos_condiciones/crear_terminos.html')

# Editar un termino o condicion por el administrador
def editar_terminos_condiciones(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    termino = get_object_or_404(TerminosCondiciones, id=id)

    if request.method == 'POST':
        version = request.POST.get('version')
        texto = request.POST.get('texto')

        # Validar que la nueva versión no exista en otro registro
        if TerminosCondiciones.objects.filter(version=version).exclude(id=termino.id).exists():
            messages.error(request, f"La versión {version} ya existe.")
            return render(request, 'administrador/terminos_condiciones/editar_terminos.html', {'termino': termino})

        termino.version = version
        termino.texto = texto
        termino.fecha_modificacion = timezone.now()  #Aquí se guarda la fecha y hora de edición
        termino.save()

        messages.success(request, "Términos y Condiciones actualizado exitosamente.")
        return redirect('listar_terminos')

    return render(request, 'administrador/terminos_condiciones/editar_terminos.html', {'termino': termino})

# Eliminar un termino o condicion por el administrador
def eliminar_terminos_condiciones(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol != 'Administrador':
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('login')

    termino = get_object_or_404(TerminosCondiciones, id=id)

    termino.delete()
    messages.success(request, "Términos y Condiciones eliminado correctamente.")
    return redirect('listar_terminos')

# visualizar los terminos o condiciones por el artista
def listar_terminos_artista(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol != 'Artista':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    terminos = TerminosCondiciones.objects.order_by('fecha_publicacion')

    return render(request, 'artista/terminos_condiciones/lista_terminos.html', {
        'usuario': usuario,
        'terminos': terminos,
    })

# visualizar los terminos o condiciones por el cliente
def listar_terminos_cliente(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol != 'Cliente':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    terminos = TerminosCondiciones.objects.order_by('fecha_publicacion')

    return render(request, 'cliente/terminos_condiciones/lista_terminos.html', {
        'usuario': usuario,
        'terminos': terminos,
    })


# visualizar los pagos como administrador
def listar_pagos_administrador(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    admin = Usuario.objects.get(id=usuario_id)
    if admin.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    pagos = Pago.objects.select_related('cliente', 'artista', 'contrato').all().order_by('-fecha_pago')

    return render(request, 'administrador/pagos/lista_pagos.html', {
        'pagos': pagos,
        'admin': admin,
    })


def listar_contratos_administrador(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    contratos = Contrato.objects.select_related('evento', 'artista').order_by('id')

    return render(request, 'administrador/contratos/lista_contratos.html', {
        'usuario': usuario,
        'contratos': contratos,
    })


# ------------------------ MENSAJES ------------------------

# --- ADMINISTRADOR ---

def listar_mensajes_admin(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    admin = Usuario.objects.get(id=usuario_id)
    if admin.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    mensajes = Mensaje.objects.filter(receptor=admin).select_related('emisor').order_by('-fecha')

    return render(request, 'administrador/mensajes/lista_mensajes.html', {
        'usuario': admin,
        'mensajes': mensajes
    })


# --- CLIENTE / ARTISTA ---

def listar_mensajes_usuario(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol not in ['Cliente', 'Artista']:
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    mensajes = Mensaje.objects.filter(emisor=usuario).select_related('receptor').order_by('-fecha')

    if usuario.rol == 'Cliente':
        template = 'cliente/mensajes/lista_mensajes.html'
    else:
        template = 'artista/mensajes/lista_mensajes.html'

    return render(request, template, {
        'usuario': usuario,
        'mensajes': mensajes
    })


def nuevo_mensaje_usuario(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol not in ['Cliente', 'Artista']:
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    if request.method == 'POST':
        texto = request.POST.get('texto')

        # Buscar al administrador como receptor
        admin = Usuario.objects.filter(rol='Administrador').first()
        if not admin:
            messages.error(request, "No se encontró un administrador receptor.")
            if usuario.rol == 'Cliente':
                return redirect('cliente_listar_mensajes')
            else:
                return redirect('artista_listar_mensajes')

        Mensaje.objects.create(
            emisor=usuario,
            receptor=admin,
            texto=texto
        )
        messages.success(request, "Mensaje enviado correctamente.")
        if usuario.rol == 'Cliente':
            return redirect('cliente_listar_mensajes')
        else:
            return redirect('artista_listar_mensajes')

    if usuario.rol == 'Cliente':
        template = 'cliente/mensajes/nuevo_mensaje.html'
    else:
        template = 'artista/mensajes/nuevo_mensaje.html'
    return render(request, template, {'usuario': usuario})


def editar_mensaje_usuario(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    usuario = Usuario.objects.get(id=usuario_id)
    mensaje = get_object_or_404(Mensaje, id=id, emisor=usuario)

    if usuario.rol not in ['Cliente', 'Artista']:
        messages.error(request, "No tienes permisos para editar este mensaje.")
        return redirect('login')

    if request.method == 'POST':
        texto = request.POST.get('texto')
        mensaje.texto = texto
        mensaje.save()

        messages.success(request, "Mensaje actualizado correctamente.")
        if usuario.rol == 'Cliente':
            return redirect('cliente_listar_mensajes')
        else:
            return redirect('artista_listar_mensajes')

    if usuario.rol == 'Cliente':
        template = 'cliente/mensajes/editar_mensaje.html'
    else:
        template = 'artista/mensajes/editar_mensaje.html'
    return render(request, template, {'usuario': usuario, 'mensaje': mensaje})


def eliminar_mensaje_usuario(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    usuario = Usuario.objects.get(id=usuario_id)
    mensaje = get_object_or_404(Mensaje, id=id, emisor=usuario)

    if usuario.rol not in ['Cliente', 'Artista']:
        messages.error(request, "No tienes permisos para eliminar este mensaje.")
        return redirect('login')

    if request.method == 'POST':  # Se recomienda usar POST para eliminar
        mensaje.delete()
        messages.success(request, "Mensaje eliminado correctamente.")
    else:
        messages.error(request, "Solicitud inválida para eliminar mensaje.")

    if usuario.rol == 'Cliente':
        return redirect('cliente_listar_mensajes')
    else:
        return redirect('artista_listar_mensajes')
    

# ------------------------ RESEÑAS ------------------------

# --- ADMINISTRADOR ---
def listar_resenas_admin(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    admin = Usuario.objects.get(id=usuario_id)
    if admin.rol != 'Administrador':
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    resenas = Reseña.objects.select_related('cliente', 'artista').all()

    return render(request, 'administrador/resenas/lista_resenas.html', {
        'usuario': admin,
        'resenas': resenas
    })


def eliminar_resena_admin(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    admin = Usuario.objects.get(id=usuario_id)
    if admin.rol != 'Administrador':
        messages.error(request, "No tienes permisos para eliminar reseñas.")
        return redirect('login')

    resena = get_object_or_404(Reseña, id=id)

    if request.method == 'POST':
        resena.delete()
        messages.success(request, "Reseña eliminada correctamente.")
        return redirect('admin_listar_resenas')

    messages.error(request, "Solicitud inválida para eliminar reseña.")
    return redirect('admin_listar_resenas')


# --- CLIENTE / ARTISTA ---
def listar_resenas_usuario(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol not in ['Cliente', 'Artista']:
        messages.error(request, "No tienes permisos para acceder a esta sección.")
        return redirect('login')

    if usuario.rol == 'Cliente':
        resenas = Reseña.objects.filter(cliente=usuario).select_related('artista').order_by('-fecha')
        template = 'cliente/resenas/lista_resenas.html'
    else:
        resenas = Reseña.objects.filter(artista=usuario).select_related('cliente').order_by('-fecha')
        template = 'artista/resenas/lista_resenas.html'

    return render(request, template, {
        'usuario': usuario,
        'resenas': resenas
    })


def nueva_resena_usuario(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    if usuario.rol not in ['Cliente', 'Artista']:
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('login')

    if request.method == 'POST':
        texto = request.POST.get('texto')
        puntuacion = request.POST.get('puntuacion')
        artista_id = request.POST.get('artista')

        try:
            artista = Usuario.objects.get(id=artista_id, rol='Artista')
        except Usuario.DoesNotExist:
            messages.error(request, "Artista no encontrado.")
            return redirect('cliente_listar_resenas' if usuario.rol == 'Cliente' else 'artista_listar_resenas')

        # Solo Cliente puede crear reseñas
        if usuario.rol != 'Cliente':
            messages.error(request, "Solo clientes pueden crear reseñas.")
            return redirect('login')

        Reseña.objects.create(
            cliente=usuario,
            artista=artista,
            texto=texto,
            puntuacion=int(puntuacion)
        )
        messages.success(request, "Reseña creada correctamente.")
        if usuario.rol == 'Cliente':
            return redirect('cliente_listar_resenas')
        else:
            return redirect('artista_listar_resenas')

    # Mostrar formulario (puedes pasar lista de artistas para elegir)
    artistas = Usuario.objects.filter(rol='Artista')
    if usuario.rol == 'Cliente':
        template = 'cliente/resenas/nueva_resena.html'
    else:
        template = 'artista/resenas/nueva_resena.html'

    return render(request, template, {
        'usuario': usuario,
        'artistas': artistas
    })


def editar_resena_usuario(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    resena = get_object_or_404(Reseña, id=id)

    # Solo el cliente que la creó puede editar
    if resena.cliente != usuario:
        messages.error(request, "No tienes permisos para editar esta reseña.")
        return redirect('login')

    if request.method == 'POST':
        texto = request.POST.get('texto')
        puntuacion = request.POST.get('puntuacion')

        resena.texto = texto
        resena.puntuacion = int(puntuacion)
        resena.save()

        messages.success(request, "Reseña actualizada correctamente.")
        if usuario.rol == 'Cliente':
            return redirect('cliente_listar_resenas')
        else:
            return redirect('artista_listar_resenas')

    if usuario.rol == 'Cliente':
        template = 'cliente/resenas/editar_resena.html'
    else:
        template = 'artista/resenas/editar_resena.html'

    return render(request, template, {
        'usuario': usuario,
        'resena': resena
    })


def eliminar_resena_usuario(request, id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)
    resena = get_object_or_404(Reseña, id=id)

    # Solo cliente que creó la reseña puede eliminarla
    if resena.cliente != usuario:
        messages.error(request, "No tienes permisos para eliminar esta reseña.")
        return redirect('login')

    if request.method == 'POST':
        resena.delete()
        messages.success(request, "Reseña eliminada correctamente.")
        if usuario.rol == 'Cliente':
            return redirect('cliente_listar_resenas')
        else:
            return redirect('artista_listar_resenas')

    messages.error(request, "Solicitud inválida para eliminar reseña.")
    if usuario.rol == 'Cliente':
        return redirect('cliente_listar_resenas')
    else:
        return redirect('artista_listar_resenas')


# ------------------------ DASHBOARD ------------------------

def resumen_mensajes_admin(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    admin = Usuario.objects.get(id=usuario_id)
    if admin.rol != 'Administrador':
        messages.error(request, "No tienes permisos para esta sección.")
        return redirect('login')

    # Cantidad de mensajes enviados por clientes y artistas
    total_mensajes_clientes = Mensaje.objects.filter(emisor__rol='Cliente').count()
    total_mensajes_artistas = Mensaje.objects.filter(emisor__rol='Artista').count()

    # Total de usuarios registrados por rol
    total_usuarios_clientes = Usuario.objects.filter(rol='Cliente').count()
    total_usuarios_artistas = Usuario.objects.filter(rol='Artista').count()

    # Conteo de contratos por estado
    contratos_aceptados = Contrato.objects.filter(estado='Aceptado').count()
    contratos_rechazados = Contrato.objects.filter(estado='Rechazado').count()
    contratos_pendientes = Contrato.objects.filter(estado='Pendiente').count()

    return render(request, 'administrador/presentacion/resumen_mensajes.html', {
        'usuario': admin,
        'total_mensajes_clientes': total_mensajes_clientes,
        'total_mensajes_artistas': total_mensajes_artistas,
        'total_usuarios_clientes': total_usuarios_clientes,
        'total_usuarios_artistas': total_usuarios_artistas,
        'contratos_aceptados': contratos_aceptados,
        'contratos_rechazados': contratos_rechazados,
        'contratos_pendientes': contratos_pendientes,
    })
