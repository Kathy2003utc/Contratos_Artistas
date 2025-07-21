from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from Aplicaciones.gestionContratos.models import Usuario, Evento, Contrato

class EventoModelTest(TestCase):

    def setUp(self):
        self.cliente = Usuario.objects.create(
            username='cliente1',
            rol='Cliente',
            password='12345',  # si usas create_user, mejor para hashing
            telefono='0987654321',
            direccion='Direccion cliente',
        )

    def test_crear_evento(self):
        evento = Evento.objects.create(
            cliente=self.cliente,
            titulo='Evento Test',
            descripcion='Descripción del evento',
            fecha=timezone.now().date(),
            ubicacion='Quito'
        )
        self.assertEqual(str(evento), 'Evento Test')
        self.assertEqual(evento.cliente, self.cliente)
        self.assertEqual(evento.titulo, 'Evento Test')

    def test_ordenamiento_por_fecha(self):
        evento1 = Evento.objects.create(
            cliente=self.cliente,
            titulo='Evento 1',
            descripcion='Desc 1',
            fecha=timezone.now().date(),
            ubicacion='Lugar 1'
        )
        evento2 = Evento.objects.create(
            cliente=self.cliente,
            titulo='Evento 2',
            descripcion='Desc 2',
            fecha=timezone.now().date() + timezone.timedelta(days=1),
            ubicacion='Lugar 2'
        )
        eventos = Evento.objects.all()
        self.assertEqual(eventos[0], evento1)
        self.assertEqual(eventos[1], evento2)


class EventoViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(
            username='cliente1',
            rol='Cliente',
            password='12345',
            telefono='0987654321',
            direccion='Direccion cliente',
        )
        session = self.client.session
        session['usuario_id'] = self.usuario.id
        session.save()

        self.evento = Evento.objects.create(
            cliente=self.usuario,
            titulo='Evento prueba',
            descripcion='Descripción',
            fecha=timezone.now().date(),
            ubicacion='Quito'
        )

        # Crear un usuario artista para pruebas
        self.artista = Usuario.objects.create(
            username='artista1',
            rol='Artista',
            password='12345',
            telefono='1234567890',
            direccion='Direccion artista',
        )

    def test_listar_eventos_sin_login(self):
        self.client.session.flush()
        response = self.client.get(reverse('listar_eventos'))
        self.assertRedirects(response, reverse('login'))

    def test_listar_eventos_con_login(self):
        response = self.client.get(reverse('listar_eventos'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.evento, response.context['eventos'])

    def test_crear_evento_get(self):
        response = self.client.get(reverse('crear_evento'))
        self.assertEqual(response.status_code, 200)

    def test_crear_evento_post(self):
        datos = {
            'titulo': 'Nuevo Evento',
            'descripcion': 'Desc evento',
            'fecha': timezone.now().date().isoformat(),
            'ubicacion': 'Guayaquil',
        }
        response = self.client.post(reverse('crear_evento'), datos)
        self.assertRedirects(response, reverse('listar_eventos'))
        self.assertTrue(Evento.objects.filter(titulo='Nuevo Evento').exists())

    def test_editar_evento_get(self):
        url = reverse('editar_evento', kwargs={'id': self.evento.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['evento'], self.evento)

    def test_editar_evento_post(self):
        url = reverse('editar_evento', kwargs={'id': self.evento.id})
        datos = {
            'titulo': 'Evento Editado',
            'descripcion': 'Desc editada',
            'fecha': timezone.now().date().isoformat(),
            'ubicacion': 'Cuenca',
        }
        response = self.client.post(url, datos)
        self.assertRedirects(response, reverse('listar_eventos'))
        self.evento.refresh_from_db()
        self.assertEqual(self.evento.titulo, 'Evento Editado')

    def test_eliminar_evento_sin_contratos(self):
        url = reverse('eliminar_evento', kwargs={'id': self.evento.id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('listar_eventos'))
        self.assertFalse(Evento.objects.filter(id=self.evento.id).exists())

    def test_eliminar_evento_con_contrato_aceptado(self):
        Contrato.objects.create(evento=self.evento, estado='Aceptado', artista=self.artista)
        url = reverse('eliminar_evento', kwargs={'id': self.evento.id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('listar_eventos'))
        # El evento no debe eliminarse si tiene contrato aceptado
        self.assertTrue(Evento.objects.filter(id=self.evento.id).exists())
