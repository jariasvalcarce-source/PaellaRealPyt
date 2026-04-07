# 📋 Guía Técnica del Proyecto: Arquitectura, APIs y Lógica de Negocio (Para el Equipo Scrum)

Este documento centraliza las decisiones técnicas, herramientas y flujos de trabajo implementados en el proyecto **La Paella Real**. Está diseñado para explicar de manera clara y profesional cómo está construido el backend, con especial énfasis en el ecosistema de APIs.

---

## 🏗️ 1. Estructura y Organización del Proyecto (Arquitectura MVT)

Nuestra aplicación está construida sobre Django, el cual usa un modelo arquitectónico conocido como **MVT (Model-View-Template)**. Para evitar que el código se convirtiera en un "código espagueti" conforme fuimos agregando las APIs y pasarelas, modularizamos el árbol de archivos así:

```text
restaurante/
├── 📁 .env                    # (NUEVO) Archivo oculto con las llaves de seguridad de Stripe y BD.
├── 📁 _archivos_soporte/      # (NUEVO) Carpeta de aislamiento. Contiene todos los .csv y logs del sistema.
├── 📁 restaurante/            # Directorio cerebral de Django (Configuraciones, settings.py, WSGI).
├── 📁 templates/              # Interfaces gráficas. Páginas divididas por roles (admin, empleado, usuarios, auth).
├── 📁 static/                 # Archivos estáticos: Nuestro CSS, imágenes y Javascripts locales (Ej: pago-factura.js).
└── 📁 core/                   # El corazón de nuestra aplicación. Toda la lógica de negocio vive aquí.
    ├── 📜 models.py           # ¡Nuestra Base de Datos en Python! Aquí definimos tablas, relaciones y validaciones (ORM).
    ├── 📁 api/                # (NUEVO) Submódulo API. Aislamos DRF del código tradicional perezoso.
    │   ├── 📜 serializers.py  # Traductores: Convierten objetos complejos Python a JSON puro.
    │   └── 📜 urls.py         # Enrutador exclusivo de peticiones REST/API (Empiezan por /api/...).
    ├── 📁 views/              # La lógica del software hiper-modularizada.
    │   ├── 📜 views.py        # Controladores estandar y navegación del sistema.
    │   ├── 📜 views_pedidos.py# Lógica cruda de domicilios, facturas, eventos y sincronización de inventario.
    │   └── 📜 views_api.py    # (NUEVO) Controladores API y el Webhook de Stripe.
```

<details>
<summary><b>🌳 HAGA CLIC AQUÍ para ver el Árbol de Carpetas Completo del Proyecto</b></summary>

```text
restaurante/
├── .env
├── manage.py
├── core/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api_auth.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── views/
│   │   ├── views.py
│   │   ├── views_api.py
│   │   └── views_pedidos.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── context_processors.py
├── restaurante/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── static/
│   ├── css/          # (+20 archivos de estilos modulares)
│   ├── img/          # (Assets gráficos, iconos de Stripe, etc.)
│   └── js/           # (Scripts Vanilla: validaciones, pago-factura.js)
├── templates/
│   ├── admin/        # Dashboard maestro, módulos de inventario, facturación, y mesas.
│   ├── empleado/     # Interfaz controlada para el staff interno.
│   ├── usuarios/     # (El Front-End del cliente: Carrito, Perfil, Pasarela de Pagos)
│   ├── inicio.html   # Homepage Principal
│   └── login.html    # Sistema de Autenticación
└── _archivos_soporte/
    ├── clientes_carga_masiva.csv
    ├── menus_carga_masiva.csv
    ├── movimientos_carga_masiva.csv
    ├── pedidos_carga_masiva.csv
    ├── productos_carga_masiva.csv
    └── proveedores_carga_masiva.csv
```
</details>

**Beneficios de esta arquitectura para el equipo:**
1. **Separación de Responsabilidades (SoC):** Si falla la API, sabemos que el error está en `core/api`, si falla la web, está en `templates` o `views.py`.
2. **Escalabilidad:** Separar `_archivos_soporte/` mantiene la raíz del proyecto inmaculada, lo que es vital para futuros despliegues a servidores como AWS o Heroku.
3. **Mantenibilidad:** Dividir las vistas (Views) en archivos especializados (`views_pedidos`, `views_api`) previene que tengamos archivos infinitos de 5,000 líneas que sean imposibles de debugear.

---

## 🌐 2. ¿Qué son las APIs y por qué las usamos?

Las **API (Application Programming Interface)** son los "puentes" que permiten que dos sistemas de software se comuniquen entre sí. En lugar de que el servidor solo escupa "páginas web visuales" (HTML), una API le permite al servidor entregar **Datos Puros (en formato JSON)** a cualquier plataforma externa (un cliente móvil, la terminal inteligente de un cajero, Postman o un servicio de reportes externo).

Para crear nuestras APIs Internas integramos la librería **Django REST Framework (DRF)**. DRF nos provee herramientas potentes como los **Serializadores**, que se encargan de convertir nuestros Modelos de Bases de Datos complejos a cadenas de texto plano JSON, y viceversa, con un par de líneas de código.

### 🛠️ Métodos Estándares REST (Ejemplos con Postman)

En Postman, nosotros consumimos nuestras propias APIs usando los **Métodos HTTP**:

1. **`GET` (Lectura)**: *Ejemplo:* Consultar `/api/empleados/`. La API va a la base de datos, recopila los empleados y nos devuelve un JSON gigante con todos los nombres sin modificar absolutamente nada.
2. **`POST` (Creación)**: Se usa para insertar un nuevo registro. *Ejemplo:* Le enviamos un bloque JSON con los datos de un nuevo cliente a `/api/clientes/crear/`. La API intercepta esto, valida que vengan todos los datos requeridos, y lo inserta en MySQL.
3. **`PUT` o `PATCH` (Actualización)**: Se usa para editar algo que ya existe (Ej: Editar el correo o el teléfono de un cliente filtrando por su ID).
4. **`DELETE` (Eliminación)**: Elimina el recurso basado en un ID.

---

## 🗃️ 3. Cargas Masivas e Integración de Pandas

Teníamos la necesidad de importar cientos o miles de registros históricos a la vez mediante archivos `.csv`. Hacer esto "a mano" o insertando fila por fila saturaría la memoria del servidor. 

**¿Cómo se abordó?**
Utilizamos la librería externa **Pandas** (`pip install pandas`). Pandas es un motor de análisis de datos hiper-optimizado escrito en *C* disfrazado de Python. 
1. Absorbe el archivo importado al instante como un *Dataframe* (como una tabla de Excel en memoria RAM).
2. Valida formatos (fecha, correos, tipos de datos) limpiando la basura masivamente.
3. Utilizamos la función nativa de Django `bulk_create()`, la cual toma todos los datos de Pandas y mediante de **un solo viaje o query** a MySQL, guarda miles de registros en 1 segundo.

---

## 💳 4. Las APIs Externas: La Pasarela de Pagos Stripe

Una **API Externa** es cuando _nuestro servidor_ se vuelve el cliente y se comunica con el servidor inteligente de otra empresa grande, como Google, Meta o bancos. Nosotros implementamos **Stripe**, un gigante financiero de procesamiento de tarjetas de crédito.

**¿Cómo funciona la integración de Stripe?**
1. **Llamada de Checkout**: Cuando el cliente da click en "Pagar con Stripe", le mandamos a la API Externa de Stripe el monto total ($570,000) de su carrito.
2. **Sesión Aislada:** Stripe nos responde con una "URL Segura Temporal" (Checkout Session) hospedada en los servidores del banco, blindada con encripción real PCI. Redirigimos al usuario para que ponga su tarjeta ahí, así nosotros nos libramos de la responsabilidad legal de tocar sus números bancarios.
3. **¿Qué es un Webhook?**: Como el pago sucede allá en las oficinas digitales de Stripe, Stripe necesita avisarnos. Creamos una ruta especial, invisible a los humanos, llamada **Webhook** (`/api/stripe/webhook/`). Tan pronto como se debita la tarjeta exitosamente, Stripe "nos llama a ese teléfono (nuestra API)" pasándonos un mensaje secreto diciendo "*¡Aprobado para el pedido 37!*".
4. **Respuesta Automática**: Nuestro Webhook detecta el mensaje, va a MySQL, cambia el estado del Pedido automáticamente a "Completado" y genera su Factura de Pago en milisegundos.

---

## 🔒 5. Seguridad de las APIs y `.env` (python-dotenv)

Con Stripe, se generan dos llaves importantes: la `Public Key` (llave pública) y la `Secret Key` (llave bancaria secreta).
Si un hacker se roba la llave secreta en el código fuente (GitHub), nos vacían la cuenta.

**Para arreglarlo, aplicamos las mejores prácticas de Ciberseguridad de la industria:**
Añadimos **Variables de Entorno (`.env`)**. Las variables de entorno consisten en un archivo fantasma de texto (`.env`) donde se alojan las contraseñas reales. En el código (`settings.py`) en lugar de poner la contraseña quemada en letras, instalamos la librería `python-dotenv` obligando al código a ponerse unas "gafas" que solo leen las llaves contenidas en ese archivo local; archivo que **anulamos explícitamente en el Gitignore** (`.gitignore`), prohibiéndole al motor de control de versiones subir tus contraseñas a la internet.

---

## ⚖️ 6. Lógica de Conversiones e Ingeniería de Inventarios (Kg, Lt, Gr)

Uno de los mayores retos en la arquitectura del sistema de compras e inventarios de un Restaurante, es el conflicto de proporciones: 

**El Problema:** Tus administradores le compran al Proveedor el pescado o el arroz al por mayor **(en Kilogramos o Litros)**. Pero la Cocina lo gasta en porciones enanas para preparar los platos **(en gramos o mililitros)**.

**La Solución Lógica Implementada:**
1. **Inventario Primario (Ingresos)**: Para evitar dolores de cabeza y miles de ceros con los administradores en el módulo contable, diseñamos la base de datos para registrar los ingresos usando la "Nomenclatura Mayor" (*Ej: Entraron 5 kg de Arroz Bomba*).
2. **Disminución Continua (Recetas)**: El sistema que diseñamos abstrae que **1 kg = 1000 gr**. Si el Chef crea una receta indicando que requiere *400 gr* de Pollo, la programación interna convierte esos 400 gr multiplicándolos por una fracción ($400 / 1000 = 0.40$).
3. Al vender la paella, nuestro sistema inteligente extrae del inventario exactamente `0.40 Kg`, permitiéndonos tener mediciones atómicas exactas al milímetro y previniendo el agotamiento del control de stock a un decimal de perfección matemática. Disminuyen dinámicamente y sabemos perfectamente cuándo reabastecer en el panel de alertas.
