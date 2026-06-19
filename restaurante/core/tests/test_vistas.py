import pytest
import json
import io
from django.test import Client
from django.urls import reverse
from core.models import (
    Rol, UsuarioAuth, Producto, Proveedor, UnidadMedida, CategoriaProducto,
    Empleado, Cliente, Menu, TipoMenu, Pedido, MetodoPago, Factura, Barrio, Localidad,
    Notificacion, DetallePedidoMenu, RecetaMenu, Pago, HistorialEstadoPedido, ConfiguracionSistema
)
from decimal import Decimal
from datetime import date, time, datetime, timedelta
from django.utils import timezone

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
        id_auth_fk=u_clien, nom_clien='C', apellido_clien='T', 
        fecha_naci_cliente='1990-01-01', tel_cliente='3000000001', correo_clien='clien@gmail.com', direc_clien='D'
    )
    
    emp = Empleado.objects.create(
        id_auth_fk=u_emple, nom_emple='E', apellido_emple='T', num_doc='E1',
        fecha_naci_emple='1990-01-01', tel_emple='3000000002', correo_emple='emple@gmail.com', 
        direc_emple='D', fecha_ingreso='2020-01-01', tipo_contrato='Término Indefinido', salario_empleado=1000
    )

    adm_emp = Empleado.objects.create(
        id_auth_fk=u_admin, nom_emple='A', apellido_emple='R', num_doc='A1',
        fecha_naci_emple='1990-01-01', tel_emple='3000000003', correo_emple='admin_real@gmail.com', 
        direc_emple='D', fecha_ingreso='2020-01-01', tipo_contrato='Término Indefinido', salario_empleado=5000
    )

    # Inventario
    prov = Proveedor.objects.create(nom_provee='P', tel_provee='3000000004', correo_provee='p@gmail.com', direc_provee='D')
    um = UnidadMedida.objects.create(nom_uni_medi='kilogramo', abreviatura='kg', tipo_uni_medi='masa')
    cat = CategoriaProducto.objects.create(nom_cate='C', des_cate='D')
    tipo = TipoMenu.objects.create(nom_tipo_menu='T', des_tipo_menu='D')
    
    prod = Producto.objects.create(
        nom_produ='P1', stock_actual_produ=Decimal('100'), stock_minimo_produ=Decimal('10'),
        fecha_venci_produ='2026-12-31', precio_uni_produ=Decimal('10'),
        id_provee_produ_fk=prov, id_uni_medi_produ_fk=um, id_cate_produ_fk=cat
    )

    menu = Menu.objects.create(nom_menu='M1', precio_menu=Decimal('1000'), des_menu='D', id_tipo_menu_fk=tipo)
    RecetaMenu.objects.create(id_menu_fk=menu, id_produ_fk=prod, cantidad_reque=Decimal('1'), id_uni_medi_fk=um)

    loc = Localidad.objects.create(nom_local='L', cod_postal_local=1)
    barrio = Barrio.objects.create(nom_barrio='B', id_local_barrio_fk=loc)

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
class TestVistasFinalCoverage80:

    def login(self, client, usuario):
        session = client.session
        session['usuario_id'] = usuario.id_auth_pk
        session['usuario'] = usuario.nombre_usuario
        session['rol'] = usuario.rol.name
        session.save()

    # -------------------------------------------------------------------------
    # AUTH & PERSONAS
    # -------------------------------------------------------------------------
    def test_auth_personas(self, client, setup_data):
        client.get(reverse('inicio'))
        client.post(reverse('login'), {'usuario': 'AdminU', 'password': 'Pass123'})
        client.get(reverse('logout'))
        
        self.login(client, setup_data['admin'])
        for v in ['dashboard_admin', 'tabla_clientes', 'tabla_empleados', 'tabla_proveedores', 'ajustes_admin']:
            client.get(reverse(v))
        
        # Empleado Edit/Status
        e = setup_data['emp']
        client.get(reverse('editar_empleado', args=[e.id_emple_pk]))
        client.post(reverse('editar_empleado', args=[e.id_emple_pk]), {
            'nom_emple': 'N', 'apellido_emple': 'A', 'fecha_naci_emple': '1990-01-01',
            'tel_emple': '3110000000', 'correo_emple': 'new@gmail.com', 'direc_emple': 'D',
            'tipo_doc': 'C', 'num_doc': 'E1', 'tipo_contrato': 'T', 'fecha_ingreso': '2020-01-01', 'salario_empleado': '100'
        })
        client.get(reverse('cambiar_estado_empleado', args=[e.id_emple_pk]))

        # Cliente Edit/Status
        c = setup_data['cli']
        client.get(reverse('editar_cliente', args=[c.id_clien_pk]))
        client.post(reverse('editar_cliente', args=[c.id_clien_pk]), {
            'nom_clien': 'N', 'apellido_clien': 'A', 'fecha_naci_cliente': '1990-01-01',
            'tel_cliente': '3120000000', 'correo_clien': 'cli_new@gmail.com', 'direc_clien': 'D'
        })
        client.get(reverse('cambiar_estado_cliente', args=[c.id_clien_pk]))

    # -------------------------------------------------------------------------
    # INVENTARIO
    # -------------------------------------------------------------------------
    def test_inventario_comprehensive(self, client, setup_data):
        self.login(client, setup_data['admin'])
        p = setup_data['prod']
        client.get(reverse('editar_producto', args=[p.id_produ_pk]))
        client.post(reverse('crear_movimiento'), {
            'tipo_movi': 'entrada', 'motivo_movi': 'A', 'cant_movi': '1', 'unidad_movi': 'kg', 
            'id_emple_movi_fk': setup_data['adm_emp'].id_emple_pk, 'id_produ_movi_fk': p.id_produ_pk
        })
        client.post(reverse('ajax_crear_categoria'), {'nom_cate': 'CAT1', 'des_cate': 'D'})
        client.get(reverse('tabla_recetas'))

    # -------------------------------------------------------------------------
    # PEDIDOS FLOW
    # -------------------------------------------------------------------------
    def test_pedidos_flow_high(self, client, setup_data):
        self.login(client, setup_data['cliente'])
        # Setup session for paying
        s = client.session
        s['carrito_temporal'] = [{'menu_id': setup_data['menu'].id_menu_pk, 'cantidad': 1, 'precio_u': 100, 'subtotal': 100, 'nombre': 'M1'}]
        s['total_temporal'] = 100
        s['tipo_pedido'] = 'domicilio'
        s['datos_entrega'] = {
            'direc_domi': 'Calle 123 #45-67', 'id_barrio_domi_fk': setup_data['barrio'].id_barrio_pk, 
            'fecha_domi': '2026-06-25', 'hora_entrega_domi': '14:00', 'id_localidad': setup_data['loc'].id_local_pk
        }
        s.save()
        
        client.post(reverse('pago_pedido'), {'id_met_pago_fk': 'efectivo', 'monto_con_el_que_paga': '200'})
        ped = Pedido.objects.first()
        
        # Admin side
        self.login(client, setup_data['admin'])
        client.get(reverse('detalle_pedido', args=[ped.id_pedido_pk]))
        client.post(reverse('cambiar_estado_pedido_detalle', args=[ped.id_pedido_pk]), {'estado_pedido': 'confirmado'})
        client.post(reverse('asignar_empleado_pedido', args=[ped.id_pedido_pk]), {'id_emple_pedido_fk': setup_data['adm_emp'].id_emple_pk})

    # -------------------------------------------------------------------------
    # API & OTHERS
    # -------------------------------------------------------------------------
    def test_api_and_others(self, client, setup_data):
        self.login(client, setup_data['admin'])
        client.get(reverse('listar_productos_api'))
        client.get(reverse('reportes_admin'))
        
        self.login(client, setup_data['empleado'])
        client.get(reverse('dashboard_empleado'))
        client.get(reverse('pedidos_empleado'))
        
        # Misc AJAX
        client.get(reverse('obtener_barrios_por_localidad', args=[setup_data['loc'].id_local_pk]))
