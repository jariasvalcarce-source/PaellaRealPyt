import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurante.settings')
django.setup()

from core.models import (
    Rol, UsuarioAuth, Empleado, Cliente, Proveedor,
    UnidadMedida, CategoriaProducto, Producto, MovimientoProducto,
    TipoMenu, Menu, RecetaMenu, Localidad, Barrio, MesaEvento, TipoEvento,
    Pedido, DetallePedidoMenu, Domicilio, Evento, MetodoPago, Factura, Pago, Notificacion
)

try:
    admin_rol = Rol.objects.get(name='admin')
    admin_user = UsuarioAuth.objects.filter(rol=admin_rol, nombre_usuario='admin').first()

    admin_empleado_id = -1
    if admin_user:
        admin_empleado = Empleado.objects.filter(id_auth_fk=admin_user).first()
        if admin_empleado:
            admin_empleado_id = admin_empleado.id_emple_pk

    # 1. Eliminar datos transaccionales
    Notificacion.objects.all().delete()
    Pago.objects.all().delete()
    Factura.objects.all().delete()
    Domicilio.objects.all().delete()
    Evento.objects.all().delete()
    DetallePedidoMenu.objects.all().delete()
    Pedido.objects.all().delete()
    MovimientoProducto.objects.all().delete()
    
    # 2. Eliminar Menus y Productos (Catalogo)
    RecetaMenu.objects.all().delete()
    Menu.objects.all().delete()
    TipoMenu.objects.all().delete()
    Producto.objects.all().delete()
    CategoriaProducto.objects.all().delete()
    UnidadMedida.objects.all().delete()
    
    # Proveedores y Clientes
    Proveedor.objects.all().delete()
    Cliente.objects.all().delete()
    
    # Empleados (menos admin)
    Empleado.objects.exclude(id_emple_pk=admin_empleado_id).delete()
    
    # Auth y demás (menos admin y roles)
    if admin_user:
        UsuarioAuth.objects.exclude(id_auth_pk=admin_user.id_auth_pk).delete()
    else:
        UsuarioAuth.objects.all().delete()

    print("OK - Base de datos limpiada. Solo queda el Admin.")
except Exception as e:
    import traceback
    traceback.print_exc()
