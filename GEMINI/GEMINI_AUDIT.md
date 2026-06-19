# Auditoría y Limpieza del Proyecto PaladumSys

## Contexto del proyecto
- Framework: Django 6.0.3, app única llamada `core`
- Base de datos: MySQL, todos los modelos en `core/models.py`
- Vistas fragmentadas en `core/views/` (auth.py, views_personas.py, 
  views_inventario.py, views_pedidos.py, views_reportes.py)
- Frontend: Vanilla CSS + JS, sin Bootstrap ni Tailwind
- PKs con sufijo `_pk`, FKs con sufijo `_fk` en todos los modelos

## FASE 1 — Solo lectura, NO modificar nada aún
Lee todos los archivos del proyecto y genera un reporte con:
- Archivos que parecen temporales, de prueba o sin usar
- Vistas registradas en urls.py que no tienen template asociado
- Templates que existen pero no tienen ruta en urls.py
- Archivos JS o CSS en static/ que no están siendo importados en ningún template
- Imports en cualquier archivo Python que no se estén usando
- Funciones definidas pero nunca llamadas
- Comentarios TODO o FIXME pendientes
- Variables hardcodeadas que deberían estar en settings o .env

## FASE 2 — Limpieza de archivos
Solo después de mostrarme el reporte de la Fase 1 y que yo apruebe, procede a:
- Eliminar archivos temporales (archivos con nombres como test_, temp_, 
  old_, backup_, _copy, etc.)
- Eliminar templates huérfanos sin ruta asociada
- Eliminar archivos JS/CSS que no se importan en ningún template
- Eliminar imports no utilizados en todos los archivos Python
- NO eliminar ningún archivo de migraciones
- NO eliminar ningún archivo de modelos
- NO eliminar settings.py ni .env

## FASE 3 — Organización del código Python
En cada archivo de `core/views/`:
- Ordenar las funciones: primero las vistas principales, luego 
  las auxiliares (funciones que empiezan con _)
- Asegurarse de que cada función tenga exactamente un return por camino lógico
- Identificar lógica duplicada entre archivos y reportarla (no cambiarla aún)
- Verificar que todas las vistas validen `request.session.get('rol')` 
  al inicio como protección de ruta

## FASE 4 — Comentarios en partes clave
Agregar docstrings y comentarios en:
- Cada función en `core/views/views_pedidos.py` explicando 
  qué hace, qué recibe y qué retorna
- Cada función en `core/views/views_inventario.py`
- Todas las funciones auxiliares que empiezan con `_` 
  (ej: `_validar_pedido`, `_descontar_stock`, `convertir_a_unidad_base`)
- Los modelos en `core/models.py`: agregar comentario encima de 
  cada clase explicando su propósito
- Las reglas de negocio críticas: donde se descuenta stock, 
  donde se generan facturas, donde se crean notificaciones

Formato de docstring a usar:
```python
def nombre_funcion(request, param):
    """
    Descripción breve de qué hace.
    
    Parámetros:
        param: descripción
    
    Retorna:
        descripción del return
    
    Reglas de negocio:
        - Regla importante 1
        - Regla importante 2
    """
```

## FASE 5 — Verificación de validaciones
Revisa que existan validaciones en frontend Y backend para:

### Productos
- [ ] stock_actual nunca negativo (CheckConstraint en modelo)
- [ ] stock_minimo mayor a 0
- [ ] precio_compra mayor a 0
- [ ] nombre sin duplicados

### Movimientos de inventario
- [ ] cantidad mayor a 0
- [ ] fecha no futura
- [ ] fecha no más de 30 días atrás
- [ ] salida no supera stock_actual
- [ ] conversión de unidades antes de descontar

### Pedidos y carrito
- [ ] validación acumulativa de stock (no por plato individual)
- [ ] stock nunca llega a negativo al descontar
- [ ] pedido no se crea si hay stock insuficiente
- [ ] factura solo se genera al estado `entregado`
- [ ] estado no puede retroceder
- [ ] estado `entregado` y `cancelado` son finales e inamovibles

### Domicilio
- [ ] dirección mínimo 10 chars y contiene número
- [ ] fecha mínimo 2 horas en el futuro
- [ ] fecha máximo 7 días en el futuro
- [ ] hora entre 12:00 PM y 8:00 PM
- [ ] barrio obligatorio con localidad en cascada

### Proveedores
- [ ] NIT/cédula sin duplicados
- [ ] teléfono 10 dígitos empezando en 3
- [ ] email sin duplicados

### Usuarios/Clientes
- [ ] email único
- [ ] contraseña con requisitos mínimos
- [ ] rol válido (admin, empleado, cliente)

Para cada validación indica:
- ✅ Existe en frontend y backend
- ⚠️ Solo existe en un lado
- ❌ No existe en ningún lado

## FASE 6 — Reporte final
Al terminar genera un reporte con:
- Lista de archivos modificados
- Lista de archivos eliminados
- Validaciones faltantes encontradas (❌ y ⚠️)
- Lógica duplicada detectada
- Recomendaciones adicionales que notes

## Reglas que debes respetar siempre
- NUNCA usar Bootstrap ni Tailwind
- NUNCA cambiar nombres de PKs ni FKs (terminan en _pk y _fk)
- NUNCA tocar archivos de migraciones
- NUNCA hardcodear rutas, siempre usar nombres de URL de urls.py
- NUNCA eliminar el modelo UsuarioAuth ni su lógica de roles
- Preguntar antes de hacer cualquier cambio estructural en modelos
- Mostrar el reporte de cada fase antes de pasar a la siguiente