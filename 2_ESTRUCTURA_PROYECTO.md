# Estructura Estricta de Archivos - La Paella Real

Para la IA: Esta es la topología exacta y las convenciones de nombrado del código. NUNCA asumas una ruta, guíate por este mapa.

## 📂 Mapa Completo de Directorios

```text
restaurante/
├── core/
│   ├── models.py                     # ÚNICO archivo de modelos para toda la app.
│   ├── urls.py                       # ÚNICO enrutador principal. No hay urls.py en sub-apps.
│   ├── context_processors.py         # Inyecta `notificaciones_no_leidas` y variables de carrito al HTML global.
│   ├── middleware.py                 # (Ej. RolMiddleware) para evitar que clientes entren a rutas /admin-panel/
│   │
│   └── views/                        # VISTAS (Fragmentadas por lógica de negocio)
│       ├── auth.py                   # login_view, logout_view, registro_view
│       ├── views_personas.py         # Empleados, Clientes, Proveedores. (crear_*, tabla_*, editar_*)
│       ├── views_inventario.py       # Productos, Categorías, Menú, Recetas (crear_menu, tabla_productos, etc.)
│       ├── views_pedidos.py          # EL MÁS COMPLEJO. Contiene:
│       │                             # - carrito_compra, guardar_carrito
│       │                             # - cambiar_estado_pedido, cambiar_estado_pedido_detalle
│       │                             # - cancelar_pedido, cancelar_pedido_usuario
│       │                             # - pago_pedido, iniciar_pago_stripe, detalle_domicilio, detalle_evento_admin
│       ├── views_reportes.py         # reportes_admin, tabla_facturas_*
│       └── views_api.py              # Endpoints JSON (si existen)
│
├── templates/
│   ├── admin/                        # RUTAS: /admin-panel/*
│   │   ├── factura/                  # tabla-factura-*.html, detalle-factura-*.html
│   │   ├── inventario/               # tabla-productos.html, index-movimiento-producto.html
│   │   ├── menu/                     # tabla-menu.html, index-receta.html
│   │   ├── pedido/                   # tabla-domicilio.html, tabla-evento.html, detalle-domicilio.html, detalle-evento.html
│   │   └── personas/                 # tabla-cliente.html, tabla-empleado.html
│   │
│   ├── empleados/                    # RUTAS: /empleado/*
│   │   └── pedido/                   # detalle-domicilio.html, detalle-evento.html (Versión vista empleado)
│   │
│   └── usuarios/                     # RUTAS: /usuario/*
│       ├── carrito-compra.html       # Interfaz de carrito
│       ├── carta.html                # Visualización del menú público
│       ├── mis-pedidos.html          # Historial de pedidos del cliente
│       └── index-pago-factura.html   # Formulario subida de comprobantes de pago
│
└── static/
    ├── js/                           # Funciones JS Vanilla
    │   ├── carrito.js                # Lógica del frontend del carrito
    │   ├── mis-pedidos.js            # Contiene: `confirmarCancelacion(pedidoId)` usando Swal.fire()
    │   ├── pago-factura.js           # Lógica visual para alternar formularios de Nequi/Bancolombia
    │   ├── detalle-evento.js         # Interacciones en vista de detalle
    │   └── notificaciones.js         # Fetch para marcar leídas
    └── css/                          # Archivos CSS Vanilla (Sin Tailwind)
        ├── base.css                  # Estilos globales (Navbar, variables CSS, layouts)
        ├── dasboard-forms.css        # Estilos específicos para formularios y tablas del admin-panel
        └── menu-carta.css            # Grilla de la carta pública
```

## Convenciones de Código a Respetar (Para Claude)

1.  **Redirecciones (Redirects):** Al cambiar estados de pedidos en `views_pedidos.py`, siempre retornar `redirect('nombre_de_la_url', kwargs={'param': valor})` usando el `name` definido en `core/urls.py`, NO hacer returns de strings fijos.
2.  **Manejo de Formularios:** Se maneja puramente vía `<form method="POST">` y extrayendo en Python con `request.POST.get('nombre_campo')`. No se usan Django Forms (`forms.py`) extensivamente.
3.  **SweetAlert2:** Para diálogos de confirmación en el frontend (ej. borrar registro, cancelar pedido), se utiliza SweetAlert2 implementado en los `.js` estáticos. El JS crea inputs ocultos (hidden) dinámicamente y hace un `form.submit()`.
