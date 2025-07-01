from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

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
