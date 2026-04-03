from .models import Notificacion

def notificaciones_globales(request):
    if request.session.get('rol') == 'admin':
        notificaciones = Notificacion.objects.filter(leida=False).order_by('-fecha')[:10]
        cant_notificaciones = Notificacion.objects.filter(leida=False).count()
        return {
            'notificaciones': notificaciones,
            'cant_notificaciones': cant_notificaciones
        }
    return {}
