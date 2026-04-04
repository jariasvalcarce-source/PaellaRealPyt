from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.db.models.functions import Cast, TruncDate
from django.db import models
from decimal import Decimal

from ..models import Pedido, DetallePedidoMenu, Pago, Factura, RecetaMenu, Producto

def _obtener_datos_reportes():
    hoy = timezone.localdate()
    # Obtener inicio de semana (lunes) en la zona horaria local
    fecha_inicio_semana = hoy - timedelta(days=hoy.weekday())
    
    # Crear límites de fecha para la semana completa
    inicio_semana = timezone.make_aware(datetime.combine(fecha_inicio_semana, datetime.min.time()), timezone.get_current_timezone())
    fin_semana = inicio_semana + timedelta(days=7)

    # Use day boundaries to avoid potential timezone mismatches
    inicio_hoy = timezone.make_aware(datetime.combine(hoy, datetime.min.time()), timezone.get_current_timezone())
    fin_hoy = inicio_hoy + timedelta(days=1)

    # 1. Ventas Semanales (Lunes a Domingo actual) usando pedidos
    # Obtener todos los pedidos y agrupar en Python por fecha local
    pedidos_semana = Pedido.objects.filter(
        fecha_pedido__gte=inicio_semana,
        fecha_pedido__lt=fin_semana,
        estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']
    ).values('fecha_pedido', 'total_pedido')

    # Agrupar por fecha local en Python
    ventas_dict = {}
    for p in pedidos_semana:
        # Convertir a hora local
        fecha_local = timezone.localtime(p['fecha_pedido']).date()
        if fecha_local not in ventas_dict:
            ventas_dict[fecha_local] = 0
        ventas_dict[fecha_local] += float(p['total_pedido'] or 0)

    # Construir array para Chart.js con los 7 días de la semana
    ventas_semana_labels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    ventas_semana_datos = [0] * 7
    
    for i in range(7):
        fecha_dia = fecha_inicio_semana + timedelta(days=i)
        ventas_semana_datos[i] = ventas_dict.get(fecha_dia, 0)

    # 2. Top 5 Platos Más Vendidos
    top_platos = DetallePedidoMenu.objects.filter(
        id_pedido_fk__estado_pedido__in=['entregado', 'confirmado', 'preparando', 'listo', 'pendiente']
    ).values('id_menu_fk__nom_menu').annotate(
        cantidad_vendida=Sum('cant_detalle')
    ).order_by('-cantidad_vendida')[:5]

    top_platos_labels = [p['id_menu_fk__nom_menu'] for p in top_platos]
    top_platos_datos = [int(p['cantidad_vendida'] or 0) for p in top_platos]

    inicio_mes = timezone.make_aware(datetime.combine(hoy.replace(day=1), datetime.min.time()), timezone.get_current_timezone())
    siguiente_mes = (hoy.replace(day=1) + timedelta(days=32)).replace(day=1)
    fin_mes = timezone.make_aware(datetime.combine(siguiente_mes, datetime.min.time()), timezone.get_current_timezone())

    ingresos_totales_mes = Pedido.objects.filter(
        fecha_pedido__gte=inicio_mes,
        fecha_pedido__lt=fin_mes,
        estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']
    ).aggregate(total=Sum('total_pedido'))['total'] or 0

    pedidos_hoy = Pedido.objects.filter(
        fecha_pedido__gte=inicio_hoy,
        fecha_pedido__lt=fin_hoy,
        estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']
    )

    ingresos_hoy = pedidos_hoy.aggregate(total=Sum('total_pedido'))['total'] or 0

    pedidos_completados = Pedido.objects.filter(estado_pedido='entregado').count()
    pedidos_cancelados = Pedido.objects.filter(estado_pedido='cancelado').count()

    detalles_hoy = DetallePedidoMenu.objects.filter(
        id_pedido_fk__in=pedidos_hoy
    ).select_related('id_menu_fk')

    platos_hoy = list(detalles_hoy.values('id_menu_fk__nom_menu').annotate(
        cantidad_vendida=Sum('cant_detalle')
    ).order_by('-cantidad_vendida'))

    total_platos_vendidos_hoy = sum(int(p['cantidad_vendida'] or 0) for p in platos_hoy)
    total_platos_diferentes_hoy = len(platos_hoy)

    consumo_por_producto = {}
    for detalle in detalles_hoy:
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

    return {
        'hoy': hoy,
        'ventas_semana_labels': ventas_semana_labels,
        'ventas_semana_datos': ventas_semana_datos,
        'top_platos_labels': top_platos_labels,
        'top_platos_datos': top_platos_datos,
        'ingresos_totales_mes': ingresos_totales_mes,
        'ingresos_hoy': ingresos_hoy,
        'pedidos_completados': pedidos_completados,
        'pedidos_cancelados': pedidos_cancelados,
        'platos_hoy': platos_hoy,
        'total_platos_vendidos_hoy': total_platos_vendidos_hoy,
        'total_platos_diferentes_hoy': total_platos_diferentes_hoy,
        'consumo_productos_hoy': consumo_productos_hoy,
        'total_insumos_hoy': total_insumos_hoy,
        'total_insumos_consumidos': total_insumos_consumidos,
        'gasto_hoy': gasto_hoy,
    }


def _obtener_resumen_dia(fecha):
    inicio_dia = timezone.make_aware(datetime.combine(fecha, datetime.min.time()), timezone.get_current_timezone())
    fin_dia = inicio_dia + timedelta(days=1)
    pedidos = Pedido.objects.filter(
        fecha_pedido__gte=inicio_dia,
        fecha_pedido__lt=fin_dia,
        estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']
    )

    ingresos = pedidos.aggregate(total=Sum('total_pedido'))['total'] or 0
    cantidad_pedidos = pedidos.count()
    detalles = DetallePedidoMenu.objects.filter(id_pedido_fk__in=pedidos).select_related('id_menu_fk')
    platos = list(detalles.values('id_menu_fk__nom_menu').annotate(cantidad_vendida=Sum('cant_detalle')).order_by('-cantidad_vendida'))
    total_platos = sum(int(p['cantidad_vendida'] or 0) for p in platos)
    platos_diferentes = len(platos)

    consumo_por_producto = {}
    for detalle in detalles:
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

    consumo_items = []
    gasto = Decimal('0')
    for item in consumo_por_producto.values():
        item['cantidad_consumida'] = item['cantidad_consumida'].quantize(Decimal('0.001'))
        item['costo'] = (item['cantidad_consumida'] * item['precio_unitario']).quantize(Decimal('0.01'))
        gasto += item['costo']
        consumo_items.append(item)

    return {
        'fecha': fecha,
        'ingresos': ingresos,
        'cantidad_pedidos': cantidad_pedidos,
        'platos_diferentes': platos_diferentes,
        'total_platos': total_platos,
        'insumos_diferentes': len(consumo_items),
        'total_consumido_kg': sum(item['cantidad_consumida'] for item in consumo_items),
        'gasto': gasto,
        'platos': platos,
        'consumo_items': sorted(consumo_items, key=lambda x: x['cantidad_consumida'], reverse=True),
    }


def reportes_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')

    datos = _obtener_datos_reportes()
    datos['resumen_hoy'] = _obtener_resumen_dia(datos['hoy'])
    datos['resumen_ayer'] = _obtener_resumen_dia(datos['hoy'] - timedelta(days=1))
    return render(request, 'admin/reportes.html', datos)


