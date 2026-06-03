# Restaurante "La Paella Real" - Documentación Técnica Avanzada (Claude/LLM Context)

## 🥘 1. Descripción Técnica y Flujos de Negocio
Este documento contiene la lógica de negocio subyacente del sistema "La Paella Real" desarrollado en Django 6.0 y Vanilla JS. Su propósito es servir como contexto base para asistentes de IA.

### 1.1 Stack y Patrones de Arquitectura
*   **Patrón:** Monolito MVT (Model-View-Template) clásico de Django. Toda la lógica reside en la app `core`. No hay APIs REST (salvo endpoints JSON esporádicos para fetch de JS).
*   **Base de Datos:** Relacional (SQLite en dev, MySQL/Postgres en prod). Modelos fuertemente tipados con PKs personalizadas explícitas (`id_*_pk`).
*   **Frontend:** Renderizado del servidor (`render()`), con recargas de página para forms. Se usa Fetch/AJAX exclusivamente para: agregar al carrito, cancelar pedidos, notificaciones (marcar leídas). Todo el estilado es Vanilla CSS, sin Tailwind ni Bootstrap.
*   **Archivos de medios:** Imágenes subidas por usuarios manejadas a través de `media/` con `Pillow` (fotos de perfil, menús, comprobantes Bancolombia/Nequi).

### 1.2 Flujos Críticos de Negocio

#### A. Flujo de Carrito y Checkout
1.  El usuario (Cliente) navega la Carta (`Menu`) y añade items.
2.  El carrito se guarda temporalmente en la base de datos (o sesión, dependiendo de la implementación activa) y se recalcula usando JS.
3.  Al hacer *Checkout*, se crea el registro padre `Pedido` y registros hijos `DetallePedidoMenu`.
4.  El cliente debe especificar si es `domicilio` o `evento` (reserva de mesa). Se inserta un registro en la tabla correspondiente.
5.  Estado inicial del `Pedido`: `'pendiente'`.

#### B. Sincronización de Estados de Pedido
El ciclo de vida del `Pedido` (`ESTADOS`: pendiente, confirmado, preparando, listo, entregado, cancelado) es el núcleo del sistema.
*   **Evento `preparando` / `entregado`**: Cuando el admin cambia el estado, ocurre la **deducción de inventario**. El sistema lee las `RecetaMenu` de cada `Menu` en el pedido, multiplica la `cantidad_reque` por la cantidad vendida, e inserta un `ConsumoPedido` deduciendo del `stock_actual` de cada `Producto` base.
*   **Sincronización Atómica**: Si el admin cambia el `Pedido` a `'entregado'`, automáticamente:
    *   Si es Domicilio: el `estado_domi` pasa a `'entregado'`.
    *   Si es Evento: el `estado_evento` pasa a `'finalizado'`, y su `MesaEvento` asociada (`id_mesa_evento_fk`) pasa de `'ocupada'` a `'disponible'`.
*   **Cancelación**: Si el cliente o el admin cancelan el pedido, el sistema exige un `motivo_cancelacion` que se inyecta en `notas_pedido`. Se liberan las mesas si es evento, y se actualiza el estado de las tablas dependientes.

#### C. Lógica de Facturación y Pagos
1.  Al confirmar un pedido, se genera una `Factura`.
2.  El cliente selecciona `MetodoPago` (Efectivo, Nequi, Bancolombia).
3.  Si es transferencia, el cliente llena un form subiendo `comprobante_img` y datos del titular. Esto crea un registro en `Pago` con `estado_pago = 'pendiente'`.
4.  El Admin revisa el comprobante en su panel y cambia el estado a `'completado'` o `'rechazado'`.

#### D. Notificaciones Push-Like (Internas)
1.  Tabla `Notificacion` se llena automáticamente en disparadores clave (ej: Stock mínimo de producto alcanzado, nuevo pedido creado, cambio de estado de pedido, pago recibido).
2.  En el *Navbar*, un contexto global en `context_processors.py` inyecta las notificaciones no leídas (`leida = False`) según el rol del `request.session['rol']`.
3.  JS usa fetch para marcar notificaciones como leídas (`/marcar-leida-notificacion/<id>`).
