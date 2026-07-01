from django.urls import path, include

from core.views.auth             import inicio, login_view, logout_view, registro_view
from core.views.views_personas   import (
    dashboard_admin, inicio_usuarios, mi_perfil, subir_foto_perfil,
    personas_admin, inventario_admin, historial_ventas,
    crear_empleado, tabla_empleados, editar_empleado, cambiar_estado_empleado,
    crear_cliente, tabla_clientes, editar_cliente, cambiar_estado_cliente,
    crear_proveedor, tabla_proveedores, editar_proveedor, cambiar_estado_proveedor, carga_proveedores,
    editar_perfil_admin, notificaciones_usuarios, favoritos_usuarios,
    notificaciones_admin, ajustes_admin, marcar_leida_notificacion, eliminar_notificacion,
    notif_dropdown_hx, enviar_promocion
)

from core.views.views_sincronizacion import (
    toggle_favorito, agregar_carrito, quitar_carrito, badge_sincronizacion
)

from core.views.views_reportes   import reportes_admin
from core.views.views_empleado   import dashboard_empleado, pedidos_empleado, detalle_pedido_empleado, mi_perfil_empleado
from core.views.views_inventario import (
    crear_producto, tabla_productos, editar_producto, cambiar_estado_producto, carga_productos,
    crear_movimiento, tabla_movimientos, detalle_movimiento,
    crear_menu, tabla_menus, menu_dashboard, editar_menu, cambiar_disponibilidad_menu, eliminar_menu,
    crear_receta, tabla_recetas, editar_receta, eliminar_receta,
    editar_unidad_receta, eliminar_unidad_receta,
    ajax_crear_categoria, ajax_crear_unidad,
    ajax_eliminar_categoria, ajax_eliminar_unidad,
    ajax_crear_tipo_menu, ajax_eliminar_tipo_menu,
)

from core.views.views_pedidos import (
    crear_pedido, mis_pedidos, pedidos_admin, cambiar_estado_pedido, cambiar_estado_pedido_detalle,
    asignar_empleado_pedido, detalle_pedido,
    carrito_compra, guardar_carrito, cancelar_pedido, cancelar_pedido_usuario,
    marcar_entregado_usuario,
    carta_usuarios, verificar_stock_menu, notificar_stock_admin, verificar_carrito_completo,
    pago_pedido, pago_exito, descargar_factura, ver_factura, iniciar_pago_stripe,
    tabla_domicilios_admin,
    detalle_domicilio,
    marcar_domicilio_entregado_admin,
    tabla_facturas_todas, tabla_facturas_domicilio,
    detalle_factura_domicilio,
    aprobar_solicitud_cancelacion, rechazar_solicitud_cancelacion,
    alertar_falta_stock, obtener_barrios_por_localidad,
)

from core.views.views_pedidos import migrate_db

urlpatterns = [
    path('dev-migrate/', migrate_db, name='migrate_db'),

    # ================== GENERALES ==================
    path('',          inicio,        name='inicio'),
    path('login/',    login_view,    name='login'),
    path('logout/',   logout_view,   name='logout'),
    path('registro/', registro_view, name='registro'),

    # ================== DASHBOARDS ==================
    path('admin-panel/', dashboard_admin,    name='dashboard_admin'),
    path('empleado/dashboard/', dashboard_empleado, name='dashboard_empleado'),
    path('empleado/pedidos/', pedidos_empleado, name='pedidos_empleado'),
    path('empleado/pedidos/<int:id_pedido>/', detalle_pedido_empleado, name='detalle_pedido_empleado'),
    path('empleado/mi-perfil/', mi_perfil_empleado, name='mi_perfil_empleado'),
    path('admin-panel/perfil/editar/', editar_perfil_admin, name='editar_perfil_admin'),
    path('admin-panel/notificaciones/', notificaciones_admin, name='notificaciones_admin'),
    path('admin-panel/notificaciones/<int:id>/leer/', marcar_leida_notificacion, name='marcar_leida_notificacion'),
    path('admin-panel/notificaciones/<int:id>/eliminar/', eliminar_notificacion, name='eliminar_notificacion'),
    path('admin-panel/ajustes/', ajustes_admin, name='ajustes_admin'),
    path('admin-panel/comunicaciones/', enviar_promocion, name='enviar_promocion'),
    path('notificaciones-hx/', notif_dropdown_hx, name='notif_dropdown_hx'),
    path('usuario/',        inicio_usuarios,    name='inicio_usuarios'),
    path('usuario/perfil/', mi_perfil,          name='mi_perfil'),
    path('usuario/perfil/subir-foto/', subir_foto_perfil, name='subir_foto_perfil'),
    path('usuario/notificaciones/', notificaciones_usuarios, name='notificaciones_usuarios'),
    path('usuario/favoritos/', favoritos_usuarios, name='favoritos_usuarios'),
    path('usuario/alertar-stock/<int:id_menu>/', alertar_falta_stock, name='alertar_falta_stock'),

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
    path('admin-panel/inventario/categorias/ajax-crear/', ajax_crear_categoria, name='ajax_crear_categoria'),
    path('admin-panel/inventario/unidades/ajax-crear/', ajax_crear_unidad, name='ajax_crear_unidad'),
    path('admin-panel/inventario/categorias/ajax-eliminar/<int:id>/', ajax_eliminar_categoria, name='ajax_eliminar_categoria'),
    path('admin-panel/inventario/unidades/ajax-eliminar/<int:id>/', ajax_eliminar_unidad, name='ajax_eliminar_unidad'),

    # Proveedores
    path('admin-panel/proveedores/',                 tabla_proveedores,        name='tabla_proveedores'),
    path('admin-panel/proveedores/nuevo/',           crear_proveedor,          name='crear_proveedor'),
    path('admin-panel/proveedores/carga/',           carga_proveedores,        name='carga_proveedores'),
    path('admin-panel/proveedores/<int:id>/editar/', editar_proveedor,         name='editar_proveedor'),
    path('admin-panel/proveedores/<int:id>/estado/', cambiar_estado_proveedor, name='cambiar_estado_proveedor'),

    # Productos
    path('admin-panel/productos/',                 tabla_productos,         name='tabla_productos'),
    path('admin-panel/productos/nuevo/',           crear_producto,          name='crear_producto'),
    path('admin-panel/productos/carga/',           carga_productos,         name='carga_productos'),
    path('admin-panel/productos/<int:id>/editar/', editar_producto,         name='editar_producto'),
    path('admin-panel/productos/<int:id>/estado/', cambiar_estado_producto, name='cambiar_estado_producto'),

    # Movimientos
    path('admin-panel/movimientos/',               tabla_movimientos,       name='tabla_movimientos'),
    path('admin-panel/movimientos/nuevo/',         crear_movimiento,        name='crear_movimiento'),
    path('admin-panel/movimientos/<int:id>/',      detalle_movimiento,      name='detalle_movimiento'),

    # Menús
    path('admin-panel/inventario/menu/', menu_dashboard, name='menu_dashboard'),
    path('admin-panel/inventario/menu/crear/',                   crear_menu,                  name='crear_menu'),
    path('admin-panel/inventario/menu/tipos/ajax-crear/',        ajax_crear_tipo_menu,        name='ajax_crear_tipo_menu'),
    path('admin-panel/inventario/menu/tipos/ajax-eliminar/<int:id>/', ajax_eliminar_tipo_menu, name='ajax_eliminar_tipo_menu'),
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

    #Pedidos a domicilio
    path('admin-panel/domicilios/',                        tabla_domicilios_admin, name='tabla_domicilios_admin'),
    path('admin-panel/domicilios/<int:id_domicilio>/',     detalle_domicilio,      name='detalle_domicilio'),
    path('admin-panel/domicilios/<int:id_domicilio>/entregado/', marcar_domicilio_entregado_admin, name='marcar_domicilio_entregado_admin'),

    # ================== PEDIDOS ==================
    path('admin-panel/pedidos/',                                  pedidos_admin,           name='pedidos_admin'),
    path('admin-panel/pedidos/<int:id_pedido>/estado/',           cambiar_estado_pedido,          name='cambiar_estado_pedido'),
    path('admin-panel/pedidos/<int:id_pedido>/estado_detalle/',  cambiar_estado_pedido_detalle,  name='cambiar_estado_pedido_detalle'),
    path('admin-panel/pedidos/<int:id_pedido>/asignar-empleado/', asignar_empleado_pedido, name='asignar_empleado_pedido'),
    path('admin-panel/pedidos/<int:id_pedido>/detalle/',          detalle_pedido,          name='detalle_pedido'),
    path('admin-panel/pedidos/<int:id_pedido>/aprobar-cancelacion/', aprobar_solicitud_cancelacion, name='aprobar_solicitud_cancelacion'),
    path('admin-panel/pedidos/<int:id_pedido>/rechazar-cancelacion/', rechazar_solicitud_cancelacion, name='rechazar_solicitud_cancelacion'),

    # ================== HISTORIAL Y REPORTES ==================
    path('admin-panel/historial-ventas/', historial_ventas, name='historial_ventas'),
    path('admin-panel/reportes/', reportes_admin, name='reportes_admin'),
    path('admin-panel/historial-ventas/todas/', tabla_facturas_todas, name='tabla_facturas_todas'),
    path('admin-panel/historial-ventas/domicilios/', tabla_facturas_domicilio, name='tabla_facturas_domicilio'),
    path('admin-panel/historial-ventas/domicilios/<int:id_factura>/', detalle_factura_domicilio, name='detalle_factura_domicilio'),

    # ================== USUARIOS ==================
    path('usuario/carta/',        carta_usuarios, name='carta_usuarios'),
    path('usuario/pedido/nuevo/', crear_pedido,   name='crear_pedido'),
    path('usuario/pedido/',       crear_pedido,   name='index_pedido'),
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
    path('usuario/carrito/verificar-completo/', verificar_carrito_completo, name='verificar_carrito_completo'),

    # Redireccionar todas las rutas /api/ hacia el nuevo archivo 
    path('api/', include('core.api.urls')),

    # Sincronización HTMX y AJAX
    path('sync/favorito/<int:menu_id>/', toggle_favorito, name='toggle_favorito'),
    path('sync/carrito/add/<int:menu_id>/', agregar_carrito, name='agregar_carrito'),
    path('sync/carrito/remove/<int:menu_id>/', quitar_carrito, name='quitar_carrito'),
    path('sync/badges/', badge_sincronizacion, name='badge_sincronizacion'),

    # Pago y Factura
    path('usuario/pago/',                    pago_pedido,       name='pago_pedido'),
    path('usuario/pago/stripe/<int:pedido_id>/', iniciar_pago_stripe, name='iniciar_pago_stripe'),
    path('usuario/pago/exito/',              pago_exito,        name='pago_exito'),
    path('factura/<int:factura_id>/ver/',    ver_factura,       name='ver_factura'),
    path('factura/<int:factura_id>/pdf/',    descargar_factura, name='descargar_factura'),
        # API Localidades y Barrios
    path('api/localidad/<int:id_localidad>/barrios/', obtener_barrios_por_localidad, name='obtener_barrios_por_localidad'),
]