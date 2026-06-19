import pytest
from django.test import Client
from django.urls import reverse
from core.models import (
    Rol, UsuarioAuth, Empleado, Cliente, Producto, Menu, RecetaMenu,
    Pedido, Domicilio, MetodoPago, Pago, Factura, Barrio, Localidad,
    Proveedor, UnidadMedida, CategoriaProducto, TipoMenu
)
from decimal import Decimal
from datetime import date, time, datetime

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def setup_data():
    # Roles
    rol_admin, _ = Rol.objects.get_or_create(name='admin')
    rol_empleado, _ = Rol.objects.get_or_create(name='empleado')
    rol_cliente, _ = Rol.objects.get_or_create(name='cliente')

    # Usuarios
    u_admin = UsuarioAuth.objects.create(nombre_usuario='AdminU', correo='admin@gmail.com', rol=rol_admin)
    u_admin.set_password('Pass123')
    u_admin.save()

    u_emple = UsuarioAuth.objects.create(nombre_usuario='EmpleU', correo='emple@gmail.com', rol=rol_empleado)
    u_emple.set_password('Pass123')
    u_emple.save()

    u_clien = UsuarioAuth.objects.create(nombre_usuario='ClienU', correo='clien@gmail.com', rol=rol_cliente)
    u_clien.set_password('Pass123')
    u_clien.save()

    # Perfiles
    cli = Cliente.objects.create(
        id_auth_fk=u_clien, nom_clien='Cliente', apellido_clien='Test', 
        fecha_naci_cliente='1990-01-01', tel_cliente='3000000001', correo_clien='clien@gmail.com', direc_clien='Direccion'
    )
    
    emp = Empleado.objects.create(
        id_auth_fk=u_emple, nom_emple='Empleado', apellido_emple='Test', num_doc='E1',
        fecha_naci_emple='1990-01-01', tel_emple='3000000002', correo_emple='emple@gmail.com', 
        direc_emple='D', fecha_ingreso='2020-01-01', tipo_contrato='Término Indefinido', salario_empleado=1000
    )

    adm_emp = Empleado.objects.create(
        id_auth_fk=u_admin, nom_emple='Admin', apellido_emple='Real', num_doc='A1',
        fecha_naci_emple='1990-01-01', tel_emple='3000000003', correo_emple='admin_real@gmail.com', 
        direc_emple='D', fecha_ingreso='2020-01-01', tipo_contrato='Término Indefinido', salario_empleado=5000
    )

    # Inventario
    prov = Proveedor.objects.create(nom_provee='P', tel_provee='3000000004', correo_provee='p@gmail.com', direc_provee='D')
    um = UnidadMedida.objects.create(nom_uni_medi='kilogramo', abreviatura='kg', tipo_uni_medi='masa')
    cat = CategoriaProducto.objects.create(nom_cate='C', des_cate='D')
    tipo = TipoMenu.objects.create(nom_tipo_menu='T', des_tipo_menu='D')
    
    prod = Producto.objects.create(
        nom_produ='P1', stock_actual_produ=Decimal('100.00'), stock_minimo_produ=Decimal('10.00'),
        fecha_venci_produ='2026-12-31', precio_uni_produ=Decimal('10.00'),
        id_provee_produ_fk=prov, id_uni_medi_produ_fk=um, id_cate_produ_fk=cat
    )

    menu = Menu.objects.create(nom_menu='M1', precio_menu=Decimal('1000.00'), des_menu='D', id_tipo_menu_fk=tipo, disponible_menu=True)
    RecetaMenu.objects.create(id_menu_fk=menu, id_produ_fk=prod, cantidad_reque=Decimal('5.00'), id_uni_medi_fk=um)

    loc = Localidad.objects.create(nom_local='Localidad Test', cod_postal_local=110111)
    barrio = Barrio.objects.create(nom_barrio='Barrio Test 123', id_local_barrio_fk=loc)

    MetodoPago.objects.get_or_create(tipo_met_pago='efectivo', defaults={'des_met_pago': 'Efectivo'})
    MetodoPago.objects.get_or_create(tipo_met_pago='nequi', defaults={'des_met_pago': 'Nequi'})
    MetodoPago.objects.get_or_create(tipo_met_pago='stripe', defaults={'des_met_pago': 'Stripe'})

    return {
        'admin': u_admin, 'empleado': u_emple, 'cliente': u_clien,
        'cli': cli, 'emp': emp, 'adm_emp': adm_emp,
        'prod': prod, 'menu': menu, 'prov': prov,
        'um': um, 'cat': cat, 'barrio': barrio, 'tipo': tipo, 'loc': loc
    }

@pytest.mark.django_db
class TestIntegrationFlujos:

    def login(self, client, usuario):
        session = client.session
        session['usuario_id'] = usuario.id_auth_pk
        session['usuario'] = usuario.nombre_usuario
        session['rol'] = usuario.rol.name
        session.save()

    def test_tc29_acceso_admin_solo_admin(self, client, setup_data):
        # 1. Sin iniciar sesión, intentar entrar al panel de administración -> redirecciona al login
        response = client.get(reverse('inventario_admin'))
        assert response.status_code == 302
        assert 'login' in response.url

        # 2. Con rol cliente, intentar entrar -> redirecciona al login
        self.login(client, setup_data['cliente'])
        response = client.get(reverse('inventario_admin'))
        assert response.status_code == 302
        assert 'login' in response.url

        # 3. Con rol empleado, intentar entrar -> redirecciona a dashboard_empleado
        self.login(client, setup_data['empleado'])
        response = client.get(reverse('inventario_admin'))
        assert response.status_code == 302
        assert 'empleado' in response.url

        # 4. Con rol admin, entra correctamente
        self.login(client, setup_data['admin'])
        response = client.get(reverse('inventario_admin'))
        assert response.status_code == 200

    def test_tc30_acceso_empleado_solo_empleado(self, client, setup_data):
        # 1. Sin iniciar sesión -> redirecciona al login
        response = client.get(reverse('pedidos_empleado'))
        assert response.status_code == 302
        assert 'login' in response.url

        # 2. Con rol cliente -> redirecciona al login
        self.login(client, setup_data['cliente'])
        response = client.get(reverse('pedidos_empleado'))
        assert response.status_code == 302
        assert 'login' in response.url

        # 3. Con rol empleado -> entra correctamente
        self.login(client, setup_data['empleado'])
        response = client.get(reverse('pedidos_empleado'))
        assert response.status_code == 200

    def test_tc31_flujo_completo_pedido_domicilio(self, client, setup_data):
        # 1. Cliente agrega plato al carrito
        self.login(client, setup_data['cliente'])
        session = client.session
        session['carrito_temporal'] = [{
            'menu_id': setup_data['menu'].id_menu_pk,
            'cantidad': 2,
            'precio_u': str(setup_data['menu'].precio_menu),
            'subtotal': str(setup_data['menu'].precio_menu * 2),
            'nombre': setup_data['menu'].nom_menu
        }]
        session['total_temporal'] = str(setup_data['menu'].precio_menu * 2)
        session['tipo_pedido'] = 'domicilio'
        session['datos_entrega'] = {
            'direc_domi': 'Calle 100 #80-50',
            'id_barrio_domi_fk': setup_data['barrio'].id_barrio_pk,
            'fecha_domi': date.today().strftime('%Y-%m-%d'),
            'hora_entrega_domi': '15:00',
            'id_localidad': setup_data['loc'].id_local_pk
        }
        session.save()

        # 2. Cliente realiza el pago/pedido
        response = client.post(reverse('pago_pedido'), {
            'id_met_pago_fk': 'efectivo',
            'monto_con_el_que_paga': '5000'
        })
        assert response.status_code in [200, 302]

        # Verificar que el pedido se guardó en BD en estado 'pendiente'
        pedido = Pedido.objects.filter(id_clien_pedido_fk=setup_data['cli']).first()
        assert pedido is not None
        assert pedido.estado_pedido == 'pendiente'
        
        # Verificar que no hay factura generada todavía
        assert Factura.objects.filter(id_pedido_factu_fk=pedido).count() == 0

        # Verificar que el stock NO ha sido descontado todavía (sigue en 100)
        setup_data['prod'].refresh_from_db()
        assert setup_data['prod'].stock_actual_produ == Decimal('100.00')

        # 3. Administrador cambia a 'confirmado'
        self.login(client, setup_data['admin'])
        client.post(reverse('cambiar_estado_pedido_detalle', args=[pedido.id_pedido_pk]), {'estado_pedido': 'confirmado'})
        pedido.refresh_from_db()
        assert pedido.estado_pedido == 'confirmado'
        
        # El stock sigue en 100 en confirmado
        setup_data['prod'].refresh_from_db()
        assert setup_data['prod'].stock_actual_produ == Decimal('100.00')

        # 4. Cambiar a 'preparando' -> se descuenta stock
        client.post(reverse('cambiar_estado_pedido_detalle', args=[pedido.id_pedido_pk]), {'estado_pedido': 'preparando'})
        pedido.refresh_from_db()
        assert pedido.estado_pedido == 'preparando'
        
        # Se descontaron 2 unidades de menú * 5 kg de ingrediente = 10 kg
        setup_data['prod'].refresh_from_db()
        assert setup_data['prod'].stock_actual_produ == Decimal('90.00')

        # 5. Cambiar a 'listo'
        client.post(reverse('cambiar_estado_pedido_detalle', args=[pedido.id_pedido_pk]), {'estado_pedido': 'listo'})
        pedido.refresh_from_db()
        assert pedido.estado_pedido == 'listo'

        # 6. Cambiar a 'entregado' -> se genera factura automáticamente
        client.post(reverse('cambiar_estado_pedido_detalle', args=[pedido.id_pedido_pk]), {'estado_pedido': 'entregado'})
        pedido.refresh_from_db()
        assert pedido.estado_pedido == 'entregado'

        # Verificar factura
        factura = Factura.objects.filter(id_pedido_factu_fk=pedido).first()
        assert factura is not None
        assert factura.total_factu == pedido.total_pedido

    def test_tc32_flujo_pago_transferencia(self, client, setup_data):
        self.login(client, setup_data['cliente'])
        session = client.session
        session['carrito_temporal'] = [{
            'menu_id': setup_data['menu'].id_menu_pk,
            'cantidad': 1,
            'precio_u': str(setup_data['menu'].precio_menu),
            'subtotal': str(setup_data['menu'].precio_menu),
            'nombre': setup_data['menu'].nom_menu
        }]
        session['total_temporal'] = str(setup_data['menu'].precio_menu)
        session['tipo_pedido'] = 'domicilio'
        session['datos_entrega'] = {
            'direc_domi': 'Calle 100 #80-50',
            'id_barrio_domi_fk': setup_data['barrio'].id_barrio_pk,
            'fecha_domi': date.today().strftime('%Y-%m-%d'),
            'hora_entrega_domi': '15:00',
            'id_localidad': setup_data['loc'].id_local_pk
        }
        session.save()

        # Realizar pago con nequi (transferencia)
        response = client.post(reverse('pago_pedido'), {
            'id_met_pago_fk': 'nequi',
            'celular_origen': '3009999999'
        })
        assert response.status_code in [200, 302]

        pedido = Pedido.objects.filter(id_clien_pedido_fk=setup_data['cli']).first()
        assert pedido is not None
        
        # Verificar que el pago se creó en estado 'pendiente'
        pago = Pago.objects.filter(id_pedido_pago_fk=pedido).first()
        assert pago is not None
        assert pago.estado_pago == 'pendiente'

        # Admin inicia sesión y cambia el estado a 'confirmado'
        self.login(client, setup_data['admin'])
        client.post(reverse('cambiar_estado_pedido_detalle', args=[pedido.id_pedido_pk]), {'estado_pedido': 'confirmado'})
        pedido.refresh_from_db()
        assert pedido.estado_pedido == 'confirmado'

        # Cambiar el estado a 'preparando' -> el pago debe aprobarse automáticamente
        client.post(reverse('cambiar_estado_pedido_detalle', args=[pedido.id_pedido_pk]), {'estado_pedido': 'preparando'})
        pedido.refresh_from_db()
        assert pedido.estado_pedido == 'preparando'
        
        # Verificar que el pago ahora es 'completado'
        pago.refresh_from_db()
        assert pago.estado_pago == 'completado'

        # Cambiar el pedido a 'listo'
        client.post(reverse('cambiar_estado_pedido_detalle', args=[pedido.id_pedido_pk]), {'estado_pedido': 'listo'})
        pedido.refresh_from_db()
        assert pedido.estado_pedido == 'listo'

        # Cambiar el pedido a 'entregado'
        client.post(reverse('cambiar_estado_pedido_detalle', args=[pedido.id_pedido_pk]), {'estado_pedido': 'entregado'})
        pedido.refresh_from_db()
        assert pedido.estado_pedido == 'entregado'
        
        # Verificar que se creó la factura y está asociada al pago
        factura = Factura.objects.filter(id_pedido_factu_fk=pedido).first()
        assert factura is not None
        
        pago.refresh_from_db()
        assert pago.id_factu_pago_fk == factura

    def test_tc33_menu_no_disponible_no_carrito(self, client, setup_data):
        # Desactivamos el menú
        setup_data['menu'].disponible_menu = False
        setup_data['menu'].save()

        self.login(client, setup_data['cliente'])
        # 1. Verificar a través de API verificar_stock_menu
        response = client.get(reverse('verificar_stock_menu', args=[setup_data['menu'].id_menu_pk]) + '?qty=1')
        # Dado que el menú no está disponible, la vista verificar_stock_menu
        # captura Http404 y devuelve un JsonResponse con status 200 y mensaje de error
        assert response.status_code == 200
        assert 'No se pudo verificar el stock' in response.json()['mensaje']

        # 2. Intentar guardar en el carrito
        response = client.post(reverse('guardar_carrito'), {
            'num_items': '1',
            'menu_id_0': setup_data['menu'].id_menu_pk,
            'cantidad_0': '1'
        })
        # La vista redirige al carrito con mensaje de error porque el menú no está disponible
        assert response.status_code == 302
        assert 'carrito' in response.url
