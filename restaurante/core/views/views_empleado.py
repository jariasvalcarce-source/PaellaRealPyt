# core/views/views_empleado.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Count
from core.models import Pedido, Domicilio, Notificacion, Empleado

def _check_empleado(request):
    """Valida que el usuario sea empleado."""
    if request.session.get('rol') != 'empleado':
        return False
    return True

def dashboard_empleado(request):
    """Dashboard simplificado para el empleado centrado en pedidos de hoy."""
    if not _check_empleado(request):
        if request.session.get('rol') == 'admin':
            return redirect('dashboard_admin')
        return redirect('login')

    hoy = timezone.localdate()
    
    # Contadores de pedidos activos (sin importar la fecha)
    pedidos_activos = Pedido.objects.exclude(estado_pedido__in=['cancelado', 'entregado'])
    
    stats = {
        'pendientes':  pedidos_activos.filter(estado_pedido__in=['pendiente', 'confirmado']).count(),
        'preparacion': pedidos_activos.filter(estado_pedido='preparando').count(),
        'listos':      pedidos_activos.filter(estado_pedido='listo').count(),
        # Para "entregados", mantenemos los creados/entregados hoy
        'entregados':  Pedido.objects.filter(estado_pedido='entregado', fecha_pedido__date=hoy).count(),
    }

    # Sección "Próximas entregas": pedidos activos (pendiente, confirmado, preparando, listo)
    # Mostramos todos los activos, sin importar si son de hoy o están atrasados.
    proximas_entregas = Pedido.objects.filter(
        estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo']
    ).select_related('id_clien_pedido_fk').prefetch_related('domicilios_set').order_by('-fecha_pedido')

    return render(request, 'empleados/dashboard.html', {
        'stats': stats,
        'proximas_entregas': proximas_entregas,
        'hoy': hoy,
    })

def pedidos_empleado(request):
    """Lista de pedidos domicilio con filtros por estado y fecha."""
    if not _check_empleado(request):
        return redirect('login')
    
    # Filtros: Por estado (Todos / Pendiente / Confirmado / Preparando / Listo / Entregado)
    # Por fecha (hoy por defecto)
    estado = request.GET.get('estado', 'todos')
    fecha_str = request.GET.get('fecha', '')
    
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    
    if estado and estado != 'todos':
        pedidos = pedidos.filter(estado_pedido=estado)
    
    if fecha_str:
        try:
            fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            
            # Crear rango de todo el día con timezone aware
            inicio_dia = timezone.make_aware(datetime.combine(fecha_dt, datetime.min.time()))
            fin_dia = timezone.make_aware(datetime.combine(fecha_dt, datetime.max.time()))
            
            pedidos = pedidos.filter(fecha_pedido__gte=inicio_dia, fecha_pedido__lte=fin_dia)
        except ValueError:
            pass
            
    return render(request, 'empleados/pedido/tabla-domicilio.html', {
        'pedidos': pedidos,
        'estado_actual': estado,
        'fecha_actual': fecha_str,
        'estados': Pedido.ESTADOS,
    })

def detalle_pedido_empleado(request, id_pedido):
    """Detalle del pedido con información limitada para el empleado."""
    if not _check_empleado(request):
        return redirect('login')
        
    pedido = get_object_or_404(Pedido, id_pedido_pk=id_pedido)
    detalles = pedido.detalles_set.select_related('id_menu_fk')
    domicilio = pedido.domicilios_set.first()
    
    # Auto-asignar el empleado si el pedido no tiene uno
    if not pedido.id_emple_pedido_fk:
        usuario_id = request.session.get('usuario_id')
        if usuario_id:
            empleado_actual = Empleado.objects.filter(id_auth_fk_id=usuario_id).first()
            if empleado_actual:
                pedido.id_emple_pedido_fk = empleado_actual
                pedido.save()
    
    # Restricción: Si el pedido tiene solicitud_cancelacion_pendiente = True,
    # el template mostrará un aviso informativo.
    
    factura = pedido.factura_set.first()
    pago = pedido.pago_set.first() or (factura.pago_set.first() if factura else None)
    
    from core.models import ConfiguracionSistema
    permite_empleados, _ = ConfiguracionSistema.objects.get_or_create(clave='permite_empleados_cambiar_estado', defaults={'valor_booleano': False})
    
    return render(request, 'empleados/pedido/detalle-domicilio.html', {
        'pedido': pedido,
        'detalles': detalles,
        'domicilio': domicilio,
        'factura': factura,
        'pago': pago,
        'permite_empleados_cambiar_estado': permite_empleados.valor_booleano,
    })

def mi_perfil_empleado(request):
    """Perfil del empleado: Ver y actualizar información personal."""
    usuario_id = request.session.get('usuario_id')
    if not _check_empleado(request):
        return redirect('login')
        
    try:
        from core.models import UsuarioAuth
        usuario = UsuarioAuth.objects.get(id_auth_pk=usuario_id)
        empleado = Empleado.objects.get(id_auth_fk=usuario)
    except (UsuarioAuth.DoesNotExist, Empleado.DoesNotExist):
        return redirect('login')

    if request.GET.get('reset_foto') == '1':
        if empleado.foto_empleado and empleado.foto_empleado != 'default.png':
            try:
                import os
                from django.core.files.storage import default_storage
                if default_storage.exists(empleado.foto_empleado):
                    default_storage.delete(empleado.foto_empleado)
            except Exception:
                pass
        empleado.foto_empleado = 'default.png'
        empleado.save()
        messages.success(request, "Foto eliminada correctamente.")
        return redirect('mi_perfil_empleado')

    if request.method == 'POST':
        # Solo permitimos actualizar: teléfono, dirección, foto
        tel = request.POST.get('tel_emple')
        direc = request.POST.get('direc_emple')
        
        if tel: empleado.tel_emple = tel
        if direc: empleado.direc_emple = direc
            
        foto = request.FILES.get('foto_perfil')
        if foto:
            import os
            from django.core.files.storage import default_storage
            from django.utils.text import slugify
            
            # Borrar foto anterior si no es default
            if empleado.foto_empleado and empleado.foto_empleado != 'default.png':
                if default_storage.exists(empleado.foto_empleado):
                    default_storage.delete(empleado.foto_empleado)
            
            ext = os.path.splitext(foto.name)[1]
            nom_base = f"empleado_{empleado.id_emple_pk}_{slugify(empleado.nom_emple)}"
            ruta = default_storage.save(f"fotos_perfil/{nom_base}{ext}", foto)
            empleado.foto_empleado = ruta

        empleado.save()
        messages.success(request, "Tu perfil ha sido actualizado exitosamente.")
        return redirect('mi_perfil_empleado')

    # Reutilizar el sistema de notificaciones de base_empleado si es necesario,
    # aunque normalmente base_empleado carga notificaciones por su cuenta
    
    return render(request, 'empleados/mi-perfil.html', {
        'empleado': empleado,
    })
