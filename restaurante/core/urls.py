from django.urls import path

from .views.auth             import inicio, login_view, logout_view, registro_view
from .views.views_personas   import (
    dashboard_admin, dashboard_empleado, inicio_usuarios, mi_perfil,
    personas_admin, inventario_admin, historial_ventas,
    crear_empleado, tabla_empleados, editar_empleado, cambiar_estado_empleado,
    crear_cliente, tabla_clientes, editar_cliente, cambiar_estado_cliente,
    crear_proveedor, tabla_proveedores, editar_proveedor, cambiar_estado_proveedor,
    editar_perfil_admin,
)

from .views.views_reportes   import reportes_admin
from .views.views_inventario import (
    crear_producto, tabla_productos, editar_producto, cambiar_estado_producto,
    crear_movimiento, tabla_movimientos,
    crear_menu, tabla_menus, editar_menu, cambiar_disponibilidad_menu, eliminar_menu,
    crear_receta, tabla_recetas, editar_receta, eliminar_receta,
    editar_unidad_receta, eliminar_unidad_receta,
)
from .views.views_api import (
    listar_productos_api, bulk_upload_productos_api,
    listar_menus_api, bulk_upload_menus_api,
    listar_pedidos_api, bulk_upload_pedidos_api,
)
from .views.views_pedidos import (
    crear_pedido, mis_pedidos, pedidos_admin, cambiar_estado_pedido,
    asignar_empleado_pedido, detalle_pedido,
    carrito_compra, guardar_carrito, cancelar_pedido, cancelar_pedido_usuario,
    marcar_entregado_usuario,
    carta_usuarios, verificar_stock_menu, notificar_stock_admin,
    pago_pedido, pago_exito, descargar_factura, ver_factura,
    tabla_domicilios_admin, tabla_eventos_admin,
    detalle_domicilio, detalle_evento_admin,
    marcar_domicilio_entregado_admin, marcar_evento_finalizado_admin,
    tabla_facturas_todas, tabla_facturas_domicilio, tabla_facturas_evento,
    detalle_factura_domicilio, detalle_factura_evento,
)

urlpatterns = [

    # ================== GENERALES ==================
    path('',          inicio,        name='inicio'),
    path('login/',    login_view,    name='login'),
    path('logout/',   logout_view,   name='logout'),
    path('registro/', registro_view, name='registro'),

    # ================== DASHBOARDS ==================
    path('admin-panel/', dashboard_admin,    name='dashboard_admin'),
    path('admin-panel/perfil/editar/', editar_perfil_admin, name='editar_perfil_admin'),
    path('empleado/',    dashboard_empleado, name='dashboard_empleado'),
    path('usuario/',        inicio_usuarios,    name='inicio_usuarios'),
    path('usuario/perfil/', mi_perfil,          name='mi_perfil'),

    # ================== ADMIN - PERSONAS ==================
    path('admin-panel/personas/', personas_admin, name='personas_admin'),

    # ================== EMPLEADOS ==================
    path('admin-panel/empleados/',                 tabla_empleados,         name='tabla_empleados'),
    path('admin-panel/empleados/nuevo/',           crear_empleado,          name='crear_empleado'),
    path('admin-panel/empleados/<int:id>/editar/', editar_empleado,         name='editar_empleado'),
    path('admin-panel/empleados/<int:id>/estado/', cambiar_estado_empleado, name='cambiar_estado_empleado'),

    # ================== CLIENTES ==================
    path('admin-panel/clientes/',                 tabla_clientes,         name='tabla_clientes'),
    path('admin-panel/clientes/nuevo/',           crear_cliente,          name='crear_cliente'),
    path('admin-panel/clientes/<int:id>/editar/', editar_cliente,         name='editar_cliente'),
    path('admin-panel/clientes/<int:id>/estado/', cambiar_estado_cliente, name='cambiar_estado_cliente'),

    # ================== INVENTARIO ==================
    path('admin-panel/inventario/', inventario_admin, name='inventario_admin'),

    # Proveedores
    path('admin-panel/proveedores/',                 tabla_proveedores,        name='tabla_proveedores'),
    path('admin-panel/proveedores/nuevo/',           crear_proveedor,          name='crear_proveedor'),
    path('admin-panel/proveedores/<int:id>/editar/', editar_proveedor,         name='editar_proveedor'),
    path('admin-panel/proveedores/<int:id>/estado/', cambiar_estado_proveedor, name='cambiar_estado_proveedor'),

    # Productos
    path('admin-panel/productos/',                 tabla_productos,         name='tabla_productos'),
    path('admin-panel/productos/nuevo/',           crear_producto,          name='crear_producto'),
    path('admin-panel/productos/<int:id>/editar/', editar_producto,         name='editar_producto'),
    path('admin-panel/productos/<int:id>/estado/', cambiar_estado_producto, name='cambiar_estado_producto'),

    # Movimientos
    path('admin-panel/movimientos/',       tabla_movimientos, name='tabla_movimientos'),
    path('admin-panel/movimientos/nuevo/', crear_movimiento,  name='crear_movimiento'),

    # Menús
    path('admin-panel/inventario/menu/crear/',                   crear_menu,                  name='crear_menu'),
    path('admin-panel/inventario/menu/tabla/',                   tabla_menus,                 name='tabla_menus'),
    path('admin-panel/inventario/menu/<int:id>/editar/',         editar_menu,                 name='editar_menu'),
    path('admin-panel/inventario/menu/<int:id>/disponibilidad/', cambiar_disponibilidad_menu, name='cambiar_disponibilidad_menu'),
    path('admin-panel/inventario/menu/<int:id>/eliminar/',       eliminar_menu,               name='eliminar_menu'),

    # Recetas
    path('admin-panel/recetas/',                                 tabla_recetas,          name='tabla_recetas'),
    path('admin-panel/recetas/nuevo/',                           crear_receta,           name='crear_receta'),
    path('admin-panel/recetas/<int:id_receta>/editar/',          editar_receta,          name='editar_receta'),
    path('admin-panel/recetas/<int:id_receta>/eliminar/',        eliminar_receta,        name='eliminar_receta'),
    path('admin-panel/recetas/unidad/<int:id_unidad>/editar/',   editar_unidad_receta,   name='editar_unidad_receta'),
    path('admin-panel/recetas/unidad/<int:id_unidad>/eliminar/', eliminar_unidad_receta, name='eliminar_unidad_receta'),

    #Pedidos a domicilio y eventos
    path('admin-panel/domicilios/',                        tabla_domicilios_admin, name='tabla_domicilios_admin'),
    path('admin-panel/domicilios/<int:id_domicilio>/',     detalle_domicilio,      name='detalle_domicilio'),
    path('admin-panel/domicilios/<int:id_domicilio>/entregado/', marcar_domicilio_entregado_admin, name='marcar_domicilio_entregado_admin'),
    path('admin-panel/eventos/',                           tabla_eventos_admin,    name='tabla_eventos_admin'),
    path('admin-panel/eventos/<int:id_evento>/',           detalle_evento_admin,   name='detalle_evento_admin'),
    path('admin-panel/eventos/<int:id_evento>/finalizado/', marcar_evento_finalizado_admin, name='marcar_evento_finalizado_admin'),

    # ================== PEDIDOS ==================
    path('admin-panel/pedidos/',                                  pedidos_admin,           name='pedidos_admin'),
    path('admin-panel/pedidos/<int:id_pedido>/estado/',           cambiar_estado_pedido,   name='cambiar_estado_pedido'),
    path('admin-panel/pedidos/<int:id_pedido>/asignar-empleado/', asignar_empleado_pedido, name='asignar_empleado_pedido'),
    path('admin-panel/pedidos/<int:id_pedido>/detalle/',          detalle_pedido,          name='detalle_pedido'),

    # ================== HISTORIAL Y REPORTES ==================
    path('admin-panel/historial-ventas/', historial_ventas, name='historial_ventas'),
    path('admin-panel/reportes/', reportes_admin, name='reportes_admin'),
    path('admin-panel/historial-ventas/todas/', tabla_facturas_todas, name='tabla_facturas_todas'),
    path('admin-panel/historial-ventas/domicilios/', tabla_facturas_domicilio, name='tabla_facturas_domicilio'),
    path('admin-panel/historial-ventas/eventos/', tabla_facturas_evento, name='tabla_facturas_evento'),
    path('admin-panel/historial-ventas/domicilios/<int:id_factura>/', detalle_factura_domicilio, name='detalle_factura_domicilio'),
    path('admin-panel/historial-ventas/eventos/<int:id_factura>/', detalle_factura_evento, name='detalle_factura_evento'),

    # ================== USUARIOS ==================
    path('usuario/carta/',        carta_usuarios, name='carta_usuarios'),
    path('usuario/pedido/nuevo/', crear_pedido,   name='crear_pedido'),
    path('usuario/mis-pedidos/',  mis_pedidos,    name='mis_pedidos'),
    path('usuario/mis-pedidos/<int:id_pedido>/cancelar/', cancelar_pedido_usuario, name='cancelar_pedido_usuario'),
    path('usuario/mis-pedidos/<int:id_pedido>/entregado/', marcar_entregado_usuario, name='marcar_entregado_usuario'),

    # Carrito
    path('usuario/carrito/',         carrito_compra,  name='carrito_compra'),
    path('usuario/carrito/guardar/', guardar_carrito, name='guardar_carrito'),
    path('usuario/pedido/cancelar/', cancelar_pedido, name='cancelar_pedido'),

    # Stock AJAX
    path('usuario/carrito/stock/<int:menu_id>/', verificar_stock_menu, name='verificar_stock_menu'),
    path('usuario/carrito/notificar-stock/', notificar_stock_admin, name='notificar_stock_admin'),

    # API interna
    path('api/productos/',                     listar_productos_api,     name='listar_productos_api'),
    path('api/productos/bulk-upload/',         bulk_upload_productos_api, name='bulk_upload_productos_api'),
    path('api/menus/',                         listar_menus_api,          name='listar_menus_api'),
    path('api/menus/bulk-upload/',             bulk_upload_menus_api,      name='bulk_upload_menus_api'),
    path('api/pedidos/',                       listar_pedidos_api,        name='listar_pedidos_api'),
    path('api/pedidos/bulk-upload/',           bulk_upload_pedidos_api,    name='bulk_upload_pedidos_api'),

    # Pago y Factura
    path('usuario/pago/',                    pago_pedido,       name='pago_pedido'),
    path('usuario/pago/exito/',              pago_exito,        name='pago_exito'),
    path('factura/<int:factura_id>/ver/',    ver_factura,       name='ver_factura'),
    path('factura/<int:factura_id>/pdf/',    descargar_factura, name='descargar_factura'),
    
]