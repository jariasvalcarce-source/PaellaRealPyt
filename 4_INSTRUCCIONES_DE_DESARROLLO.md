# Instrucciones y Reglas de Desarrollo - La Paella Real

Este documento establece las directrices que todo desarrollador (humano o Inteligencia Artificial) debe seguir obligatoriamente al trabajar en el código base de "La Paella Real". El incumplimiento de estas reglas causará errores de arquitectura y romperá el flujo del sistema.

---

## 🏗️ 1. Flujo de Trabajo para Añadir una Nueva Funcionalidad (Ej. Una Nueva Vista)

Si necesitas crear una nueva funcionalidad, sigue **estrictamente** este orden:

1.  **Lógica del Controlador (View):**
    *   **NO** crees un nuevo archivo `views.py`. Busca el archivo existente que mejor se adapte en la carpeta `core/views/` (ej: `views_personas.py`, `views_pedidos.py`, `views_inventario.py`, etc.).
    *   Asegúrate de importar los modelos necesarios usando rutas absolutas desde core: `from core.models import ...`
    *   Maneja la protección de rutas al inicio de la función validando `request.session.get('rol')`.
2.  **Registro de Rutas (URLs):**
    *   Abre `core/urls.py`.
    *   Importa tu nueva vista en el bloque correspondiente al inicio del archivo.
    *   Añade el `path()` usando un nombre claro en el parámetro `name=''`. 
    *   **Importante:** Nunca añadas múltiples funciones dentro de un mismo `path()`.
3.  **Plantillas HTML (Templates):**
    *   Crea el archivo `.html` en la carpeta correspondiente al rol que interactuará con él (`templates/admin/`, `templates/usuarios/` o `templates/empleados/`).
    *   Extiende el layout base correcto. Usa `{% extends "base_admin.html" %}` o el equivalente para inyectar los navbars.
4.  **Estilos e Interacciones (CSS/JS):**
    *   Si la vista es compleja, NO escribas CSS inline ni etiquetas `<script>` enormes en el HTML.
    *   Crea un archivo `.js` y/o `.css` con el **mismo nombre de la plantilla** en las carpetas `static/js/` y `static/css/`.
    *   Enlázalo al final del HTML.

---

## 🚫 2. Anti-Patrones y Cosas a EVITAR (Checklist de Errores Comunes)

Para las IAs (como Claude) y humanos trabajando en este proyecto, **NUNCA** hagan lo siguiente:

*   ❌ **NO asumas que la PK de un modelo se llama `id`.** Absolutamente todos los modelos tienen un nombre explícito para su primary key finalizado en `_pk` (ej: `id_pedido_pk`, `id_clien_pk`).
*   ❌ **NO asumas que los Foreign Keys se llaman por convención estándar de Django.** Todos terminan explícitamente en `_fk` (ej: `id_clien_pedido_fk`). Si vas a crear una relación, asegúrate de ver el archivo `3_BASE_DE_DATOS.md`.
*   ❌ **NO uses rutas hardcodeadas en HTML ni en redirecciones.** 
    *   MAL: `return redirect('/admin-panel/pedidos/')`
    *   MAL: `<a href="../../admin/pedido/tabla-evento.html">`
    *   **BIEN:** `return redirect('pedidos_admin')`
    *   **BIEN:** `<a href="{% url 'tabla_eventos_admin' %}">`
*   ❌ **NO intentes reescribir con Tailwind CSS o Bootstrap.** El proyecto está estandarizado bajo **Vanilla CSS** con Flexbox/Grid y variables CSS root (en `base.css`).
*   ❌ **NO imprimas variables de 'Choices' de forma cruda en HTML.** 
    *   MAL: `{{ pedido.estado_pedido }}` -> (imprime "en_camino")
    *   **BIEN:** `{{ pedido.get_estado_pedido_display }}` -> (imprime "En Camino")

---

## 🔄 3. Reglas de Base de Datos y Migraciones

*   El archivo central y **único** de modelos es `core/models.py`.
*   Si agregas un nuevo campo a un modelo (ej. en `Pedido` o `Factura`), SIEMPRE debes proporcionar un valor por defecto (`default=...`) o permitir nulos (`null=True, blank=True`), ya que la base de datos ya tiene registros existentes.
*   Cada vez que modifiques `core/models.py`, es de cumplimiento obligatorio ejecutar:
    1.  `python manage.py makemigrations core`
    2.  `python manage.py migrate`

---

## 🎨 4. Guía de Interfaz de Usuario (UI)

*   **Iconos:** Utilizamos **Boxicons** (`<i class='bx bx-nombre'></i>`). No importes FontAwesome ni otras librerías.
*   **Formularios:** Todo el envío de datos al backend usa formularios clásicos (`<form method="POST">`) con `{% csrf_token %}`.
*   **Alertas Visuales:** Para diálogos de confirmación o modales estéticos en el Frontend, usamos **SweetAlert2**. 
*   **Mensajes Flash del Servidor:** En las vistas de Python, usa `messages.success(request, 'Mensaje')` o `messages.error(...)`. El frontend ya está preparado para renderizar estos mensajes al usuario como notificaciones temporales al recargar la página.
