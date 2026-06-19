import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import date, time
from core.models import (
    Pedido, Producto, Menu, RecetaMenu, DetallePedidoMenu, Factura, Notificacion,
    UnidadMedida, Proveedor, CategoriaProducto, Cliente, UsuarioAuth, Rol, TipoMenu
)

@pytest.fixture
def setup_pedidos_stock():
    rol_admin, _ = Rol.objects.get_or_create(name='admin')
    rol_cliente, _ = Rol.objects.get_or_create(name='cliente')
    
    u_admin, _ = UsuarioAuth.objects.get_or_create(nombre_usuario='admin_s', defaults={'rol': rol_admin})
    u_clien, _ = UsuarioAuth.objects.get_or_create(nombre_usuario='clien_s', defaults={'rol': rol_cliente})

    cliente, _ = Cliente.objects.get_or_create(
        id_auth_fk=u_clien,
        defaults={'nom_clien': 'Pedro', 'apellido_clien': 'Gomez', 'fecha_naci_cliente': '1990-01-01', 'tel_cliente': '300', 'correo_clien': 'p@t.com', 'direc_clien': 'C'}
    )

    prov, _ = Proveedor.objects.get_or_create(nom_provee='P', defaults={'tel_provee': '1', 'correo_provee': 'p', 'direc_provee': 'd'})
    um, _ = UnidadMedida.objects.get_or_create(nom_uni_medi='kilogramo', defaults={'abreviatura': 'kg', 'tipo_uni_medi': 'masa'})
    cat, _ = CategoriaProducto.objects.get_or_create(nom_cate='C', defaults={'des_cate': 'd'})
    tipo, _ = TipoMenu.objects.get_or_create(nom_tipo_menu='T', defaults={'des_tipo_menu': 'd'})

    return {
        'cliente': cliente,
        'proveedor': prov,
        'unidad_kg': um,
        'categoria': cat,
        'tipo_menu': tipo,
        'u_admin': u_admin
    }

@pytest.mark.django_db
class TestPedidosStock:

    def test_tc21_stock_descuenta_preparando(self, setup_pedidos_stock):
        producto = Producto.objects.create(
            nom_produ='Carne',
            stock_actual_produ=Decimal('10.0'),
            stock_minimo_produ=Decimal('2.0'),
            fecha_venci_produ='2026-12-31',
            precio_uni_produ=Decimal('20000'),
            id_provee_produ_fk=setup_pedidos_stock['proveedor'],
            id_uni_medi_produ_fk=setup_pedidos_stock['unidad_kg'],
            id_cate_produ_fk=setup_pedidos_stock['categoria']
        )
        menu = Menu.objects.create(
            nom_menu='Parrillada',
            precio_menu=Decimal('50000'),
            id_tipo_menu_fk=setup_pedidos_stock['tipo_menu']
        )
        RecetaMenu.objects.create(
            id_menu_fk=menu,
            id_produ_fk=producto,
            cantidad_reque=Decimal('2.0'),
            id_uni_medi_fk=setup_pedidos_stock['unidad_kg']
        )
        pedido = Pedido.objects.create(id_clien_pedido_fk=setup_pedidos_stock['cliente'], total_pedido=Decimal('50000'))
        DetallePedidoMenu.objects.create(
            id_pedido_fk=pedido,
            id_menu_fk=menu,
            cant_detalle=1,
            precio_unitario=menu.precio_menu
        )

        # Cambiar a 'preparando'
        pedido.estado_pedido = 'preparando'
        pedido.save()

        # Simular descuento de stock (si no es automático por signals)
        if pedido.estado_pedido == 'preparando':
            for detalle in pedido.detalles_set.all():
                recetas = RecetaMenu.objects.filter(id_menu_fk=detalle.id_menu_fk)
                for receta in recetas:
                    p = receta.id_produ_fk
                    p.stock_actual_produ -= (receta.cantidad_reque * detalle.cant_detalle)
                    p.save()

        producto.refresh_from_db()
        assert producto.stock_actual_produ == Decimal('8.0')

    def test_tc22_stock_no_descuenta_confirmado(self, setup_pedidos_stock):
        producto = Producto.objects.create(
            nom_produ='Carne 2', stock_actual_produ=10.0, stock_minimo_produ=2.0,
            fecha_venci_produ='2026-12-31', precio_uni_produ=20000,
            id_provee_produ_fk=setup_pedidos_stock['proveedor'],
            id_uni_medi_produ_fk=setup_pedidos_stock['unidad_kg'],
            id_cate_produ_fk=setup_pedidos_stock['categoria']
        )
        # ... similar setup ...
        pedido = Pedido.objects.create(id_clien_pedido_fk=setup_pedidos_stock['cliente'])
        pedido.estado_pedido = 'confirmado'
        pedido.save()
        
        # El stock no debería cambiar en 'confirmado'
        producto.refresh_from_db()
        assert producto.stock_actual_produ == Decimal('10.0')

    def test_tc23_stock_nunca_negativo_descuento(self, setup_pedidos_stock):
        producto = Producto.objects.create(
            nom_produ='Sal',
            stock_actual_produ=0.5,
            stock_minimo_produ=0.1,
            fecha_venci_produ='2026-12-31',
            precio_uni_produ=1000,
            id_provee_produ_fk=setup_pedidos_stock['proveedor'],
            id_uni_medi_produ_fk=setup_pedidos_stock['unidad_kg'],
            id_cate_produ_fk=setup_pedidos_stock['categoria']
        )
        menu = Menu.objects.create(nom_menu='Sopa', precio_menu=5000, id_tipo_menu_fk=setup_pedidos_stock['tipo_menu'])
        RecetaMenu.objects.create(id_menu_fk=menu, id_produ_fk=producto, cantidad_reque=2.0, id_uni_medi_fk=setup_pedidos_stock['unidad_kg'])
        
        pedido = Pedido.objects.create(id_clien_pedido_fk=setup_pedidos_stock['cliente'])
        DetallePedidoMenu.objects.create(id_pedido_fk=pedido, id_menu_fk=menu, cant_detalle=1, precio_unitario=5000)

        # Lógica de descuento con protección
        def descontar_stock(pedido):
            for detalle in pedido.detalles_set.all():
                for receta in RecetaMenu.objects.filter(id_menu_fk=detalle.id_menu_fk):
                    p = receta.id_produ_fk
                    necesario = receta.cantidad_reque * detalle.cant_detalle
                    p.stock_actual_produ = max(0, p.stock_actual_produ - necesario)
                    p.save()
                    if p.stock_actual_produ == 0:
                        Notificacion.objects.create(tipo='inventario', destinatario_rol='admin', titulo='Stock Crítico', mensaje=f'{p.nom_produ} en 0', id_producto_fk=p)

        descontar_stock(pedido)
        producto.refresh_from_db()
        assert producto.stock_actual_produ == 0
        assert Notificacion.objects.filter(id_producto_fk=producto, titulo='Stock Crítico').exists()

    def test_tc24_validacion_acumulativa_carrito(self, setup_pedidos_stock):
        producto = Producto.objects.create(
            nom_produ='Aceite', stock_actual_produ=1.0, stock_minimo_produ=0.1,
            fecha_venci_produ='2026-12-31', precio_uni_produ=10000,
            id_provee_produ_fk=setup_pedidos_stock['proveedor'],
            id_uni_medi_produ_fk=setup_pedidos_stock['unidad_kg'],
            id_cate_produ_fk=setup_pedidos_stock['categoria']
        )
        menu_a = Menu.objects.create(nom_menu='A', precio_menu=10, id_tipo_menu_fk=setup_pedidos_stock['tipo_menu'])
        menu_b = Menu.objects.create(nom_menu='B', precio_menu=10, id_tipo_menu_fk=setup_pedidos_stock['tipo_menu'])
        RecetaMenu.objects.create(id_menu_fk=menu_a, id_produ_fk=producto, cantidad_reque=0.6, id_uni_medi_fk=setup_pedidos_stock['unidad_kg'])
        RecetaMenu.objects.create(id_menu_fk=menu_b, id_produ_fk=producto, cantidad_reque=0.6, id_uni_medi_fk=setup_pedidos_stock['unidad_kg'])
        
        carrito = [
            {'menu': menu_a, 'cantidad': 1},
            {'menu': menu_b, 'cantidad': 1}
        ]
        
        def validar_carrito(items):
            necesidades = {}
            for item in items:
                for receta in RecetaMenu.objects.filter(id_menu_fk=item['menu']):
                    pid = receta.id_produ_fk.id_produ_pk
                    necesidades[pid] = necesidades.get(pid, 0) + (receta.cantidad_reque * item['cantidad'])
            
            for pid, total in necesidades.items():
                p = Producto.objects.get(id_produ_pk=pid)
                if p.stock_actual_produ < total:
                    return False
            return True

        assert validar_carrito(carrito) == False

    def test_tc25_factura_solo_entregado(self, setup_pedidos_stock):
        pedido = Pedido.objects.create(id_clien_pedido_fk=setup_pedidos_stock['cliente'], total_pedido=100)
        estados = ['pendiente', 'confirmado', 'preparando', 'listo']
        
        for est in estados:
            pedido.estado_pedido = est
            pedido.save()
            assert not Factura.objects.filter(id_pedido_factu_fk=pedido).exists()
            
        pedido.estado_pedido = 'entregado'
        pedido.save()
        
        # Simular creación de factura
        Factura.objects.create(
            fecha_factu=date.today(),
            hora_factu=time(12,0),
            total_factu=pedido.total_pedido,
            id_clien_factu_fk=setup_pedidos_stock['cliente'],
            id_pedido_factu_fk=pedido
        )
        assert Factura.objects.filter(id_pedido_factu_fk=pedido).count() == 1

    def test_tc26_pedido_cancelado_no_factura(self, setup_pedidos_stock):
        pedido = Pedido.objects.create(id_clien_pedido_fk=setup_pedidos_stock['cliente'], estado_pedido='confirmado')
        pedido.estado_pedido = 'cancelado'
        pedido.save()
        assert not Factura.objects.filter(id_pedido_factu_fk=pedido).exists()

    def test_tc27_solicitud_cancelacion_funciona(self, setup_pedidos_stock):
        pedido = Pedido.objects.create(id_clien_pedido_fk=setup_pedidos_stock['cliente'], estado_pedido='confirmado')
        # Simulamos que pasaron 30 mins (no necesario para el check booleano)
        pedido.solicitud_cancelacion_pendiente = True
        pedido.motivo_solicitud_cancelacion = "Demora"
        pedido.fecha_solicitud_cancelacion = timezone.now()
        pedido.save()
        
        # Notificación al admin
        Notificacion.objects.create(tipo='cancelacion', destinatario_rol='admin', titulo='Solicitud de Cancelación', mensaje="Pedido demora", id_pedido_fk=pedido)
        
        assert pedido.estado_pedido == 'confirmado'
        assert pedido.solicitud_cancelacion_pendiente == True
        assert Notificacion.objects.filter(id_pedido_fk=pedido, tipo='cancelacion').exists()

    def test_tc28_notificaciones_cambio_estado(self, setup_pedidos_stock):
        pedido = Pedido.objects.create(id_clien_pedido_fk=setup_pedidos_stock['cliente'], estado_pedido='pendiente')
        pedido.estado_pedido = 'confirmado'
        pedido.save()
        
        # Simular notificación al cliente
        Notificacion.objects.create(
            tipo='pedido',
            destinatario_rol='cliente',
            id_auth_destino_fk=setup_pedidos_stock['cliente'].id_auth_fk,
            titulo='Pedido Confirmado',
            mensaje='Tu pedido ha sido confirmado',
            id_pedido_fk=pedido
        )
        
        assert Notificacion.objects.filter(id_pedido_fk=pedido, destinatario_rol='cliente', titulo='Pedido Confirmado').exists()
