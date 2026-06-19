# Plan de Pruebas — PaladumSys

## Contexto crítico antes de escribir cualquier prueba
- Framework: Django 6.0.3, app única `core`, sin REST Framework activo
- Autenticación: sesiones de Django (request.session['rol']), NO JWT
- No hay módulo de Eventos — fue eliminado
- No hay ventas en mesa — solo domicilios
- Las PKs terminan en `_pk`, las FKs en `_fk`
- El stock NUNCA puede ser negativo (CheckConstraint en Producto)
- El stock se descuenta SOLO cuando el pedido pasa a `preparando`
- La Factura se genera SOLO cuando el pedido pasa a `entregado`
- No hay costo de envío por distancia
- Herramienta de pruebas: pytest + pytest-django
- Base de datos de prueba: MySQL (configurada en settings)

## PASO 0 — Configuración previa

Antes de escribir las pruebas verifica:
1. Que existe `pytest.ini` o `setup.cfg` con configuración de django
2. Que `DJANGO_SETTINGS_MODULE` está configurado
3. Que existe `core/tests/__init__.py`

Si no existen, créalos:

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = restaurante.settings
python_files = tests/test_*.py
python_classes = Test*
python_functions = test_*
```

## MÓDULO 1 — Inventario (archivo: core/tests/test_inventario.py)

Escribe pruebas pytest para estos casos. Usa `@pytest.mark.django_db` 
en cada prueba. Usa el ORM de Django directamente, no endpoints REST.

### TC-01: Crear producto con datos válidos
```python
# Crear un Producto con todos los campos requeridos
# Verificar que se guardó en BD
# Verificar que stock_actual == stock_inicial ingresado
```

### TC-02: Stock actual nunca puede ser negativo
```python
# Intentar guardar un Producto con stock_actual = -1
# Debe lanzar IntegrityError por el CheckConstraint
# Verificar que no se guardó en BD
```

### TC-03: Stock mínimo debe ser mayor a 0
```python
# Intentar crear Producto con stock_minimo = 0
# Verificar que la validación lo rechaza
```

### TC-04: Nombre de producto sin duplicados
```python
# Crear Producto con nombre "Arroz Bomba"
# Intentar crear otro con el mismo nombre
# Verificar que lanza error de integridad o validación
```

### TC-05: Movimiento de entrada suma al stock
```python
# Crear Producto con stock_actual = 5.0 KG
# Registrar MovimientoInventario tipo='entrada', cantidad=3.0
# Verificar que stock_actual del producto == 8.0
```

### TC-06: Movimiento de salida resta del stock
```python
# Crear Producto con stock_actual = 10.0 KG
# Registrar salida de 4.0 KG
# Verificar que stock_actual == 6.0
```

### TC-07: Movimiento de salida no puede superar el stock
```python
# Producto con stock_actual = 2.0 KG
# Intentar registrar salida de 5.0 KG
# Verificar que se rechaza y stock sigue en 2.0
```

### TC-08: Conversión de unidades (gramos a KG)
```python
# Producto almacenado en KG con stock_actual = 1.0
# Registrar salida de 500 gramos
# Verificar que stock_actual == 0.5 KG
# Usar la función convertir_a_unidad_base de core/utils.py
```

### TC-09: Alerta de stock mínimo
```python
# Producto con stock_actual = 0.5 KG, stock_minimo = 1.0 KG
# Verificar que stock_actual <= stock_minimo (condición de alerta)
# Verificar que se creó una Notificacion con destinatario_rol='admin'
```

### TC-10: Menu se desactiva automáticamente cuando ingrediente llega a 0
```python
# Crear Producto con stock_actual = 0.1 KG
# Crear Menu que usa ese producto en su RecetaMenu
# Descontar el stock hasta 0
# Verificar que menu.disponible_menu == False
```

## MÓDULO 2 — Domicilios (archivo: core/tests/test_domicilios.py)

### TC-11: Crear domicilio con datos válidos
```python
# Crear Cliente, UsuarioAuth, Pedido con tipo='domicilio'
# Crear Domicilio asociado con dirección válida
# Verificar estado_pedido == 'pendiente'
# Verificar estado_domi == 'pendiente'
```

### TC-12: Dirección debe contener al menos un número
```python
# Intentar crear Domicilio con direc_domi = "Calle Norte"
# Verificar que la validación lo rechaza
# La dirección "Calle 80 #45-23" sí debe pasar
```

### TC-13: Fecha de entrega no puede ser en el pasado
```python
# Intentar crear Domicilio con fecha_domi = fecha de ayer
# Verificar que se rechaza
```

### TC-14: Fecha de entrega máximo 7 días en el futuro
```python
# Intentar crear Domicilio con fecha 8 días en el futuro
# Verificar que se rechaza
```

### TC-15: Hora de entrega debe estar entre 12PM y 8PM
```python
# Intentar con hora_entrega_domi = 09:00 → debe rechazarse
# Intentar con hora_entrega_domi = 21:00 → debe rechazarse
# Intentar con hora_entrega_domi = 14:00 → debe aceptarse
```

### TC-16: Transición de estado válida
```python
# Pedido en 'pendiente' → cambiar a 'confirmado'
# Verificar que el cambio se guardó
```

### TC-17: Transición de estado inválida
```python
# Pedido en 'entregado' → intentar cambiar a 'pendiente'
# Verificar que se lanza error y el estado no cambia
```

### TC-18: Estado 'entregado' es final e inamovible
```python
# Pedido en 'entregado'
# Intentar cualquier cambio de estado
# Verificar que siempre se rechaza
```

### TC-19: Cancelación solo disponible antes de 'preparando'
```python
# Pedido en 'preparando' → intentar cancelar
# Verificar que se rechaza
# Pedido en 'confirmado' → cancelar → debe funcionar
```

### TC-20: Al cancelar, estado_domi también cambia a 'cancelado'
```python
# Pedido con domicilio asociado en estado 'confirmado'
# Cancelar el pedido
# Verificar pedido.estado_pedido == 'cancelado'
# Verificar domicilio.estado_domi == 'cancelado'
```

## MÓDULO 3 — Pedidos y Stock (archivo: core/tests/test_pedidos.py)

### TC-21: Stock se descuenta al pasar a 'preparando'
```python
# Producto con stock_actual = 10.0 KG
# Menu con RecetaMenu que requiere 2.0 KG de ese producto
# Crear Pedido con 1 unidad de ese Menu
# Cambiar estado a 'preparando'
# Verificar stock_actual == 8.0 KG
```

### TC-22: Stock NO se descuenta al pasar a 'confirmado'
```python
# Mismo setup anterior
# Cambiar estado a 'confirmado'
# Verificar que stock_actual sigue igual (sin cambio)
```

### TC-23: Stock nunca llega a negativo al descontar
```python
# Producto con stock_actual = 0.5 KG
# Menu que requiere 2.0 KG
# Pedido con ese Menu
# Cambiar estado a 'preparando'
# Verificar stock_actual == 0 (nunca negativo)
# Verificar que se creó Notificacion de stock crítico
```

### TC-24: Validación acumulativa del carrito
```python
# Producto con stock_actual = 1.0 KG
# Menu A requiere 0.6 KG, Menu B requiere 0.6 KG (mismo ingrediente)
# Carrito con 1 Menu A + 1 Menu B = necesita 1.2 KG
# Verificar que la validación rechaza el carrito completo
# (aunque individualmente cada uno pasaría la validación)
```

### TC-25: Factura se genera SOLO al estado 'entregado'
```python
# Pedido pasar por: pendiente → confirmado → preparando → listo
# Verificar que NO existe Factura en ninguno de esos estados
# Cambiar a 'entregado'
# Verificar que SÍ se creó exactamente 1 Factura
```

### TC-26: Pedido cancelado no genera factura
```python
# Pedido en 'confirmado' → cancelar
# Verificar que no existe ninguna Factura para ese pedido
```

### TC-27: solicitud_cancelacion_pendiente funciona correctamente
```python
# Pedido en 'confirmado' con más de 30 minutos
# Cliente activa solicitud de cancelación
# Verificar solicitud_cancelacion_pendiente == True
# Verificar que el estado_pedido NO cambió (sigue 'confirmado')
# Verificar que se creó Notificacion para el admin
```

### TC-28: Notificaciones se generan en cambios de estado
```python
# Pedido en 'pendiente' → cambiar a 'confirmado'
# Verificar que se creó Notificacion para el cliente
# con el mensaje correcto de confirmación
```

## PRUEBAS DE INTEGRACIÓN (archivo: core/tests/test_integracion.py)

Estas pruebas usan Django TestClient con sesiones, NO JWT.

### TC-29: Solo admin puede acceder al panel de admin
```python
# Crear usuario con rol='cliente'
# Intentar GET /admin-panel/inventario/
# Verificar redirect o 403
# Crear usuario con rol='admin'
# Hacer login (POST /login/ con credenciales)
# Intentar GET /admin-panel/inventario/
# Verificar 200
```

### TC-30: Solo empleado puede acceder a rutas de empleado
```python
# Usuario con rol='cliente' → GET /empleado/pedidos/ → bloqueado
# Usuario con rol='empleado' → GET /empleado/pedidos/ → 200
```

### TC-31: Flujo completo de pedido domicilio
```python
# 1. Cliente hace login
# 2. Agrega plato al carrito (POST al endpoint de carrito)
# 3. Crea pedido con datos de domicilio válidos
# 4. Admin cambia estado a confirmado
# 5. Admin cambia estado a preparando → verificar descuento de stock
# 6. Admin cambia estado a listo
# 7. Admin cambia estado a entregado → verificar creación de factura
# Verificar cada estado en BD en cada paso
```

### TC-32: Flujo de pago con transferencia
```python
# 1. Pedido creado
# 2. Cliente selecciona Bancolombia
# 3. Se crea Pago con estado='pendiente', asociado al Pedido
# 4. NO existe Factura aún
# 5. Admin aprueba el comprobante → estado_pago='completado'
# 6. Admin marca entregado → se genera Factura
# 7. Verificar que Pago queda vinculado a la Factura
```

### TC-33: Menu no disponible no puede agregarse al carrito
```python
# Menu con disponible_menu=False
# Cliente intenta agregarlo al carrito
# Verificar que se rechaza con mensaje apropiado
```

## PRUEBAS DE CARGA (instrucciones JMeter)

Las pruebas de carga se hacen contra el sistema desplegado en Railway.
NO se hacen con pytest. Documentar los pasos para ejecutarlas en JMeter:

Genera un archivo `JMETER_INSTRUCCIONES.md` con:
1. Configuración del Thread Group para 3 usuarios simultáneos
2. Endpoints a probar:
   - GET /usuario/carta/ (carta pública)
   - POST /login/ 
   - GET /admin-panel/inventario/ (con sesión admin)
   - GET /admin-panel/pedidos/
3. Criterios de éxito: respuesta < 2 segundos, 0% errores
4. Cómo exportar el reporte HTML desde JMeter

## INSTRUCCIONES DE EJECUCIÓN

Una vez escritas todas las pruebas, ejecutar en este orden:

```bash
# 1. Verificar configuración
python manage.py check

# 2. Ejecutar todas las pruebas con cobertura
pytest --cov=core --cov-report=html -v

# 3. Ver reporte de cobertura
# Abrir htmlcov/index.html en el navegador

# 4. Si alguna prueba falla, mostrar detalle completo
pytest --cov=core -v --tb=long 2>&1 | tee resultados_pruebas.txt
```

## MATRIZ DE RESULTADOS

Al terminar de ejecutar, genera un archivo `MATRIZ_RESULTADOS.md` con:
- TC-ID
- Descripción
- Resultado obtenido
- ¿Pasó? SÍ/NO
- Fecha de ejecución

## REGLAS IMPORTANTES
- Usar @pytest.mark.django_db en TODAS las pruebas que toquen BD
- NO hardcodear IDs, siempre crear objetos frescos en cada prueba
- Cada prueba debe ser independiente (no depende de otra)
- Usar factory_boy o fixtures de pytest para crear datos de prueba
- NO usar endpoints REST, usar el ORM directamente en pruebas unitarias
- Para pruebas de integración usar django.test.Client con login por sesión
- Los nombres de campos deben coincidir EXACTAMENTE con core/models.py
  (leer el archivo antes de escribir cualquier prueba)