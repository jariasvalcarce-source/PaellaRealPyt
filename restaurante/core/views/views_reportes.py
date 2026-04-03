from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import calendar
from django.db.models.functions import ExtractMonth, ExtractWeekDay

from ..models import Pedido, DetallePedidoMenu, Pago

def reportes_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
        
    hoy = timezone.now()
    fecha_inicio_semana = hoy - timedelta(days=hoy.weekday())
    
    # 1. Ventas Semanales (Lunes a Domingo actual)
    ventas_semana_query = Pago.objects.filter(
        estado_pago='aprobado',
        fecha_pago__gte=fecha_inicio_semana
    ).annotate(
        dia_semana=ExtractWeekDay('fecha_pago')
    ).values('dia_semana').annotate(total=Sum('monto_pago')).order_by('dia_semana')
    
    # Convertir a estructura para Chart.js (Dom=1, ..., Sab=7) -> (Lun, Mar, Mie...)
    # Ajuste: ExtractWeekDay en MySQL: 1 = Domingo, 2 = Lunes, ..., 7 = Sabado
    dias_nombres = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
    ventas_semana_labels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    ventas_semana_datos = [0] * 7
    
    for v in ventas_semana_query:
        # v['dia_semana'] devuelve 1-7
        # Queremos index 0 para Lunes, 6 para Domingo.
        dia_db = v['dia_semana']
        if dia_db == 1: idx = 6 # Dom
        else: idx = dia_db - 2  # Lun=2->0, Sáb=7->5
        ventas_semana_datos[idx] = float(v['total'] or 0)
        
    # 2. Top 5 Platos Más Vendidos (Todos los tiempos o del mes)
    top_platos = DetallePedidoMenu.objects.filter(
        id_pedido_fk__estado_pedido__in=['entregado','confirmado','preparando','listo','pendiente']
    ).values('id_menu_fk__nom_menu').annotate(
        cantidad_vendida=Sum('cant_detalle')
    ).order_by('-cantidad_vendida')[:5]
    
    top_platos_labels = [p['id_menu_fk__nom_menu'] for p in top_platos]
    top_platos_datos = [int(p['cantidad_vendida'] or 0) for p in top_platos]

    # Resumenes globales (Kpis superiores)
    ingresos_totales_mes = Pago.objects.filter(
        estado_pago='aprobado',
        fecha_pago__month=hoy.month,
        fecha_pago__year=hoy.year
    ).aggregate(total=Sum('monto_pago'))['total'] or 0
    
    ingresos_hoy = Pago.objects.filter(
        estado_pago='aprobado',
        fecha_pago=hoy.date()
    ).aggregate(total=Sum('monto_pago'))['total'] or 0
    
    pedidos_completados = Pedido.objects.filter(estado_pedido='entregado').count()
    pedidos_cancelados = Pedido.objects.filter(estado_pedido='cancelado').count()

    context = {
        'ventas_semana_labels': ventas_semana_labels,
        'ventas_semana_datos': ventas_semana_datos,
        'top_platos_labels': top_platos_labels,
        'top_platos_datos': top_platos_datos,
        
        'ingresos_totales_mes': ingresos_totales_mes,
        'ingresos_hoy': ingresos_hoy,
        'pedidos_completados': pedidos_completados,
        'pedidos_cancelados': pedidos_cancelados,
    }
    
    return render(request, 'admin/reportes.html', context)
