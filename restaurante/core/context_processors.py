from core.models import Notificacion
from django.db.models import Q

def notificaciones_globales(request):
    ctx = {}
    rol = request.session.get('rol')
    usuario_id = request.session.get('usuario_id')

    if rol in ['admin', 'empleado']:
        notif_list = Notificacion.objects.filter(
            destinatario_rol=rol
        ).order_by('-fecha')[:10]
        cant_noleidas = Notificacion.objects.filter(
            destinatario_rol=rol, leida=False
        ).count()
        ctx['notificaciones'] = notif_list
        ctx['cant_notificaciones'] = cant_noleidas
    
    if usuario_id:
        # Notificaciones del usuario cliente (leídas y no leídas) para mostrar en el dropdown
        notif_cliente = Notificacion.objects.filter(
            Q(id_auth_destino_fk_id=usuario_id) |
            Q(destinatario_rol='cliente', id_auth_destino_fk__isnull=True)
        ).order_by('-fecha')[:5]  # Últimas 5
        cant_noleidas_cliente = Notificacion.objects.filter(
            Q(id_auth_destino_fk_id=usuario_id) |
            Q(destinatario_rol='cliente', id_auth_destino_fk__isnull=True),
            leida=False
        ).count()
        ctx['notif_cliente_list'] = notif_cliente
        ctx['cant_noleidas_cliente'] = cant_noleidas_cliente
        
        from core.models import Cliente
        try:
            ctx['cliente_global'] = Cliente.objects.get(id_auth_fk_id=usuario_id)
        except Cliente.DoesNotExist:
            pass

    return ctx
