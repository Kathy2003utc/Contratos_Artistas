from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('iniciarSesion/', views.iniciarSesion, name='iniciar_sesion'),
    path('logout/', views.cerrarSesion, name='logout'),

    # Cambié views.registro por views.registrarUsuario
    path('registro/', views.registrarUsuario, name='registro'),  
    path('registrarUsuario/', views.registrarUsuario, name='registrar_usuario'),

    path('administrador/', lambda request: render(request, 'administrador/dashboard.html'), name='dashboard_administrador'),
    path('cliente/dashboard/', views.dashboard_cliente, name='dashboard_cliente'),
    path('artista/dashboard/', views.dashboard_artista, name='dashboard_artista'),

    path('perfil/', views.ver_perfil, name='ver_perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/eliminar/', views.eliminar_perfil, name='eliminar_perfil'),

    path('cliente/eventos/', views.listar_eventos, name='listar_eventos'),
    path('cliente/eventos/crear/', views.crear_evento, name='crear_evento'),
    path('cliente/eventos/editar/<int:id>/', views.editar_evento, name='editar_evento'),
    path('cliente/eventos/eliminar/<int:id>/', views.eliminar_evento, name='eliminar_evento'),
]
