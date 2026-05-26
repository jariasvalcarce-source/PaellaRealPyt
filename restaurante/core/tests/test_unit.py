import pytest
from core.models import TipoMenu, Menu

@pytest.mark.django_db
def test_creacion_tipo_menu():
    """Prueba unitaria: Verifica que se pueda crear un TipoMenu correctamente"""
    tipo = TipoMenu.objects.create(nom_tipo_menu="Entradas")
    assert tipo.nom_tipo_menu == "Entradas"
    assert TipoMenu.objects.count() == 1

@pytest.mark.django_db
def test_creacion_menu():
    """Prueba unitaria: Verifica que se pueda crear un Menú correctamente"""
    tipo = TipoMenu.objects.create(nom_tipo_menu="Plato Principal")
    menu = Menu.objects.create(
        id_tipo_menu_fk=tipo,
        nom_menu="Paella Valenciana",
        des_menu="Paella tradicional",
        precio_menu=45000,
        disponible_menu=True
    )
    assert menu.nom_menu == "Paella Valenciana"
    assert menu.precio_menu == 45000
    assert menu.id_tipo_menu_fk == tipo
    assert Menu.objects.count() == 1
