from django.db import models
from django.contrib.auth.models import AbstractUser

# Opciones de roles
ROL_CHOICES = (
    ('Cliente', 'Cliente'),
    ('Artista', 'Artista'),
    ('Administrador', 'Administrador'),
)

class Usuario(AbstractUser):
    telefono = models.CharField(max_length=10)
    direccion = models.TextField()
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='Cliente')
    bloqueado = models.BooleanField(default=False)
    foto_perfil = models.ImageField(upload_to='usuarios/perfil/', null=True, blank=True)

    # Campos exclusivos para artistas
    portafolio_pdf = models.FileField(upload_to='usuarios/portafolios/', null=True, blank=True)
    facebook_url = models.URLField(max_length=200, null=True, blank=True)
    x_url = models.URLField("X (Twitter)", max_length=200, null=True, blank=True)
    web_url = models.URLField("Página web", max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.rol})"


