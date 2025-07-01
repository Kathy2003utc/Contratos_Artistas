from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('iniciarSesion/', views.iniciarSesion, name='iniciar_sesion'),
    path('logout/', views.cerrarSesion, name='logout'),

    path('registro/', views.registro, name='registro'),
    path('registrarUsuario/', views.registrarUsuario, name='registrar_usuario'),

    path('administrador/', lambda request: render(request, 'administrador/dashboard.html'), name='dashboard_administrador'),
    path('cliente/dashboard/', views.dashboard_cliente, name='dashboard_cliente'),
    path('artista/dashboard/', views.dashboard_artista, name='dashboard_artista'),
]
