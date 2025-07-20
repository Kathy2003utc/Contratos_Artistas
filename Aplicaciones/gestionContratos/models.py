from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
import uuid

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
    verificado = models.BooleanField(default=False) 
    bloqueado = models.BooleanField(default=False)
    foto_perfil = models.ImageField(upload_to='usuarios/perfil/', null=True, blank=True)

    # Campos exclusivos para artistas
    portafolio_pdf = models.FileField(upload_to='usuarios/portafolios/', null=True, blank=True)
    facebook_url = models.URLField(max_length=200, null=True, blank=True)
    x_url = models.URLField("X (Twitter)", max_length=200, null=True, blank=True)
    web_url = models.URLField("Página web", max_length=200, null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name='usuarios',
        blank=True,
        help_text='Grupos a los que pertenece el usuario.',
        verbose_name='grupos',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_permisos',
        blank=True,
        help_text='Permisos específicos para el usuario.',
        verbose_name='permisos de usuario',
    )

    def __str__(self):
        return f"{self.username} ({self.rol})"


class Evento(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'Cliente'})
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha = models.DateField()
    ubicacion = models.CharField(max_length=200)

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['fecha']


class Contrato(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    artista = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'Artista'})
    estado = models.CharField(max_length=20, choices=[('Pendiente', 'Pendiente'), ('Aceptado', 'Aceptado'), ('Rechazado', 'Rechazado')], default='Pendiente')
    fecha_contrato = models.DateField(auto_now_add=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pdf = models.FileField(upload_to='contratos/pdfs/', null=True, blank=True)

    observaciones = models.TextField(null=True, blank=True) 


    def __str__(self):
        return f"Contrato de {self.artista.username} para {self.evento.titulo}"

    class Meta:
        ordering = ['-fecha_contrato']


class Mensaje(models.Model):
    emisor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_enviados')
    receptor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"De {self.emisor.username} a {self.receptor.username}"

    class Meta:
        ordering = ['-fecha']


class Reseña(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'Cliente'})
    artista = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='resenas', limit_choices_to={'rol': 'Artista'})
    texto = models.TextField()
    puntuacion = models.IntegerField()
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.cliente.username} a {self.artista.username}"

    class Meta:
        ordering = ['-fecha']


class Pago(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'Cliente'}, related_name='pagos_cliente')
    artista = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'Artista'}, related_name='pagos_artista')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    comprobante_imagen = models.ImageField(upload_to='pagos/comprobantes/', null=True, blank=True)

    def __str__(self):
        return f"Pago de {self.cliente.username} a {self.artista.username} - ${self.monto}"

    class Meta:
        ordering = ['-fecha_pago']

class VerificacionCorreo(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6)
    creado_en = models.DateTimeField(auto_now_add=True)
    expirado = models.BooleanField(default=False)

    def esta_expirado(self):
        return timezone.now() > self.creado_en + timezone.timedelta(minutes=10)  # Código válido por 10 minutos
    
class TerminosCondiciones(models.Model):
    version = models.CharField(max_length=20, unique=True)  # Ej: "v1.0", "2025-07"
    texto = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)  # Nueva línea


    def __str__(self):
        return f"Términos y Condiciones v{self.version} - {'Activo' if self.activo else 'Inactivo'}"

    class Meta:
        ordering = ['-fecha_publicacion']

class RegistroSesion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_login = models.DateTimeField(auto_now_add=True)
    fecha_logout = models.DateTimeField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    exitoso = models.BooleanField(default=True)  # Por si quieres registrar intentos fallidos

    def __str__(self):
        estado = "cerrada" if self.fecha_logout else "abierta"
        return f"Sesión {estado} de {self.usuario.username} - {self.fecha_login.strftime('%Y-%m-%d %H:%M:%S')}"
    
    class Meta:
        ordering = ['-fecha_login']

