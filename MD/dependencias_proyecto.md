# Dependencias y Librerías del Proyecto

## ¿Existe un archivo `requirements.txt`?
Actualmente, **no existe** un archivo `requirements.txt` estructurado en la raíz del proyecto. Las dependencias están instaladas directamente en el entorno virtual (`.venv`). 

Sin embargo, a partir de los paquetes instalados en tu entorno virtual, las principales librerías que está utilizando el proyecto son:

### 1. Framework Principal
- **Django (6.0.3):** El motor principal del backend.

### 2. Base de Datos
- **mysqlclient (2.2.8):** El conector principal oficial en C para MySQL en Django.
- **PyMySQL (1.1.2):** Otro conector en Python puro para MySQL (posiblemente usado de respaldo o por otra herramienta).

### 3. API y Autenticación
- **djangorestframework (3.17.1):** Utilizado para construir los endpoints de la API (por ejemplo, para el manejo asíncrono del stock o barrios).
- **djangorestframework-simplejwt (5.5.1):** Manejo de autenticación por tokens JWT en la API.
- **PyJWT (2.12.1):** Dependencia subyacente para los JSON Web Tokens.

### 4. Integraciones y Variables de Entorno
- **stripe (15.1.0):** El SDK oficial de Stripe para el procesamiento de pagos.
- **python-dotenv (1.2.2):** Para cargar y leer las variables de entorno de tu archivo `.env` de forma segura.
- **requests (2.34.0):** Para realizar peticiones HTTP a APIs externas si es necesario.

### 5. Análisis de Datos
- **pandas (3.0.3):** Poderosa librería para manipulación y análisis de datos tabulares.
- **numpy (2.4.4):** Librería matemática requerida frecuentemente por pandas.

### 6. Multimedia
- **Pillow (12.2.0):** Librería de procesamiento de imágenes, fundamental porque tienes campos `ImageField` en Django para los productos y avatares.

### 7. Testing
- **pytest (9.0.3):** Framework de pruebas avanzado.
- **pytest-django (4.12.0):** Integración de pytest específicamente con el entorno y la base de datos de Django.

---

> **Recomendación:** Es muy importante generar el archivo `requirements.txt` oficial para facilitar los despliegues y a otros desarrolladores. Puedes generarlo ejecutando el comando:
> `python -m pip freeze > requirements.txt` 
> dentro de la carpeta `restaurante`.
