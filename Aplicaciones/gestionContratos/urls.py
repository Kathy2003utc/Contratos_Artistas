from django.urls import path
from . import views
from django.shortcuts import render


urlpatterns = [

    path('', views.login, name='login'),                    # Página principal de login
    path('login/', views.login, name='login'),
    path('iniciarSesion/', views.iniciarSesion, name='iniciar_sesion'),
    path('logout/', views.cerrarSesion, name='logout'),

    path('registro/', views.registro, name='registro'),
    path('registrarUsuario/', views.registrarUsuario, name='registrar_usuario'),

    path('administrador/', lambda request: render(request, 'administrador/dashboard.html'), name='dashboard_administrador'),
    path('cliente/dashboard/', lambda request: render(request, 'cliente/dashboard.html'), name='dashboard_cliente'),
    path('artista/dashboard/', lambda request: render(request, 'artista/dashboard.html'), name='dashboard_artista'),
]
