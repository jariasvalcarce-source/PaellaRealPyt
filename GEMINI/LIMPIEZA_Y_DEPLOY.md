# Limpieza de Entornos y Preparación para Despliegue — PaladumSys

## CONTEXTO
Varios integrantes del equipo crearon entornos virtuales distintos 
mientras trabajaban (venv, env, .venv). Antes de organizar la entrega 
final y desplegar en Railway, hay que limpiar el proyecto.

## REGLA IMPORTANTE
NO instalar dependencias en el Python global del sistema. Cada 
integrante debe seguir usando su propio entorno virtual local. 
Lo único que se comparte en el repositorio es `requirements.txt`.

---

## TAREA 1 — Buscar y reportar entornos virtuales

Busca en todo el repositorio (raíz y subcarpetas) cualquier carpeta 
que sea un entorno virtual. Identifícalas por:
- Nombres: `venv`, `env`, `.venv`, `ENV`, `virtualenv`
- O por contener internamente las carpetas `Scripts`, `Lib`, `Include` 
  (Windows) o `bin`, `lib` (Linux/Mac)

Lista todas las que encuentres con su ruta completa y su peso 
aproximado en MB antes de borrar nada.

## TAREA 2 — Verificar que están en .gitignore

Antes de eliminar nada, confirma que el `.gitignore` en la raíz 
ya incluye:
.venv/

venv/

env/

ENV/
Si falta alguna variante de las que encontraste en la Tarea 1, 
agrégala.

## TAREA 3 — Eliminar las carpetas de entornos virtuales

Elimina físicamente del proyecto todas las carpetas de entornos 
virtuales que encontraste, EXCEPTO si están siendo usadas 
activamente ahora mismo (verifica si hay algún proceso corriendo 
desde esa carpeta antes de borrar).

Si alguna ya fue commiteada por error a Git en el pasado (verificar 
con `git ls-files | findstr venv`), debe removerse del control de 
versiones:
```bash
git rm -r --cached nombre_carpeta_venv
```

## TAREA 4 — Generar requirements.txt actualizado

Genera o actualiza el archivo `requirements.txt` en la raíz de 
`restaurante/` con todas las dependencias actuales del proyecto:
```bash
pip freeze > requirements.txt
```

Verifica que incluya específicamente estas (agrégalas si faltan, 
con la versión correcta):
- Django==6.0.3
- gunicorn
- whitenoise
- mysqlclient (o PyMySQL si mysqlclient da problemas en Windows)
- python-dotenv
- dj-database-url
- stripe
- Pillow

## TAREA 5 — Checklist técnico para despliegue en Railway

Verifica y corrige cada uno de estos puntos en el proyecto:

### 5.1 — Archivo Procfile
Debe existir en `restaurante/Procfile` con el contenido:
web: gunicorn restaurante.wsgi --bind 0.0.0.0:$PORT
Si no existe, créalo. (Reemplaza `restaurante` por el nombre real 
del módulo wsgi si es diferente — verifícalo en la carpeta del 
proyecto donde está `settings.py`)

### 5.2 — settings.py — Variables de entorno
Verifica que estas líneas existan y no estén hardcodeadas:
```python
import os
import dj_database_url

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}
```
Si encuentras `SECRET_KEY` o credenciales de BD escritas directamente 
en el código, repórtalo como hallazgo crítico antes de continuar.

### 5.3 — settings.py — WhiteNoise para archivos estáticos
Verifica que `MIDDLEWARE` incluya, justo después de SecurityMiddleware:
```python
'whitenoise.middleware.WhiteNoiseMiddleware',
```
Y que existan estas configuraciones:
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 5.4 — Verificar .env no está en el repositorio
```bash
git ls-files | findstr .env
```
Debe devolver vacío. Si aparece algo, repórtalo inmediatamente 
como hallazgo crítico de seguridad sin eliminarlo todavía 
(necesito decidir si rotar credenciales).

### 5.5 — Archivo .env.example
Crea un archivo `restaurante/.env.example` (este SÍ se sube al repo, 
sin valores reales) que sirva de plantilla para el equipo:
SECRET_KEY=tu-clave-secreta-aqui

DEBUG=True

DATABASE_URL=mysql://usuario:password@localhost:3306/paladumdb

STRIPE_SECRET_KEY=tu-clave-stripe-aqui

ALLOWED_HOSTS=localhost,127.0.0.1

## REPORTE FINAL

Al terminar todas las tareas, dame un resumen con:
- Carpetas de entornos virtuales encontradas y eliminadas (con peso en MB)
- Confirmación de que .gitignore las cubre
- Confirmación de que requirements.txt está actualizado y con qué versiones clave
- Estado de cada punto del checklist 5.1 al 5.5 (✅ o ❌ con lo que falta)
- Si encontraste el .env expuesto en el repo, repórtalo de forma destacada

NO hagas commit ni push todavía. Solo deja todo listo y muéstrame 
el reporte para que yo apruebe antes de subir los cambios.