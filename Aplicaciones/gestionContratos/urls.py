from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('iniciarSesion/', views.iniciarSesion, name='iniciar_sesion'),
    path('logout/', views.cerrarSesion, name='logout'),

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


]
