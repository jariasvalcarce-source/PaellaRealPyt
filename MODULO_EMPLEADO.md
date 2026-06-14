# Módulo de Empleado — PaladumSys

## Contexto
El empleado es el operador del restaurante. Su único foco es 
gestionar pedidos de domicilio: confirmarlos, prepararlos y 
entregarlos. No tiene acceso a información financiera, 
inventario ni configuración del sistema.

El prefijo de rutas del empleado es `/empleado/...`
La protección de rutas valida `request.session.get('rol') == 'empleado'`

---

## MÓDULO 1 — Dashboard del Empleado

### Ruta
`/empleado/dashboard/` → name: `dashboard_empleado`

### Vista: `views_empleado.py` (crear archivo nuevo en core/views/)
Función: `dashboard_empleado(request)`

### Datos a mostrar
Contadores de pedidos del día actual agrupados por estado,
excluyendo cancelados:
- Pedidos pendientes (por confirmar)
- Pedidos en preparación
- Pedidos listos para entregar
- Pedidos entregados hoy

Sección "Próximas entregas": listar los pedidos con estado
`listo` o `preparando` ordenados por `hora_entrega_domi` 
ascendente, mostrando: número de pedido, dirección de entrega
y hora programada.

### Template
`templates/empleados/dashboard.html`
Extender `base_empleado.html` (verificar que exista, si no crearlo
basándose en `base_admin.html` pero con el menú simplificado).

---

## MÓDULO 2 — Lista de Pedidos Domicilio

### Ruta
`/empleado/pedidos/` → name: `pedidos_empleado`

### Vista
Función: `pedidos_empleado(request)`

### Datos a mostrar
Tabla o tarjetas con TODOS los pedidos domicilio, ordenados
por fecha descendente. Mostrar:
- Número de pedido
- Nombre del cliente
- Dirección de entrega
- Fecha y hora de entrega programada
- Estado actual con badge de color
- Botón "Ver detalle"

### Filtros disponibles para el empleado
- Por estado (Todos / Pendiente / Confirmado / Preparando / 
  Listo / Entregado)
- Por fecha (hoy por defecto)

### Template
`templates/empleados/pedido/tabla-domicilio.html`

---

## MÓDULO 3 — Detalle del Pedido

### Ruta
`/empleado/pedidos/<int:id_pedido>/` → name: `detalle_pedido_empleado`

### Vista
Función: `detalle_pedido_empleado(request, id_pedido)`

### Datos a mostrar

**Información del cliente (limitada):**
- Nombre completo
- Teléfono
- Dirección de entrega
- Barrio
- Hora de entrega programada
- Notas especiales del pedido

NO mostrar: email, documento, historial de pedidos del cliente,
información de pago, monto de la factura.

**Platos del pedido:**
- Nombre del plato
- Cantidad
- Notas de preparación (si las hay en el detalle)

**Estado actual y cambio de estado:**
Mostrar el estado actual con badge.
Mostrar SOLO los botones de transición válidos para el empleado:

