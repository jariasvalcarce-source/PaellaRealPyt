from django.urls import path
from core.api_auth import login_api
from core.views.views_api import (
    listar_productos_api, bulk_upload_productos_api,
    listar_menus_api, bulk_upload_menus_api,
    listar_pedidos_api, bulk_upload_pedidos_api,
    listar_clientes_api, obtener_cliente_api, crear_cliente_api, bulk_upload_clientes_api,
    listar_empleados_api, obtener_empleado_api, crear_empleado_api, bulk_upload_empleados_api,
    bulk_upload_proveedores_api, bulk_upload_movimientos_api,
    bulk_upload_recetas_api,
    webhook_stripe_api
)

urlpatterns = [
    path('auth/login/', login_api, name='login_api'),

    # Productos
    path('productos/',             listar_productos_api,      name='listar_productos_api'),
    path('productos/bulk-upload/', bulk_upload_productos_api, name='bulk_upload_productos_api'),

    # Menús
    path('menus/',                 listar_menus_api,          name='listar_menus_api'),
    path('menus/bulk-upload/',     bulk_upload_menus_api,     name='bulk_upload_menus_api'),

    # Pedidos
    path('pedidos/',               listar_pedidos_api,        name='listar_pedidos_api'),
    path('pedidos/bulk-upload/',   bulk_upload_pedidos_api,   name='bulk_upload_pedidos_api'),

    # Clientes
    path('clientes/',               listar_clientes_api,      name='listar_clientes_api'),
    path('clientes/bulk-upload/',   bulk_upload_clientes_api, name='bulk_upload_clientes_api'),
    path('clientes/<int:cliente_id>/', obtener_cliente_api,   name='obtener_cliente_api'),
    path('clientes/nuevo/',         crear_cliente_api,        name='crear_cliente_api'),

    # Empleados
    path('empleados/',               listar_empleados_api,    name='listar_empleados_api'),
    path('empleados/nuevo/',         crear_empleado_api,      name='crear_empleado_api'),
    path('empleados/bulk-upload/',   bulk_upload_empleados_api, name='bulk_upload_empleados_api'),
    path('empleados/<int:empleado_id>/', obtener_empleado_api,name='obtener_empleado_api'),

    # Proveedores y Movimientos (Nuevos Módulos Masivos)
    path('proveedores/bulk-upload/', bulk_upload_proveedores_api, name='bulk_upload_proveedores_api'),
    path('movimientos/bulk-upload/', bulk_upload_movimientos_api, name='bulk_upload_movimientos_api'),
    path('recetas/bulk-upload/', bulk_upload_recetas_api, name='bulk_upload_recetas_api'),
    
    # Webhook Stripe
    path('stripe/webhook/', webhook_stripe_api, name='webhook_stripe_api'),
]
