import json
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.views.decorators.csrf import csrf_exempt
from core.models import UsuarioAuth

class CustomJWTAuthentication(JWTAuthentication):
    """
    Decodifica el Token y busca al usuario en nuestra tabla UsuarioAuth
    en lugar de la tabla auth_user de Django.
    """
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')
        try:
            usuario = UsuarioAuth.objects.get(id_auth_pk=user_id)
            if not usuario.activo:
                raise AuthenticationFailed('El usuario está inactivo.', code='user_inactive')
            
            # DRF requires the user object to have an `is_authenticated` property
            usuario.is_authenticated = True 
            return usuario
        except UsuarioAuth.DoesNotExist:
            raise AuthenticationFailed('Usuario no encontrado', code='user_not_found')

@csrf_exempt
def login_api(request):
    """
    Endpoint para autenticarse en la API.
    Recibe un JSON con = { "username": "...", "password": "..." }
    Y devuelve los tokens Access y Refresh.
    """
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido. Usa POST.'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'ok': False, 'error': 'Debes enviar username y password.'}, status=400)

        usuario = UsuarioAuth.objects.filter(nombre_usuario=username).first()

        if usuario and usuario.activo and usuario.check_password(password):
            # Usuario válido. Generamos el JWT.
            # Aseguramos que la propiedad 'id' apunte al PK para que simplejwt funcione nativamente 
            # (aunque definiremos USER_ID_FIELD='id_auth_pk' en settings)
            refresh = RefreshToken.for_user(usuario)
            
            return JsonResponse({
                'ok': True,
                'rol': usuario.rol.name,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        else:
            return JsonResponse({'ok': False, 'error': 'Credenciales inválidas.'}, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'JSON inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
