# Análisis y Realidad del Proyecto "La Paella Real" (Correcciones para Claude)

Este documento aclara la arquitectura real y el estado actual del proyecto "La Paella Real", contrastando directamente la información errónea que presenta el manual documentado y detallando cómo funciona el código realmente.

---

## Sección 2.3 — Backend (el error más grave)
**Falso:** El manual indica que el backend usa PHP 8.2 con PHP-FPM.

**Realidad:**
1. **No hay PHP:** El proyecto está construido **100% en Python con el framework Django**. No existe un solo archivo o línea de código PHP en todo el repositorio.
2. **Versión de Django:** La versión exacta que estás utilizando en tu entorno virtual (`.venv`) es **Django 6.0.3** (la versión más reciente en desarrollo), no Django 5.x como dice el manual.
3. **Servidor WSGI:** Actualmente estás ejecutando el servidor de desarrollo local integrado de Django (`python manage.py runserver`). No hay configuraciones activas de Gunicorn, Nginx, ni mucho menos Apache/PHP-FPM, dado que estás en fase de desarrollo en Windows.

---

## Sección 4.2 — Frontend
**Falso:** El manual menciona el uso de Bootstrap 5.3.x.

**Realidad:**
1. **Cero Bootstrap o Tailwind:** El proyecto **no utiliza Bootstrap** en absoluto. Toda la interfaz de usuario está desarrollada con **Vanilla CSS** puro.
2. **Arquitectura CSS:** Tienes un sistema de estilos propio y muy organizado, basado en variables nativas de CSS (`:root`) que manejan colores, espacios, tipografías y sombras, logrando un estilo premium, glassmorfismo y modo oscuro personalizado. Todo el esfuerzo de diseño está hecho a la medida (por ejemplo, `dasboard-forms.css`).
3. **Librerías Visuales:**
   - **Íconos:** Sí se usan SVGs incrustados (estilo Heroicons o similares) y se ha configurado el uso de Boxicons en varias plantillas.
   - **Alertas:** Se utiliza **SweetAlert2** fuertemente en el frontend (recientemente encapsulado en un archivo propio llamado `premium-alerts.js` para estandarizar notificaciones emergentes muy estilizadas).
   - **Gráficos (Chart.js):** Por el momento, **no hay rastro de Chart.js** en el código. Las estadísticas mostradas actualmente en el panel se renderizan en tarjetas HTML sin gráficas de canvas u otra librería interactiva de gráficos.

---

## Sección 8 — Endpoints
**Falso:** El manual asume aplicaciones independientes con rutas como `/auth/login/` o `/reservas/agendar/`.

**Realidad:**
Toda tu arquitectura está centralizada en el archivo `core/urls.py`. Los prefijos de URL reales que organizan tu proyecto son:

- **Panel de Administración (`/admin-panel/...`):**
  - `/admin-panel/personas/`, `/admin-panel/inventario/`, `/admin-panel/pedidos/`, `/admin-panel/reportes/`, `/admin-panel/historial-ventas/`.
- **Portal de Usuario / Cliente (`/usuario/...`):**
  - `/usuario/carta/`, `/usuario/pedido/`, `/usuario/carrito/`, `/usuario/pago/`.
- **Rutas de Autenticación Raíz (`/...`):**
  - `/login/`, `/registro/`, `/logout/`.
- **API y AJAX (`/api/...`):**
  - Manejo asíncrono como carga de localidades y barrios, así como verificaciones rápidas de stock.
- **Facturación (`/factura/...`):**
  - Generación en PDF y visualización de comprobantes.

---

## Sección 9 — Persistencia / Scripts SQL
**Falso:** Se menciona lógica de base de datos directa como `procedure-stock.sql` y `trigger-stock.sql`.

**Realidad:**
1. **Lógica en Python:** **No existen Triggers ni Stored Procedures en MySQL.** Toda la lógica de "persistencia avanzada" y control de inventario (descuento de ingredientes por receta, validación de stock, etc.) está programada completamente en **Python/Django**.
2. **Ubicación:** Esta lógica se encuentra en las funciones y vistas de la carpeta `core/views/` (ej. `views_inventario.py` y `views_pedidos.py`) y en los métodos nativos del ORM de Django (`models.py`). Esto es una ventaja inmensa, pues hace que la base de datos sea agnóstica (podrías cambiar de MySQL a PostgreSQL sin reescribir triggers).

---

## Sección 13 — Diagrama de componentes
**Falso:** El manual describe múltiples apps separadas (`auth`, `restaurante`, `pedidos`, `reservas`).

**Realidad:**
El proyecto posee una **arquitectura monolítica de una sola aplicación principal llamada `core`**. 
Todos los modelos, formularios, y vistas están dentro de `restaurante/core/`. En lugar de separar las apps a nivel de framework, organizaste el código de manera modular usando archivos separados dentro de `core/views/` (ej: `views_personas.py`, `views_inventario.py`), lo cual mantiene el proyecto en un solo punto central.

---

## Integraciones Externas

- **Pagos (Stripe vs Nequi/Bancolombia):** 
  El proyecto **tiene implementado exitosamente Stripe**. Existen endpoints reales (`iniciar_pago_stripe` y `pago_exito`) que procesan pagos a través de esta pasarela. También hay soporte de lógica para subir "comprobantes" manuales en algunos flujos, pero la integración digital principal que existe en el código es Stripe.
- **Google Maps / WhatsApp Business / Twilio:**
  **Son solo ideas del manual.** Actualmente, en el código fuente no existe ninguna importación, librería, clave de API ni endpoint que haga uso de estas integraciones. No hay ruteo por mapas interactivos reales ni envío automatizado de SMS por Twilio implementados hasta este momento.

---

### Resumen para Claude:
Dile a Claude que se base **estrictamente en el código existente en la carpeta `core/`**. Que ignore cualquier referencia a PHP, Bootstrap, Chart.js, Triggers de MySQL y aplicaciones Django separadas que estén en el manual antiguo. La verdad técnica de este proyecto es que es un monolito en **Django 6.0.3, con frontend en CSS Vanilla altamente personalizado, ORM manejando la persistencia y notificaciones con SweetAlert2.**
