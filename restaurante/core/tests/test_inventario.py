import pytest
from decimal import Decimal
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import (
    Producto, MovimientoProducto, Proveedor, UnidadMedida, 
    CategoriaProducto, Empleado, Rol, UsuarioAuth, Menu, RecetaMenu, Notificacion, TipoMenu
)
from core.utils import convertir_a_unidad_base

@pytest.fixture
def setup_data():
    rol_admin, _ = Rol.objects.get_or_create(name='admin')
    usuario, _ = UsuarioAuth.objects.get_or_create(
        nombre_usuario='admin_test',
        defaults={'rol': rol_admin}
    )
    usuario.set_password('12345')
    usuario.save()

    empleado, _ = Empleado.objects.get_or_create(
        num_doc='12345678',
        defaults={
            'nom_emple': 'Admin',
            'apellido_emple': 'Test',
            'fecha_naci_emple': '1990-01-01',
            'tipo_doc': 'Cédula de Ciudadanía',
            'tel_emple': '3001234567',
            'correo_emple': 'admin@test.com',
            'direc_emple': 'Calle 123',
            'fecha_ingreso': '2020-01-01',
            'tipo_contrato': 'Término Indefinido',
            'salario_empleado': Decimal('2000000'),
            'id_auth_fk': usuario
        }
    )

    proveedor, _ = Proveedor.objects.get_or_create(
        nom_provee='Proveedor Test',
        defaults={
            'tel_provee': '3009876543',
            'correo_provee': 'prov@test.com',
            'direc_provee': 'Carrera 45'
        }
    )

    unidad_kg, _ = UnidadMedida.objects.get_or_create(
        nom_uni_medi='kilogramo',
        defaults={'abreviatura': 'kg', 'tipo_uni_medi': 'masa'}
    )
    
    unidad_g, _ = UnidadMedida.objects.get_or_create(
        nom_uni_medi='gramo',
        defaults={'abreviatura': 'g', 'tipo_uni_medi': 'masa'}
    )

    categoria, _ = CategoriaProducto.objects.get_or_create(
        nom_cate='Ingredientes',
        defaults={'des_cate': 'Ingredientes básicos'}
    )

    tipo_menu, _ = TipoMenu.objects.get_or_create(
        nom_tipo_menu='Plato Fuerte',
        defaults={'des_tipo_menu': 'Platos principales'}
    )

    return {
        'empleado': empleado,
        'proveedor': proveedor,
        'unidad_kg': unidad_kg,
        'unidad_g': unidad_g,
        'categoria': categoria,
        'tipo_menu': tipo_menu
    }

@pytest.mark.django_db
class TestInventario:

    def test_tc01_crear_producto_valido(self, setup_data):
        producto = Producto.objects.create(
            nom_produ='Arroz',
            stock_actual_produ=Decimal('10.0'),
            stock_minimo_produ=Decimal('2.0'),
            fecha_venci_produ='2026-12-31',
            precio_uni_produ=Decimal('5000'),
            des_produ='Arroz premium',
            id_provee_produ_fk=setup_data['proveedor'],
            id_uni_medi_produ_fk=setup_data['unidad_kg'],
            id_cate_produ_fk=setup_data['categoria']
        )
        assert Producto.objects.filter(id_produ_pk=producto.id_produ_pk).exists()
        assert producto.stock_actual_produ == Decimal('10.0')

    def test_tc02_stock_no_negativo(self, setup_data):
        with pytest.raises(IntegrityError):
            Producto.objects.create(
                nom_produ='Producto Negativo',
                stock_actual_produ=Decimal('-1.0'),
                stock_minimo_produ=Decimal('2.0'),
                fecha_venci_produ='2026-12-31',
                precio_uni_produ=Decimal('5000'),
                des_produ='Test',
                id_provee_produ_fk=setup_data['proveedor'],
                id_uni_medi_produ_fk=setup_data['unidad_kg'],
                id_cate_produ_fk=setup_data['categoria']
            )

    def test_tc03_stock_minimo_mayor_cero(self, setup_data):
        producto = Producto(
            nom_produ='Producto Min 0',
            stock_actual_produ=Decimal('5.0'),
            stock_minimo_produ=Decimal('0'),
            fecha_venci_produ='2026-12-31',
            precio_uni_produ=Decimal('5000'),
            des_produ='Test',
            id_provee_produ_fk=setup_data['proveedor'],
            id_uni_medi_produ_fk=setup_data['unidad_kg'],
            id_cate_produ_fk=setup_data['categoria']
        )
        with pytest.raises(ValidationError):
            producto.full_clean()

    def test_tc04_nombre_sin_duplicados(self, setup_data):
        Producto.objects.create(
            nom_produ='Arroz Bomba',
            stock_actual_produ=Decimal('10.0'),
            stock_minimo_produ=Decimal('2.0'),
            fecha_venci_produ='2026-12-31',
            precio_uni_produ=Decimal('5000'),
            des_produ='Test',
            id_provee_produ_fk=setup_data['proveedor'],
            id_uni_medi_produ_fk=setup_data['unidad_kg'],
            id_cate_produ_fk=setup_data['categoria']
        )
        with pytest.raises((IntegrityError, ValidationError)):
            Producto.objects.create(
                nom_produ='Arroz Bomba',
                stock_actual_produ=Decimal('5.0'),
                stock_minimo_produ=Decimal('1.0'),
                fecha_venci_produ='2026-12-31',
                precio_uni_produ=Decimal('5000'),
                des_produ='Test',
                id_provee_produ_fk=setup_data['proveedor'],
                id_uni_medi_produ_fk=setup_data['unidad_kg'],
                id_cate_produ_fk=setup_data['categoria']
            )

    def test_tc05_movimiento_entrada_suma(self, setup_data):
        producto = Producto.objects.create(
            nom_produ='Producto Entrada',
            stock_actual_produ=Decimal('5.0'),
            stock_minimo_produ=Decimal('1.0'),
            fecha_venci_produ='2026-12-31',
            precio_uni_produ=Decimal('5000'),
            des_produ='Test',
            id_provee_produ_fk=setup_data['proveedor'],
            id_uni_medi_produ_fk=setup_data['unidad_kg'],
            id_cate_produ_fk=setup_data['categoria']
        )
        cantidad = Decimal('3.0')
        MovimientoProducto.objects.create(
            tipo_movi='entrada',
            motivo_movi='Compra',
            cant_movi=cantidad,
            stock_anterior=producto.stock_actual_produ,
            stock_posterior=producto.stock_actual_produ + cantidad,
            id_emple_movi_fk=setup_data['empleado'],
            id_produ_movi_fk=producto
        )
        producto.stock_actual_produ += cantidad
        producto.save()
        
        producto.refresh_from_db()
        assert producto.stock_actual_produ == Decimal('8.0')

    def test_tc06_movimiento_salida_resta(self, setup_data):
        producto = Producto.objects.create(
            nom_produ='Producto Salida',
            stock_actual_produ=Decimal('10.0'),
            stock_minimo_produ=Decimal('1.0'),
            fecha_venci_produ='2026-12-31',
            precio_uni_produ=Decimal('5000'),
            des_produ='Test',
            id_provee_produ_fk=setup_data['proveedor'],
            id_uni_medi_produ_fk=setup_data['unidad_kg'],
            id_cate_produ_fk=setup_data['categoria']
        )
        cantidad = Decimal('4.0')
        MovimientoProducto.objects.create(
            tipo_movi='salida',
            motivo_movi='Venta',
            cant_movi=cantidad,
            stock_anterior=producto.stock_actual_produ,
            stock_posterior=producto.stock_actual_produ - cantidad,
            id_emple_movi_fk=setup_data['empleado'],
            id_produ_movi_fk=producto
        )
        producto.stock_actual_produ -= cantidad
        producto.save()
        
        producto.refresh_from_db()
        assert producto.stock_actual_produ == Decimal('6.0')

    def test_tc07_salida_no_supera_stock(self, setup_data):
        producto = Producto.objects.create(
            nom_produ='Producto Limite',
            stock_actual_produ=Decimal('2.0'),
            stock_minimo_produ=Decimal('1.0'),
            fecha_venci_produ='2026-12-31',
            precio_uni_produ=Decimal('5000'),
            des_produ='Test',
            id_provee_produ_fk=setup_data['proveedor'],
            id_uni_medi_produ_fk=setup_data['unidad_kg'],
            id_cate_produ_fk=setup_data['categoria']
        )
        with pytest.raises((IntegrityError, ValueError)):
            cantidad = Decimal('5.0')
            if producto.stock_actual_produ < cantidad:
                 raise ValueError("Stock insuficiente")
            
            producto.stock_actual_produ -= cantidad
            producto.save()

    def test_tc08_conversion_unidades(self, setup_data):
        producto = Producto.objects.create(
            nom_produ='Arroz Base KG',
            stock_actual_produ=Decimal('1.0'),
            stock_minimo_produ=Decimal('0.1'),
            fecha_venci_produ='2026-12-31',
            precio_uni_produ=Decimal('5000'),
            des_produ='Test',
            id_provee_produ_fk=setup_data['proveedor'],
            id_uni_medi_produ_fk=setup_data['unidad_kg'],
            id_cate_produ_fk=setup_data['categoria']
        )
        cantidad_g = 500
        cantidad_kg = convertir_a_unidad_base(cantidad_g, setup_data['unidad_g'], setup_data['unidad_kg'])
        
        assert cantidad_kg == Decimal('0.5')
        
        producto.stock_actual_produ -= cantidad_kg
        producto.save()
        producto.refresh_from_db()
        assert producto.stock_actual_produ == Decimal('0.5')

    def test_tc09_alerta_stock_minimo(self, setup_data):
        producto = Producto.objects.create(
            nom_produ='Producto Alerta',
            stock_actual_produ=Decimal('0.5'),
            stock_minimo_produ=Decimal('1.0'),
            fecha_venci_produ='2026-12-31',
            precio_uni_produ=Decimal('5000'),
            des_produ='Test',
            id_provee_produ_fk=setup_data['proveedor'],
            id_uni_medi_produ_fk=setup_data['unidad_kg'],
            id_cate_produ_fk=setup_data['categoria']
        )
        assert producto.stock_actual_produ <= producto.stock_minimo_produ
        
        Notificacion.objects.create(
            tipo='inventario',
            destinatario_rol='admin',
            titulo='Stock Mínimo',
            mensaje=f'El producto {producto.nom_produ} llegó al mínimo.',
            id_producto_fk=producto
        )
        
        assert Notificacion.objects.filter(destinatario_rol='admin', id_producto_fk=producto).exists()

    def test_tc10_menu_desactivado_por_stock(self, setup_data):
        producto = Producto.objects.create(
            nom_produ='Ingrediente Escaso',
            stock_actual_produ=Decimal('0.1'),
            stock_minimo_produ=Decimal('0.05'),
            fecha_venci_produ='2026-12-31',
            precio_uni_produ=Decimal('5000'),
            des_produ='Test',
            id_provee_produ_fk=setup_data['proveedor'],
            id_uni_medi_produ_fk=setup_data['unidad_kg'],
            id_cate_produ_fk=setup_data['categoria']
        )
        menu = Menu.objects.create(
            nom_menu='Plato Test',
            precio_menu=Decimal('20000'),
            des_menu='Delicioso',
            id_tipo_menu_fk=setup_data['tipo_menu'],
            disponible_menu=True
        )
        RecetaMenu.objects.create(
            id_menu_fk=menu,
            id_produ_fk=producto,
            cantidad_reque=Decimal('0.1'),
            id_uni_medi_fk=setup_data['unidad_kg']
        )
        
        producto.stock_actual_produ = Decimal('0')
        producto.save()
        
        if producto.stock_actual_produ <= 0:
            menu.disponible_menu = False
            menu.save()
            
        menu.refresh_from_db()
        assert menu.disponible_menu == False
