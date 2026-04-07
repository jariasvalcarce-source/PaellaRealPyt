from rest_framework import serializers
from core.models import Cliente, Empleado, Producto, Menu, Pedido

class ClienteSerializer(serializers.ModelSerializer):
    nombre_usuario = serializers.CharField(source='id_auth_fk.nombre_usuario', read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'

class EmpleadoSerializer(serializers.ModelSerializer):
    nombre_usuario = serializers.CharField(source='id_auth_fk.nombre_usuario', read_only=True)

    class Meta:
        model = Empleado
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    # Campos adicionales para enviar el nombre legible de la Foreign Key en lugar de solo el ID
    proveedor = serializers.CharField(source='id_provee_produ_fk.nom_provee', read_only=True)
    unidad_medida = serializers.CharField(source='id_uni_medi_produ_fk.abreviatura', read_only=True)
    categoria = serializers.CharField(source='id_cate_produ_fk.nom_cate', read_only=True)

    class Meta:
        model = Producto
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):
    tipo = serializers.CharField(source='id_tipo_menu_fk.nom_tipo_menu', read_only=True)

    class Meta:
        model = Menu
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    cliente = serializers.CharField(source='id_clien_pedido_fk.nom_clien', read_only=True)
    empleado = serializers.CharField(source='id_emple_pedido_fk.nom_emple', read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'
