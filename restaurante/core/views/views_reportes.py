from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.db.models.functions import Cast, TruncDate
from django.db import models
from decimal import Decimal

from core.models import Pedido, DetallePedidoMenu, Pago, Factura, RecetaMenu, Producto, Menu

def _obtener_datos_reportes(request_get):
    hoy = timezone.localdate()
    fecha_inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_semana = timezone.make_aware(datetime.combine(fecha_inicio_semana, datetime.min.time()), timezone.get_current_timezone())
    fin_semana = inicio_semana + timedelta(days=7)

    inicio_mes = timezone.make_aware(datetime.combine(hoy.replace(day=1), datetime.min.time()), timezone.get_current_timezone())
    siguiente_mes = (hoy.replace(day=1) + timedelta(days=32)).replace(day=1)
    fin_mes = timezone.make_aware(datetime.combine(siguiente_mes, datetime.min.time()), timezone.get_current_timezone())

    fecha_inicio_str = request_get.get('fecha_inicio')
    fecha_fin_str = request_get.get('fecha_fin')
    plato_id = request_get.get('plato_id')

    es_filtrado = bool(fecha_inicio_str or fecha_fin_str or plato_id)

    if fecha_inicio_str:
        inicio_periodo = timezone.make_aware(datetime.strptime(fecha_inicio_str, '%Y-%m-%d'), timezone.get_current_timezone())
    else:
        inicio_periodo = timezone.make_aware(datetime.combine(hoy, datetime.min.time()), timezone.get_current_timezone())

    if fecha_fin_str:
        fin_periodo = timezone.make_aware(datetime.strptime(fecha_fin_str, '%Y-%m-%d'), timezone.get_current_timezone()) + timedelta(days=1)
    else:
        fin_periodo = inicio_periodo + timedelta(days=1)

    pedidos_semana = Pedido.objects.filter(
        fecha_pedido__gte=inicio_semana,
        fecha_pedido__lt=fin_semana,
        estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']
    ).values('fecha_pedido', 'total_pedido')

    ventas_dict_semana = {}
    for p in pedidos_semana:
        fecha_local = timezone.localtime(p['fecha_pedido']).date()
        if fecha_local not in ventas_dict_semana:
            ventas_dict_semana[fecha_local] = 0
        ventas_dict_semana[fecha_local] += float(p['total_pedido'] or 0)

    top_platos = DetallePedidoMenu.objects.filter(
        id_pedido_fk__estado_pedido__in=['entregado', 'confirmado', 'preparando', 'listo', 'pendiente']
    ).values('id_menu_fk__nom_menu').annotate(
        cantidad_vendida=Sum('cant_detalle')
    ).order_by('-cantidad_vendida')[:5]

    top_platos_labels = [p['id_menu_fk__nom_menu'] for p in top_platos]
    top_platos_datos = [int(p['cantidad_vendida'] or 0) for p in top_platos]

    pedidos_periodo = Pedido.objects.filter(
        fecha_pedido__gte=inicio_periodo,
        fecha_pedido__lt=fin_periodo,
        estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']
    )

    ingresos_periodo = pedidos_periodo.aggregate(total=Sum('total_pedido'))['total'] or 0
    pedidos_completados = pedidos_periodo.filter(estado_pedido='entregado').count()
    pedidos_cancelados = Pedido.objects.filter(
        fecha_pedido__gte=inicio_periodo,
        fecha_pedido__lt=fin_periodo,
        estado_pedido='cancelado'
    ).count()

    if es_filtrado:
        ingresos_tarjeta_1 = ingresos_periodo
        titulo_tarjeta_1 = 'Ingresos del Periodo'
        ingresos_tarjeta_2 = pedidos_completados
        titulo_tarjeta_2 = 'Pedidos Completados'
        
        # Calcular gráfica para el periodo filtrado
        ventas_dict_periodo = {}
        for p in pedidos_periodo:
            fecha_local = timezone.localtime(p.fecha_pedido).date()
            if fecha_local not in ventas_dict_periodo:
                ventas_dict_periodo[fecha_local] = 0
            ventas_dict_periodo[fecha_local] += float(p.total_pedido or 0)
            
        delta_days = (fin_periodo - inicio_periodo).days
        ventas_semana_labels = []
        ventas_semana_datos = []
        for i in range(min(delta_days, 31)):  # Máximo 31 días en la gráfica
            current_date = (inicio_periodo + timedelta(days=i)).date()
            ventas_semana_labels.append(current_date.strftime('%d/%m'))
            ventas_semana_datos.append(ventas_dict_periodo.get(current_date, 0))
            
        fecha_fin_real = fin_periodo - timedelta(days=1)
        if inicio_periodo.date() == fecha_fin_real.date():
            titulo_grafica = f"Ingresos del Día ({inicio_periodo.strftime('%d/%m/%Y')})"
        else:
            titulo_grafica = f"Curva de Ingresos ({inicio_periodo.strftime('%d/%m/%y')} al {fecha_fin_real.strftime('%d/%m/%y')})"

    else:
        ingresos_totales_mes = Pedido.objects.filter(
            fecha_pedido__gte=inicio_mes,
            fecha_pedido__lt=fin_mes,
            estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']
        ).aggregate(total=Sum('total_pedido'))['total'] or 0
        ingresos_tarjeta_1 = ingresos_totales_mes
        titulo_tarjeta_1 = 'Ingresos del Mes'
        ingresos_tarjeta_2 = ingresos_periodo
        titulo_tarjeta_2 = 'Ingresos del Día'
        
        ventas_semana_labels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        ventas_semana_datos = [ventas_dict_semana.get(fecha_inicio_semana + timedelta(days=i), 0) for i in range(7)]
        titulo_grafica = "Curva de Ingresos Semanales (Lunes a Domingo Actual)"

    detalles_qs = DetallePedidoMenu.objects.filter(id_pedido_fk__in=pedidos_periodo).select_related('id_menu_fk')
    
    if plato_id:
        detalles_qs = detalles_qs.filter(id_menu_fk_id=plato_id)

    platos_hoy = list(detalles_qs.values('id_menu_fk__nom_menu').annotate(
        cantidad_vendida=Sum('cant_detalle')
    ).order_by('-cantidad_vendida'))

    total_platos_vendidos = sum(int(p['cantidad_vendida'] or 0) for p in platos_hoy)
    total_platos_diferentes = len(platos_hoy)

    consumo_por_producto = {}
    for detalle in detalles_qs:
        recetas = RecetaMenu.objects.select_related('id_produ_fk').filter(id_menu_fk=detalle.id_menu_fk)
        for receta in recetas:
            producto = receta.id_produ_fk
            consumo_kg = (Decimal(receta.cantidad_reque) / Decimal('1000')) * detalle.cant_detalle
            if producto.id_produ_pk not in consumo_por_producto:
                consumo_por_producto[producto.id_produ_pk] = {
                    'producto': producto,
                    'cantidad_consumida': Decimal('0'),
                    'stock_actual': producto.stock_actual_produ,
                    'precio_unitario': producto.precio_uni_produ,
                }
            consumo_por_producto[producto.id_produ_pk]['cantidad_consumida'] += consumo_kg

    consumo_productos_hoy = []
    gasto_hoy = Decimal('0')
    for item in consumo_por_producto.values():
        item['cantidad_consumida'] = item['cantidad_consumida'].quantize(Decimal('0.001'))
        item['costo'] = (item['cantidad_consumida'] * item['precio_unitario']).quantize(Decimal('0.01'))
        gasto_hoy += item['costo']
        consumo_productos_hoy.append(item)

    consumo_productos_hoy.sort(key=lambda x: x['cantidad_consumida'], reverse=True)
    total_insumos_hoy = len(consumo_productos_hoy)
    total_insumos_consumidos = sum(item['cantidad_consumida'] for item in consumo_productos_hoy)

    menus_lista = Menu.objects.filter(disponible_menu=True)

    return {
        'ventas_semana_labels': ventas_semana_labels,
        'ventas_semana_datos': ventas_semana_datos,
        'titulo_grafica': titulo_grafica,
        'top_platos_labels': top_platos_labels,
        'top_platos_datos': top_platos_datos,
        'es_filtrado': es_filtrado,
        'titulo_tarjeta_1': titulo_tarjeta_1,
        'ingresos_tarjeta_1': ingresos_tarjeta_1,
        'titulo_tarjeta_2': titulo_tarjeta_2,
        'ingresos_tarjeta_2': ingresos_tarjeta_2,
        'pedidos_cancelados': pedidos_cancelados,
        'pedidos_completados_global': pedidos_completados,
        'platos_hoy': platos_hoy,
        'total_platos_vendidos_hoy': total_platos_vendidos,
        'total_platos_diferentes_hoy': total_platos_diferentes,
        'consumo_productos_hoy': consumo_productos_hoy,
        'total_insumos_hoy': total_insumos_hoy,
        'total_insumos_consumidos': total_insumos_consumidos,
        'gasto_hoy': gasto_hoy,
        'fecha_inicio_str': fecha_inicio_str,
        'fecha_fin_str': fecha_fin_str,
        'plato_id': int(plato_id) if plato_id else None,
        'menus_lista': menus_lista
    }

def reportes_admin(request):
    if request.session.get('rol') != 'admin':
        return redirect('login')

    datos = _obtener_datos_reportes(request.GET)
    return render(request, 'admin/reportes.html', datos)
