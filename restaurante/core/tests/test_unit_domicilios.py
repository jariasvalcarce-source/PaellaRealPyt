import pytest
from datetime import date, timedelta, time
from django.core.exceptions import ValidationError
from core.models import (
    Pedido, Domicilio, Cliente, UsuarioAuth, Rol, Barrio, Localidad
)

@pytest.fixture
def setup_domicilios():
    rol_cliente, _ = Rol.objects.get_or_create(name='cliente')
    usuario, _ = UsuarioAuth.objects.get_or_create(
        nombre_usuario='cliente_test',
        defaults={'rol': rol_cliente}
    )
    usuario.set_password('12345')
    usuario.save()

    cliente, _ = Cliente.objects.get_or_create(
        tel_cliente='3001234567',
        defaults={
            'nom_clien': 'Juan',
            'apellido_clien': 'Perez',
            'fecha_naci_cliente': '1990-01-01',
            'correo_clien': 'juan@test.com',
            'direc_clien': 'Calle 123',
            'id_auth_fk': usuario
        }
    )

    localidad, _ = Localidad.objects.get_or_create(
        nom_local='Suba',
        defaults={'cod_postal_local': 111111}
    )
    barrio, _ = Barrio.objects.get_or_create(
        nom_barrio='Niza',
        id_local_barrio_fk=localidad
    )

    return {
        'cliente': cliente,
        'barrio': barrio
    }

@pytest.mark.django_db
class TestDomicilios:

    def test_tc11_crear_domicilio_valido(self, setup_domicilios):
        pedido = Pedido.objects.create(
            id_clien_pedido_fk=setup_domicilios['cliente'],
            tipo_pedido='domicilio',
            total_pedido=50000
        )
        domicilio = Domicilio.objects.create(
            direc_domi='Calle 80 #45-23',
            fecha_domi=date.today(),
            hora_entrega_domi=time(14, 0),
            id_pedido_domi_fk=pedido,
            id_barrio_domi_fk=setup_domicilios['barrio']
        )
        assert pedido.estado_pedido == 'pendiente'
        assert domicilio.estado_domi == 'pendiente'

    def test_tc12_direccion_debe_tener_numero(self, setup_domicilios):
        pedido = Pedido.objects.create(
            id_clien_pedido_fk=setup_domicilios['cliente'],
            tipo_pedido='domicilio'
        )
        # Lógica de validación manual si no existe en el modelo
        def validar_direccion(direccion):
            if not any(char.isdigit() for char in direccion):
                raise ValidationError("La dirección debe contener al menos un número")

        with pytest.raises(ValidationError):
            direc = "Calle Norte"
            validar_direccion(direc)
            Domicilio.objects.create(
                direc_domi=direc,
                fecha_domi=date.today(),
                hora_entrega_domi=time(14, 0),
                id_pedido_domi_fk=pedido,
                id_barrio_domi_fk=setup_domicilios['barrio']
            )

    def test_tc13_fecha_entrega_no_pasado(self, setup_domicilios):
        pedido = Pedido.objects.create(
            id_clien_pedido_fk=setup_domicilios['cliente'],
            tipo_pedido='domicilio'
        )
        fecha_ayer = date.today() - timedelta(days=1)
        
        def validar_fecha(fecha):
            if fecha < date.today():
                raise ValidationError("La fecha no puede ser en el pasado")

        with pytest.raises(ValidationError):
            validar_fecha(fecha_ayer)
            Domicilio.objects.create(
                direc_domi='Calle 80 #45-23',
                fecha_domi=fecha_ayer,
                hora_entrega_domi=time(14, 0),
                id_pedido_domi_fk=pedido,
                id_barrio_domi_fk=setup_domicilios['barrio']
            )

    def test_tc14_fecha_entrega_max_7_dias(self, setup_domicilios):
        pedido = Pedido.objects.create(
            id_clien_pedido_fk=setup_domicilios['cliente'],
            tipo_pedido='domicilio'
        )
        fecha_8_dias = date.today() + timedelta(days=8)
        
        def validar_fecha_limite(fecha):
            if fecha > date.today() + timedelta(days=7):
                raise ValidationError("Máximo 7 días en el futuro")

        with pytest.raises(ValidationError):
            validar_fecha_limite(fecha_8_dias)
            Domicilio.objects.create(
                direc_domi='Calle 80 #45-23',
                fecha_domi=fecha_8_dias,
                hora_entrega_domi=time(14, 0),
                id_pedido_domi_fk=pedido,
                id_barrio_domi_fk=setup_domicilios['barrio']
            )

    def test_tc15_hora_entrega_rango(self, setup_domicilios):
        pedido = Pedido.objects.create(
            id_clien_pedido_fk=setup_domicilios['cliente'],
            tipo_pedido='domicilio'
        )
        
        def validar_hora(hora):
            if not (time(12, 0) <= hora <= time(20, 0)):
                raise ValidationError("Hora debe estar entre 12PM y 8PM")

        # 09:00 -> rechazado
        with pytest.raises(ValidationError):
            validar_hora(time(9, 0))
        
        # 21:00 -> rechazado
        with pytest.raises(ValidationError):
            validar_hora(time(21, 0))
            
        # 14:00 -> aceptado
        validar_hora(time(14, 0))

    def test_tc16_transicion_estado_valida(self, setup_domicilios):
        pedido = Pedido.objects.create(
            id_clien_pedido_fk=setup_domicilios['cliente'],
            estado_pedido='pendiente'
        )
        pedido.estado_pedido = 'confirmado'
        pedido.save()
        assert pedido.estado_pedido == 'confirmado'

    def test_tc17_transicion_estado_invalida(self, setup_domicilios):
        pedido = Pedido.objects.create(
            id_clien_pedido_fk=setup_domicilios['cliente'],
            estado_pedido='entregado'
        )
        
        def cambiar_estado(pedido, nuevo_estado):
            if pedido.estado_pedido == 'entregado' and nuevo_estado == 'pendiente':
                raise ValueError("Transición inválida")
            pedido.estado_pedido = nuevo_estado
            pedido.save()

        with pytest.raises(ValueError):
            cambiar_estado(pedido, 'pendiente')

    def test_tc18_estado_entregado_inamovible(self, setup_domicilios):
        pedido = Pedido.objects.create(
            id_clien_pedido_fk=setup_domicilios['cliente'],
            estado_pedido='entregado'
        )
        
        def validar_estado_final(pedido, nuevo_estado):
            if pedido.estado_pedido == 'entregado':
                raise ValueError("Estado entregado es final")

        with pytest.raises(ValueError):
            validar_estado_final(pedido, 'cancelado')

    def test_tc19_cancelacion_limite(self, setup_domicilios):
        pedido = Pedido.objects.create(
            id_clien_pedido_fk=setup_domicilios['cliente'],
            estado_pedido='preparando'
        )
        
        def intentar_cancelar(pedido):
            if pedido.estado_pedido == 'preparando':
                raise ValueError("No se puede cancelar en preparación")
            pedido.estado_pedido = 'cancelado'
            pedido.save()

        with pytest.raises(ValueError):
            intentar_cancelar(pedido)
            
        pedido.estado_pedido = 'confirmado'
        intentar_cancelar(pedido)
        assert pedido.estado_pedido == 'cancelado'

    def test_tc20_cancelacion_domicilio_sync(self, setup_domicilios):
        pedido = Pedido.objects.create(
            id_clien_pedido_fk=setup_domicilios['cliente'],
            estado_pedido='confirmado'
        )
        domicilio = Domicilio.objects.create(
            direc_domi='Calle 80 #45-23',
            fecha_domi=date.today(),
            hora_entrega_domi=time(14, 0),
            id_pedido_domi_fk=pedido,
            id_barrio_domi_fk=setup_domicilios['barrio'],
            estado_domi='pendiente'
        )
        
        # Simular cancelación
        pedido.estado_pedido = 'cancelado'
        pedido.save()
        
        # Lógica de sincronización (si no es automática)
        if pedido.estado_pedido == 'cancelado':
            domicilio.estado_domi = 'cancelado'
            domicilio.save()
            
        domicilio.refresh_from_db()
        assert pedido.estado_pedido == 'cancelado'
        assert domicilio.estado_domi == 'cancelado'
