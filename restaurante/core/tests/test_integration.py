import pytest
from django.urls import reverse
from django.test import Client
from core.models import Cliente, UsuarioAuth, Rol

@pytest.fixture
def cliente_autenticado(client):
    """Fixture para crear un usuario, un cliente y loguearlo"""
    rol = Rol.objects.create(name="Cliente")
    usuario = UsuarioAuth.objects.create(
        correo="test@cliente.com",
        contrasena_hash="password123",
        rol=rol,
        activo=True
    )
    cliente = Cliente.objects.create(
        id_auth_fk=usuario,
        nom_clien="Juan",
        apellido_clien="Perez",
        tel_cliente="3001234567",
        fecha_naci_cliente="1990-01-01"
    )
    session = client.session
    session['usuario_id'] = usuario.id_auth_pk
    session['rol'] = "Cliente"
    session.save()
    return client

@pytest.mark.django_db
def test_integracion_vista_carta(cliente_autenticado):
    """Prueba de integración: Verifica que un cliente logueado puede acceder a la carta"""
    url = reverse('carta_usuarios')
    response = cliente_autenticado.get(url)
    assert response.status_code == 200
    assert 'tipos' in response.context
    assert b'Men' in response.content

@pytest.mark.django_db
def test_integracion_redireccion_sin_login(client):
    """Prueba de integración: Verifica que si no hay sesión, se redirige al login"""
    url = reverse('carrito_compra')
    response = client.get(url)
    assert response.status_code == 302
    assert '/login' in response.url
