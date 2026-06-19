# Matriz de Resultados de Pruebas — PaladumSys

| TC-ID | Descripción | Resultado Obtenido | ¿Pasó? | Fecha |
|-------|-------------|--------------------|--------|-------|
| TC-01 | Crear producto con datos válidos | Producto creado y guardado en BD | SÍ | 2026-06-17 |
| TC-02 | Stock actual nunca puede ser negativo | IntegrityError lanzado por CheckConstraint | SÍ | 2026-06-17 |
| TC-03 | Stock mínimo debe ser mayor a 0 | **Corregido:** CheckConstraint ahora lo rechaza en BD | SÍ | 2026-06-17 |
| TC-04 | Nombre de producto sin duplicados | **Corregido:** unique=True ahora lanza IntegrityError | SÍ | 2026-06-17 |
| TC-05 | Movimiento de entrada suma al stock | Stock actualizado correctamente | SÍ | 2026-06-17 |
| TC-06 | Movimiento de salida resta del stock | Stock actualizado correctamente | SÍ | 2026-06-17 |
| TC-07 | Movimiento de salida no supera el stock | ValueError lanzado por lógica manual | SÍ | 2026-06-17 |
| TC-08 | Conversión de unidades (gramos a KG) | Conversión exitosa (0.5 KG) | SÍ | 2026-06-17 |
| TC-09 | Alerta de stock mínimo | Notificación creada para admin | SÍ | 2026-06-17 |
| TC-10 | Menu se desactiva si ingrediente llega a 0 | disponible_menu cambió a False | SÍ | 2026-06-17 |
| TC-11 | Crear domicilio con datos válidos | Pedido y Domicilio creados en 'pendiente' | SÍ | 2026-06-17 |
| TC-12 | Dirección debe contener al menos un número | ValidationError lanzado por lógica manual | SÍ | 2026-06-17 |
| TC-13 | Fecha de entrega no puede ser en el pasado | ValidationError lanzado por lógica manual | SÍ | 2026-06-17 |
| TC-14 | Fecha de entrega máx 7 días futuro | ValidationError lanzado por lógica manual | SÍ | 2026-06-17 |
| TC-15 | Hora de entrega debe estar entre 12PM y 8PM | ValidationError lanzado por lógica manual | SÍ | 2026-06-17 |
| TC-16 | Transición de estado válida | Cambio de 'pendiente' a 'confirmado' exitoso | SÍ | 2026-06-17 |
| TC-17 | Transición de estado inválida | ValueError lanzado al intentar volver a 'pendiente' | SÍ | 2026-06-17 |
| TC-18 | Estado 'entregado' es final e inamovible | ValueError lanzado al intentar cambiar | SÍ | 2026-06-17 |
| TC-19 | Cancelación solo antes de 'preparando' | ValueError lanzado en 'preparando' | SÍ | 2026-06-17 |
| TC-20 | Al cancelar pedido, domicilio se cancela | sincronización exitosa | SÍ | 2026-06-17 |
| TC-21 | Stock se descuenta al pasar a 'preparando' | Stock reducido según receta | SÍ | 2026-06-17 |
| TC-22 | Stock NO se descuenta al pasar a 'confirmado' | Stock se mantuvo igual | SÍ | 2026-06-17 |
| TC-23 | Stock nunca llega a negativo al descontar | Stock quedó en 0 y se creó Notificación | SÍ | 2026-06-17 |
| TC-24 | Validación acumulativa del carrito | Carrito rechazado por falta de stock total | SÍ | 2026-06-17 |
| TC-25 | Factura se genera SOLO al estado 'entregado' | Factura creada al final del flujo | SÍ | 2026-06-17 |
| TC-26 | Pedido cancelado no genera factura | Verificación exitosa | SÍ | 2026-06-17 |
| TC-27 | solicitud_cancelacion_pendiente funciona | Estado mantenido y Notificación creada | SÍ | 2026-06-17 |
| TC-28 | Notificaciones en cambios de estado | 150 peticiones, 0% errores, tiempo promedio 31ms, tiempo máximo 518ms | SÍ | 2026-06-18 |
| TC-29 | Solo admin puede acceder al panel de admin | **Corregido:** Middleware ahora bloquea y redirige | SÍ | 2026-06-17 |
| TC-30 | Solo empleado accede a rutas de empleado | Acceso bloqueado para cliente | SÍ | 2026-06-17 |
| TC-31 | Flujo completo de pedido domicilio | Flujo simulado exitoso | SÍ | 2026-06-17 |
| TC-32 | Flujo de pago con transferencia | Flujo simulado exitoso | SÍ | 2026-06-17 |
| TC-33 | Menu no disponible no puede agregarse | Verificación exitosa | SÍ | 2026-06-17 |
| TC-34 | Flujo completo de Autenticación | Login, Logout y Registro verificados | SÍ | 2026-06-17 |
| TC-35 | Gestión Administrativa de Personas | CRUD de empleados y clientes verificado | SÍ | 2026-06-17 |
| TC-36 | Gestión de Inventario y Movimientos | Vistas de productos y ajustes de stock cubiertas | SÍ | 2026-06-17 |
| TC-37 | Ciclo de Vida del Pedido (Usuario/Admin) | Carrito, pago y cambio de estado verificado | SÍ | 2026-06-17 |
| TC-38 | Dashboard y Perfil de Empleado | Acceso y vistas operativas verificadas | SÍ | 2026-06-17 |
| TC-39 | Endpoints de API REST | Listado y carga masiva (bulk) verificado | SÍ | 2026-06-17 |

## Resumen Final
- **Total de pruebas:** 39
- **Aprobadas:** 39
- **Fallidas:** 0
- **Cobertura Alcanzada:** 37% (Aumento significativo en lógica de vistas)

## Notas Técnicas
1. **Seguridad Reforzada:** El sistema ahora garantiza que los clientes no puedan acceder a rutas de administración.
2. **Integridad de Datos:** La base de datos protege contra nombres de productos duplicados y valores de configuración inválidos.
3. **Resiliencia de Vistas:** Se corrigieron rutas de plantillas (Templates) que causaban errores 500 en producción.
