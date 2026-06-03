# Diccionario Exacto del ORM - La Paella Real (`core/models.py`)

Para la IA: Este documento contiene el esquema **exacto** y los nombres literales de los campos definidos en `models.py`. Al generar código, **usa estrictamente estas Primary Keys, Foreign Keys y campos**.

> ⚠️ Nota crítica de diseño: Todas las llaves primarias tienen el sufijo `_pk`, y las llaves foráneas tienen el sufijo `_fk`. Además, se especifica el parámetro `db_column` explícitamente en las relaciones.

### 1. Autenticación y Personas
*   **UsuarioAuth**:
    *   PK: `id_auth_pk` (AutoField)
    *   Campos: `username`, `email`, `password`, `rol` (Choices: 'admin', 'empleado', 'cliente').
*   **Cliente**:
    *   PK: `id_clien_pk` (AutoField)
    *   FK: `id_auth_fk` (O2O a UsuarioAuth)
    *   Campos: `tipo_docu_clien` (Choices: CC, TI, NIT, CE, PAS), `num_docu_clien`, `nom_clien`, `ape_clien`, `tel_clien`, `direc_clien`.
*   *(Empleado y Proveedor siguen la misma convención: `id_emple_pk`, `id_prove_pk`)*

### 2. Inventario y Menú
*   **Producto** (Ingredientes):
    *   PK: `id_produ_pk`
    *   Campos: `nom_produ`, `stock_actual` (Decimal), `stock_minimo` (Decimal), `precio_compra` (Decimal).
    *   FKs: `id_cate_produ_fk`, `id_uni_medi_fk`, `id_prove_fk`.
*   **Menu** (Platos para venta):
    *   PK: `id_menu_pk`
    *   Campos: `nom_menu`, `precio_menu` (Decimal), `des_menu`, `img_menu`, `disponible_menu` (Bool).
    *   FK: `id_tipo_menu_fk`.
*   **RecetaMenu** (Tabla puente Menú - Producto):
    *   PK: `id_receta_pk`
    *   FKs: `id_menu_fk`, `id_produ_fk`, `id_uni_medi_fk`.
    *   Campo crítico: `cantidad_reque` (DecimalField) -> Se usa para deducción.

### 3. Pedidos (Flujo Core)
*   **Pedido** (Cabecera):
    *   PK: `id_pedido_pk`
    *   FKs: `id_clien_pedido_fk`, `id_emple_pedido_fk` (opcional).
    *   Campos críticos: 
        *   `fecha_pedido` (DateTime)
        *   `tipo_pedido` (Choices: 'domicilio', 'evento')
        *   `total_pedido` (Decimal)
        *   `notas_pedido` (CharField)
        *   `estado_pedido`: Choices exactos: `('pendiente', 'Pendiente'), ('confirmado', 'Confirmado'), ('preparando', 'Preparando'), ('listo', 'Listo'), ('entregado', 'Entregado'), ('cancelado', 'Cancelado')`.
*   **DetallePedidoMenu**:
    *   PK: `id_detalle_pk`
    *   FKs: `id_pedido_fk` (related_name='detalles_set'), `id_menu_fk`.
    *   Campos: `cant_detalle`, `precio_unitario`, `subtotal`.
*   **MesaEvento**:
    *   PK: `id_mesa_pk`
    *   Campos: `num_mesa`, `capa_mesa`, `estado_mesa` (Choices: 'disponible', 'ocupada', 'reservada').
*   **Domicilio** y **Evento** (Subtipos lógicos del Pedido):
    *   **Domicilio**: PK: `id_domi_pk`, FK: `id_pedido_domi_fk` (related_name='domicilios_set').
        *   Campos: `direc_domi`, `fecha_domi`, `hora_entrega_domi`.
        *   `estado_domi`: ('pendiente', 'en camino', 'entregado', 'cancelado').
    *   **Evento**: PK: `id_evento_pk`, FK: `id_pedido_evento_fk` (related_name='eventos_set').
        *   Campos: `fecha_evento`, `hora_inicio_evento`, `hora_fin_evento`, `cant_invi_evento`.
        *   FK a Mesa: `id_mesa_evento_fk`.
        *   `estado_evento`: ('pendiente', 'en revisión', 'aprobado', 'rechazado', 'programado', 'en progreso', 'finalizado', 'cancelado').

### 4. Pagos y Notificaciones
*   **Factura**:
    *   PK: `id_factu_pk`
    *   FKs: `id_clien_factu_fk`, `id_pedido_factu_fk`.
    *   Campos: `fecha_factu`, `total_factu`.
*   **Pago**:
    *   PK: `id_pago_pk`
    *   FKs: `id_met_pago_fk` (MetodoPago), `id_factu_pago_fk` (Factura).
    *   Campos financieros: `monto_pago`, `referencia_pago`, `comprobante_img`.
    *   Campos extra (Nequi/Bancolombia): `celular_origen`, `nombre_titular`, `monto_con_el_que_paga`.
    *   `estado_pago`: ('pendiente', 'completado', 'rechazado').
*   **Notificacion**:
    *   PK: `id_notif_pk`
    *   Campos base: `titulo`, `mensaje`, `leida` (Bool), `fecha`.
    *   Ruteo: `tipo` (categoria), `destinatario_rol`, `id_auth_destino_fk`.
    *   FKs Contextuales (allow Null): `id_pedido_fk`, `id_evento_fk`, `id_factura_fk`.

### Ejemplos Críticos de Código (Consultas ORM)
Dado un `pedido = Pedido.objects.get(id_pedido_pk=1)`:
1.  Para acceder a los ítems comprados: `menus = pedido.detalles_set.all()`
2.  Para comprobar si es domicilio y acceder a sus datos:
    ```python
    if pedido.tipo_pedido == 'domicilio':
        domi = pedido.domicilios_set.first() 
        # usar domi.direc_domi
    ```
3.  Impresión correcta de un choice en template: `{{ pedido.get_estado_pedido_display }}`. NUNCA imprimir `pedido.estado_pedido` directo si se espera un string formateado.
