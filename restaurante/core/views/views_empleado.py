# core/views/views_empleado.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Count
from core.models import Pedido, Domicilio, Notificacion

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
    
    # Contadores de pedidos del día actual agrupados por estado, excluyendo cancelados
    pedidos_hoy = Pedido.objects.filter(fecha_pedido__date=hoy).exclude(estado_pedido='cancelado')
    
    stats = {
        'pendientes':  pedidos_hoy.filter(estado_pedido='pendiente').count(),
        'preparacion': pedidos_hoy.filter(estado_pedido='preparando').count(),
        'listos':      pedidos_hoy.filter(estado_pedido='listo').count(),
        'entregados':  pedidos_hoy.filter(estado_pedido='entregado').count(),
    }

    # Sección "Próximas entregas": pedidos con estado listo o preparando ordenados por hora_entrega_domi
    proximas_entregas = Pedido.objects.filter(
        estado_pedido__in=['preparando', 'listo'],
        domicilios_set__fecha_domi=hoy
    ).select_related('id_clien_pedido_fk').prefetch_related('domicilios_set').order_by('domicilios_set__hora_entrega_domi')

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
    fecha_str = request.GET.get('fecha', timezone.localdate().strftime('%Y-%m-%d'))
    
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    
    if estado and estado != 'todos':
        pedidos = pedidos.filter(estado_pedido=estado)
    
    if fecha_str:
        try:
            fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            pedidos = pedidos.filter(fecha_pedido__date=fecha_dt)
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
    
    # Restricción: Si el pedido tiene solicitud_cancelacion_pendiente = True,
    # el template mostrará un aviso informativo.
    
    factura = pedido.factura_set.first()
    pago = pedido.pago_set.first() or (factura.pago_set.first() if factura else None)
    
    return render(request, 'empleados/pedido/detalle-domicilio.html', {
        'pedido': pedido,
        'detalles': detalles,
        'domicilio': domicilio,
        'factura': factura,
        'pago': pago,
    })
