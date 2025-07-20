from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('iniciarSesion/', views.iniciarSesion, name='iniciar_sesion'),
    path('logout/', views.cerrarSesion, name='logout'),

    # Verificacion de correo
    path('verificar-correo/<int:usuario_id>/', views.verificarCorreo, name='verificar_correo'),
    path('reenviar-codigo/<int:usuario_id>/', views.reenviar_codigo, name='reenviar_codigo'),
    

    # Registro
    path('registro/', views.registrarUsuario, name='registro'),  
    path('registrarUsuario/', views.registrarUsuario, name='registrar_usuario'),

    # Dashboards por rol
    path('administrador/', views.dashboard_administrador, name='dashboard_administrador'),
    path('cliente/dashboard/', views.dashboard_cliente, name='dashboard_cliente'),
    path('artista/dashboard/', views.dashboard_artista, name='dashboard_artista'),

    # Perfil
    path('perfil/', views.ver_perfil, name='ver_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/eliminar/', views.eliminar_perfil, name='eliminar_perfil'),

    # Cliente - Eventos
    path('cliente/eventos/', views.listar_eventos, name='listar_eventos'),
    path('cliente/eventos/crear/', views.crear_evento, name='crear_evento'),
    path('cliente/eventos/editar/<int:id>/', views.editar_evento, name='editar_evento'),
    path('cliente/eventos/eliminar/<int:id>/', views.eliminar_evento, name='eliminar_evento'),

    # Artista - Eventos
    path('artista/eventos/', views.eventos_artista, name='eventos_artista'),

    # Admin - Eventos
    path('administrador/eventos/', views.listar_eventos_admin, name='eventos_admin'),

    # Cliente - Contratos
    path('cliente/contratos/', views.listar_contratos_cliente, name='listar_contratos'),
    path('cliente/contratos/crear/', views.crear_contrato_cliente, name='crear_contrato'),
    path('cliente/contratos/editar/<int:id>/', views.editar_contrato_cliente, name='editar_contrato'),
    path('cliente/contratos/eliminar/<int:id>/', views.eliminar_contrato_cliente, name='eliminar_contrato'),

    # Artista - Contratos
    path('artista/contratos/', views.listar_contratos_artista, name='contratos_artista'),
    path('artista/contratos/editar/<int:id>/', views.editar_estado_contrato_artista, name='editar_estado_contrato_artista'),
    path('artista/contratos/accion/<int:id>/', views.accion_contrato_artista, name='accion_contrato_artista'),

    # Cliente - Pagos
    path('cliente/pagos/', views.listar_pagos_cliente, name='listar_pagos'),
    path('cliente/pagos/registrar/', views.registrar_pago, name='registrar_pago'),
    path('pagos/<int:id>/editar/', views.editar_pago, name='editar_pago'),
    path('pagos/<int:id>/eliminar/', views.eliminar_pago, name='eliminar_pago'),

    # Artista - Pagos
    path('artista/pagos/', views.listar_pagos_artista, name='listar_pagos_artista'),


    #Administrador - Registro de sesiones
    path('administrador/sesiones/', views.listar_registros_sesion, name='listar_registros_sesion'),

    # Rutas del calendario
    path('calendario/', views.calendario, name='calendario'),
    path('editarEvento/<int:id>/', views.verEvento, name='ver_evento'),

    #Ruta para ver lista de usuarios como admin
    path('administrador/artistas/', views.listar_artistas, name='listar_artistas'),
    path('administrador/clientes/', views.listar_clientes, name='listar_clientes'),

    #Rutas para CRUD de terminos y condiciones como admin
    path('administrador/terminos_condiciones/', views.listar_terminos_condiciones, name='listar_terminos'),
    path('administrador/terminos_condiciones/crear/', views.crear_terminos_condiciones, name='crear_terminos'),
    path('administrador/terminos_condiciones/editar/<int:id>/', views.editar_terminos_condiciones, name='editar_terminos'),
    path('administrador/terminos_condiciones/eliminar/<int:id>/', views.eliminar_terminos_condiciones, name='eliminar_terminos'),

    # ruta para visuaizar terminos y condiciones como artista y cliente
    path('artista/terminos/', views.listar_terminos_artista, name='listar_terminos_artista'),
    path('cliente/terminos-condiciones/', views.listar_terminos_cliente, name='listar_terminos_cliente'),


    #ruta para ver lista de pagos como administrador
    path('administrador/pagos/', views.listar_pagos_administrador, name='listar_pagos_administrador'),
    #ruta para ver lista de contratos como administrador
    path('administrador/contratos/', views.listar_contratos_administrador, name='listar_contratos_administrador'),


        # ------------------------ MENSAJES ------------------------

    # ADMINISTRADOR - solo puede ver mensajes recibidos
    path('administrador/mensajes/', views.listar_mensajes_admin, name='mensajes_admin'),

    # CLIENTE - puede hacer CRUD de sus mensajes enviados
    path('cliente/mensajes/', views.listar_mensajes_usuario, name='listar_mensajes_cliente'),
    path('cliente/mensajes/nuevo/', views.nuevo_mensaje_usuario, name='nuevo_mensaje_cliente'),
    path('cliente/mensajes/editar/<int:id>/', views.editar_mensaje_usuario, name='editar_mensaje_cliente'),
    path('cliente/mensajes/eliminar/<int:id>/', views.eliminar_mensaje_usuario, name='eliminar_mensaje_cliente'),

    # ARTISTA - puede hacer CRUD de sus mensajes enviados
    path('artista/mensajes/', views.listar_mensajes_usuario, name='listar_mensajes_artista'),
    path('artista/mensajes/nuevo/', views.nuevo_mensaje_usuario, name='nuevo_mensaje_artista'),
    path('artista/mensajes/editar/<int:id>/', views.editar_mensaje_usuario, name='editar_mensaje_artista'),
    path('artista/mensajes/eliminar/<int:id>/', views.eliminar_mensaje_usuario, name='eliminar_mensaje_artista'),


]
