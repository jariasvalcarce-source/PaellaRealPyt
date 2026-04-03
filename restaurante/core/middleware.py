"""
middleware.py — La Paella Real
Intercepta todas las respuestas de páginas protegidas y añade headers
de no-caché para que el navegador nunca almacene esas páginas.
Así, al dar "atrás" después de cerrar sesión, el browser debe
re-pedir la página al servidor, que detectará que no hay sesión
y redirigirá al login.
"""

# Rutas de páginas protegidas que nunca deben cachearse
PROTECTED_PREFIXES = (
    '/usuario/',
    '/admin-panel/',
    '/empleado/',
)


class NoCacheProtectedMiddleware:
    """
    Agrega Cache-Control: no-store a todas las respuestas de rutas
    protegidas. Esto impide que el navegador sirva la página desde
    caché después de cerrar sesión.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Solo aplica a las rutas protegidas
        if any(request.path.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma']        = 'no-cache'
            response['Expires']       = '0'

        return response
