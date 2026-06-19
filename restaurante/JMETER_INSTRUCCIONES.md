# Instrucciones para Pruebas de Carga con JMeter — PaladumSys

Estas pruebas están diseñadas para ejecutarse contra el sistema desplegado (ej. Railway).

## 1. Configuración del Thread Group
- **Número de hilos (usuarios):** 3
- **Ramp-up period (segundos):** 5
- **Loop Count:** 10

## 2. Endpoints a Probar
1. **Carta Pública:** `GET /usuario/carta/`
2. **Login Admin:** `POST /login/` (usar credenciales válidas en Body Data: `usuario=admin&contrasena=12345`)
3. **Panel Inventario (con sesión):** `GET /admin-panel/inventario/`
4. **Panel Pedidos (con sesión):** `GET /admin-panel/pedidos/`

## 3. Criterios de Éxito
- **Tiempo de respuesta:** < 2000ms (2 segundos) para el 90% de las peticiones.
- **Tasa de error:** 0% de errores (todas las respuestas deben ser 200 OK o redirecciones válidas).

## 4. Cómo ejecutar y generar el reporte
Ejecuta JMeter desde la línea de comandos para obtener mejores resultados:

```bash
jmeter -n -t Pruebas_NoFuncionales.jmx -l resultados.jtl -e -o reporte_html/
```

- `-n`: Modo no-GUI
- `-t`: Archivo .jmx de entrada
- `-l`: Archivo de resultados log
- `-e`: Generar reporte dashboard
- `-o`: Carpeta de salida para el reporte HTML
