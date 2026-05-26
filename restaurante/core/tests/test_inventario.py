import pytest
from decimal import Decimal
from core.models import Producto, Proveedor, UnidadMedida, CategoriaProducto, Empleado, MovimientoProducto
from core.views.views_inventario import _actualizar_stock

@pytest.fixture
def db_setup():
    # Crear dependencias básicas
    categoria = CategoriaProducto.objects.create(
        nom_cate="Ingredientes",
        des_cate="Ingredientes de cocina"
    )
    unidad = UnidadMedida.objects.create(
        nom_uni_medi="Kilogramo",
        abreviatura="kg",
        tipo_uni_medi="peso"
    )
    proveedor = Proveedor.objects.create(
        nom_provee="Distribuidora Central",
        tel_provee=5551234,
        correo_provee="distribuidora@correo.com",
        direc_provee="Calle 123",
        estado_provee="activo"
    )
    empleado = Empleado.objects.create(
        nom_emple="Carlos",
        apellido_emple="Gomez",
        fecha_naci_emple="1990-01-01",
        tipo_doc="Cédula de Ciudadanía",
        num_doc="12345678",
        tel_emple="3001234567",
        correo_emple="carlos@correo.com",
        direc_emple="Calle 456",
        fecha_ingreso="2025-01-01",
        tipo_contrato="Término Indefinido",
        salario_empleado=1500000.00,
        estado_emple="activo"
    )
    
    # Crear producto de prueba
    producto = Producto.objects.create(
        nom_produ="Arroz Bomba",
        stock_actual_produ=10.0,
        stock_minimo_produ=2.0,
        fecha_venci_produ="2027-12-31",
        precio_uni_produ=4.50,
        des_produ="Arroz especial para paella",
        estado_produ="disponible",
        id_provee_produ_fk=proveedor,
        id_uni_medi_produ_fk=unidad,
        id_cate_produ_fk=categoria
    )
    
    return {
        "producto": producto,
        "empleado": empleado,
        "unidad": unidad,
        "proveedor": proveedor,
        "categoria": categoria
    }

@pytest.mark.django_db
def test_creacion_producto(db_setup):
    """Prueba unitaria básica: Verificar la creación correcta del producto"""
    prod = db_setup["producto"]
    assert prod.nom_produ == "Arroz Bomba"
    assert prod.stock_actual_produ == 10.0
    assert prod.estado_produ == "disponible"

@pytest.mark.django_db
def test_actualizar_stock_entrada(db_setup):
    """Prueba de integración: Sumar stock al registrar una entrada"""
    prod = db_setup["producto"]
    
    # Simular una entrada de 5.5 kg
    cantidad = 5.5
    anterior, posterior = _actualizar_stock(prod, "entrada", cantidad)
    
    # Verificar retorno y actualización en base de datos
    assert anterior == 10.0
    assert posterior == 15.5
    
    # Recargar de BD para verificar persistencia
    prod.refresh_from_db()
    assert prod.stock_actual_produ == 15.5
    assert prod.estado_produ == "disponible"

@pytest.mark.django_db
def test_actualizar_stock_salida_y_agotado(db_setup):
    """Prueba de integración: Restar stock hasta agotar el producto"""
    prod = db_setup["producto"]
    
    # Simular una salida de 10 kg (agota el producto)
    cantidad = 10.0
    anterior, posterior = _actualizar_stock(prod, "salida", cantidad)
    
    assert anterior == 10.0
    assert posterior == 0.0
    
    prod.refresh_from_db()
    assert prod.stock_actual_produ == 0.0
    # Al llegar a 0 o menos, el estado debe cambiar a "no disponible"
    assert prod.estado_produ == "no disponible"

@pytest.mark.django_db
def test_salida_insuficiente_rechazada(db_setup, client):
    """Prueba de integración: Intentar hacer una salida mayor al stock disponible"""
    prod = db_setup["producto"]
    emp = db_setup["empleado"]
    
    # Autenticar al cliente simulando variables de sesión
    session = client.session
    session["usuario"] = "Carlos"
    session["rol"] = "admin"
    session.save()
    
    # Intentar enviar una petición POST para crear un movimiento de salida de 15 kg (disponible: 10 kg)
    url = "/admin-panel/movimientos/nuevo/"
    data = {
        "tipo_movi": "salida",
        "motivo_movi": "merma",
        "cant_movi": "15.0",
        "id_emple_movi_fk": emp.id_emple_pk,
        "id_produ_movi_fk": prod.id_produ_pk
    }
    
    response = client.post(url, data)
    
    # El stock del producto no debe haber cambiado
    prod.refresh_from_db()
    assert prod.stock_actual_produ == 10.0
    assert prod.estado_produ == "disponible"
    
    # No se debe haber creado ningún objeto MovimientoProducto
    assert not MovimientoProducto.objects.filter(id_produ_movi_fk=prod).exists()
