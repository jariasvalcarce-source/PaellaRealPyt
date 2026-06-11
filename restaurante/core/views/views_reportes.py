from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.db.models.functions import Cast, TruncDate, ExtractHour
from django.db import models
from decimal import Decimal

from core.models import Pedido, DetallePedidoMenu, Pago, Factura, RecetaMenu, Producto, Menu

def _obtener_datos_reportes(request_get):
    hoy = timezone.localdate()
    ayer = hoy - timedelta(days=1)
    fecha_inicio_semana = hoy - timedelta(days=hoy.weekday())
    semana_pasada_inicio = fecha_inicio_semana - timedelta(days=7)
    
    # Manejo de filtros
    fecha_inicio_str = request_get.get('fecha_inicio')
    fecha_fin_str = request_get.get('fecha_fin')
    plato_id = request_get.get('plato_id')

    if fecha_inicio_str:
        inicio_periodo = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
    else:
        # Por defecto hoy
        inicio_periodo = hoy

    if fecha_fin_str:
        fin_periodo = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    else:
        fin_periodo = hoy

    # Hacer timezone aware para consultas
    inicio_tz = timezone.make_aware(datetime.combine(inicio_periodo, datetime.min.time()))
    fin_tz = timezone.make_aware(datetime.combine(fin_periodo, datetime.max.time()))
    
    # Periodo anterior para variaciones
    dias_periodo = (fin_periodo - inicio_periodo).days + 1
    inicio_anterior = inicio_periodo - timedelta(days=dias_periodo)
    fin_anterior = inicio_periodo - timedelta(days=1)
    inicio_anterior_tz = timezone.make_aware(datetime.combine(inicio_anterior, datetime.min.time()))
    fin_anterior_tz = timezone.make_aware(datetime.combine(fin_anterior, datetime.max.time()))

    # Pedidos completados en el periodo
    pedidos_periodo = Pedido.objects.filter(
        fecha_pedido__gte=inicio_tz,
        fecha_pedido__lte=fin_tz,
        estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']
    )
    
    # Pedidos completados en el periodo anterior
    pedidos_anterior = Pedido.objects.filter(
        fecha_pedido__gte=inicio_anterior_tz,
        fecha_pedido__lte=fin_anterior_tz,
        estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']
    )

    # Ingresos Totales
    ingresos_totales = pedidos_periodo.aggregate(total=Sum('total_pedido'))['total'] or 0
    ingresos_anterior = pedidos_anterior.aggregate(total=Sum('total_pedido'))['total'] or 0
    
    if ingresos_anterior > 0:
        variacion_ingresos = round(((float(ingresos_totales) - float(ingresos_anterior)) / float(ingresos_anterior)) * 100, 1)
    else:
        variacion_ingresos = 100.0 if ingresos_totales > 0 else 0.0

    # Ingresos Hoy
    hoy_tz_inicio = timezone.make_aware(datetime.combine(hoy, datetime.min.time()))
    hoy_tz_fin = timezone.make_aware(datetime.combine(hoy, datetime.max.time()))
    ayer_tz_inicio = timezone.make_aware(datetime.combine(ayer, datetime.min.time()))
    ayer_tz_fin = timezone.make_aware(datetime.combine(ayer, datetime.max.time()))

    ingresos_hoy = Pedido.objects.filter(fecha_pedido__gte=hoy_tz_inicio, fecha_pedido__lte=hoy_tz_fin, estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']).aggregate(total=Sum('total_pedido'))['total'] or 0
    ingresos_ayer = Pedido.objects.filter(fecha_pedido__gte=ayer_tz_inicio, fecha_pedido__lte=ayer_tz_fin, estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']).aggregate(total=Sum('total_pedido'))['total'] or 0

    if ingresos_ayer > 0:
        variacion_hoy = round(((float(ingresos_hoy) - float(ingresos_ayer)) / float(ingresos_ayer)) * 100, 1)
    else:
        variacion_hoy = 100.0 if ingresos_hoy > 0 else 0.0

    # Pedidos Cancelados
    pedidos_cancelados = Pedido.objects.filter(fecha_pedido__gte=inicio_tz, fecha_pedido__lte=fin_tz, estado_pedido='cancelado').count()
    pedidos_cancelados_anterior = Pedido.objects.filter(fecha_pedido__gte=inicio_anterior_tz, fecha_pedido__lte=fin_anterior_tz, estado_pedido='cancelado').count()
    variacion_cancelados = pedidos_cancelados - pedidos_cancelados_anterior

    # Métricas de Pedidos
    total_pedidos_periodo = pedidos_periodo.count() + pedidos_cancelados
    pedidos_entregados = pedidos_periodo.filter(estado_pedido='entregado').count()
    ticket_promedio = (ingresos_totales / pedidos_periodo.count()) if pedidos_periodo.count() > 0 else 0

    hora_pico_qs = pedidos_periodo.annotate(hora=ExtractHour('fecha_pedido')).values('hora').annotate(total=Count('id_pedido_pk')).order_by('-total').first()
    if hora_pico_qs and hora_pico_qs.get('hora') is not None:
        # Django returns an integer for hour
        hora_str = str(hora_pico_qs['hora']).zfill(2)
        hora_pico = f"{hora_str}:00"
    else:
        hora_pico = "N/A"

    # Platos vendidos (hoy) o en el periodo si filtramos
    detalles_qs = DetallePedidoMenu.objects.filter(id_pedido_fk__in=pedidos_periodo).select_related('id_menu_fk')
    if plato_id:
        detalles_qs = detalles_qs.filter(id_menu_fk_id=plato_id)

    platos_vendidos = list(detalles_qs.values('id_menu_fk__nom_menu', 'id_menu_fk__precio_menu', 'id_menu_fk').annotate(
        total_vendido=Sum('cant_detalle')
    ).order_by('-total_vendido'))

    platos_vendidos_hoy = []
    total_unidades_hoy = 0
    for p in platos_vendidos:
        platos_vendidos_hoy.append({
            'nom_menu': p['id_menu_fk__nom_menu'],
            'total_vendido': p['total_vendido']
        })
        total_unidades_hoy += p['total_vendido']

    # Insumos y Rentabilidad
    consumo_por_producto = {}
    rentabilidad_por_plato_dict = {}

    for detalle in detalles_qs:
        menu_id = detalle.id_menu_fk_id
        if menu_id not in rentabilidad_por_plato_dict:
            rentabilidad_por_plato_dict[menu_id] = {
                'nom_menu': detalle.id_menu_fk.nom_menu,
                'unidades_vendidas': 0,
                'precio_venta': detalle.id_menu_fk.precio_menu,
                'costo_insumos_total_plato': Decimal('0'),
            }
        
        rentabilidad_por_plato_dict[menu_id]['unidades_vendidas'] += detalle.cant_detalle
        
        recetas = RecetaMenu.objects.select_related('id_produ_fk').filter(id_menu_fk=detalle.id_menu_fk)
        
        if not rentabilidad_por_plato_dict[menu_id].get('sin_receta_evaluado'):
            rentabilidad_por_plato_dict[menu_id]['sin_receta'] = not recetas.exists()
            rentabilidad_por_plato_dict[menu_id]['sin_receta_evaluado'] = True

        costo_unitario_plato = Decimal('0')
        
        if not rentabilidad_por_plato_dict[menu_id]['sin_receta']:
            for receta in recetas:
                producto = receta.id_produ_fk
                # La cantidad_reque está en gramos, convertimos a Kg para multiplicar por el precio (si el precio es por Kg)
                # En tu sistema actual, stock_actual_produ puede ser kg o gr, asumimos kg = /1000
                consumo_kg = (Decimal(receta.cantidad_reque) / Decimal('1000'))
                costo_insumo = consumo_kg * producto.precio_uni_produ
                costo_unitario_plato += costo_insumo
                
                consumo_total_detalle = consumo_kg * detalle.cant_detalle
                costo_total_detalle = costo_insumo * detalle.cant_detalle

                if producto.id_produ_pk not in consumo_por_producto:
                    consumo_por_producto[producto.id_produ_pk] = {
                        'nom_produ': producto.nom_produ,
                        'total_consumido': Decimal('0'),
                        'costo_total': Decimal('0'),
                    }
                consumo_por_producto[producto.id_produ_pk]['total_consumido'] += consumo_total_detalle
                consumo_por_producto[producto.id_produ_pk]['costo_total'] += costo_total_detalle

            rentabilidad_por_plato_dict[menu_id]['costo_insumos_total_plato'] += (costo_unitario_plato * detalle.cant_detalle)

    insumos_hoy = []
    total_consumido_hoy = Decimal('0')
    gasto_estimado_hoy = Decimal('0')
    for item in consumo_por_producto.values():
        insumos_hoy.append(item)
        total_consumido_hoy += item['total_consumido']
        gasto_estimado_hoy += item['costo_total']

    insumos_hoy.sort(key=lambda x: x['total_consumido'], reverse=True)

    # Calculos Rentabilidad
    rentabilidad_por_plato = []
    ganancia_total = Decimal('0')
    costo_total_insumos = Decimal('0')
    
    for plato in rentabilidad_por_plato_dict.values():
        if plato.get('sin_receta'):
            rentabilidad_por_plato.append({
                'nom_menu': plato['nom_menu'],
                'unidades_vendidas': plato['unidades_vendidas'],
                'precio_venta': float(plato['precio_venta']),
                'costo_insumos': 0.0,
                'ganancia_unitaria': 0.0,
                'margen': -1,  # -1 represents N/A for frontend
                'ganancia_total': 0.0,
                'sin_receta': True
            })
        else:
            costo_unitario = plato['costo_insumos_total_plato'] / plato['unidades_vendidas'] if plato['unidades_vendidas'] > 0 else Decimal('0')
            ganancia_unitaria = plato['precio_venta'] - costo_unitario
            margen = (ganancia_unitaria / plato['precio_venta'] * 100) if plato['precio_venta'] > 0 else 0
            ganancia_total_plato = ganancia_unitaria * plato['unidades_vendidas']
            
            ganancia_total += ganancia_total_plato
            costo_total_insumos += plato['costo_insumos_total_plato']

            rentabilidad_por_plato.append({
                'nom_menu': plato['nom_menu'],
                'unidades_vendidas': plato['unidades_vendidas'],
                'precio_venta': float(plato['precio_venta']),
                'costo_insumos': float(costo_unitario),
                'ganancia_unitaria': float(ganancia_unitaria),
                'margen': round(float(margen)),
                'ganancia_total': float(ganancia_total_plato),
                'sin_receta': False
            })

    rentabilidad_por_plato.sort(key=lambda x: x['ganancia_total'], reverse=True)

    margen_promedio = round((float(ganancia_total) / float(ingresos_totales)) * 100) if ingresos_totales > 0 else 0
    porcentaje_costo_insumos = round((float(costo_total_insumos) / float(ingresos_totales)) * 100) if ingresos_totales > 0 else 0

    plato_mas_rentable = max(rentabilidad_por_plato, key=lambda x: x['margen']) if rentabilidad_por_plato else None
    plato_menos_rentable = min(rentabilidad_por_plato, key=lambda x: x['margen']) if rentabilidad_por_plato else None

    totales = {
        'unidades': sum(p['unidades_vendidas'] for p in rentabilidad_por_plato),
        'costo_promedio': sum(p['costo_insumos'] for p in rentabilidad_por_plato) / len(rentabilidad_por_plato) if rentabilidad_por_plato else 0,
        'ganancia_unitaria_promedio': sum(p['ganancia_unitaria'] for p in rentabilidad_por_plato) / len(rentabilidad_por_plato) if rentabilidad_por_plato else 0,
        'margen_promedio': margen_promedio,
        'ganancia_total': ganancia_total
    }

    # Gráficas
    # Curva semanal: ultimos 7 dias desde fin_periodo
    DIAS_SEMANA = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    ventas_semanales_labels = []
    ventas_semanales_data = []
    for i in range(6, -1, -1):
        dia = fin_periodo - timedelta(days=i)
        dia_tz_inicio = timezone.make_aware(datetime.combine(dia, datetime.min.time()))
        dia_tz_fin = timezone.make_aware(datetime.combine(dia, datetime.max.time()))
        
        ingreso_dia = Pedido.objects.filter(fecha_pedido__gte=dia_tz_inicio, fecha_pedido__lte=dia_tz_fin, estado_pedido__in=['pendiente', 'confirmado', 'preparando', 'listo', 'entregado']).aggregate(total=Sum('total_pedido'))['total'] or 0
        dia_str = DIAS_SEMANA[dia.weekday()]
        ventas_semanales_labels.append(dia_str)
        ventas_semanales_data.append(float(ingreso_dia))

    rentabilidad_labels = [p['nom_menu'] for p in rentabilidad_por_plato]
    rentabilidad_precios = [p['precio_venta'] for p in rentabilidad_por_plato]
    rentabilidad_costos = [p['costo_insumos'] for p in rentabilidad_por_plato]
    
    # Estado del Inventario
    productos_criticos = Producto.objects.filter(stock_actual_produ__lte=models.F('stock_minimo_produ')).order_by('stock_actual_produ')

    return {
        'fecha_inicio': inicio_periodo,
        'fecha_fin': fin_periodo,
        'menus': Menu.objects.filter(disponible_menu=True),
        'plato_id_seleccionado': str(plato_id) if plato_id else '',
        
        'ingresos_totales': float(ingresos_totales),
        'variacion_ingresos': variacion_ingresos,
        'ingresos_hoy': float(ingresos_hoy),
        'variacion_hoy': variacion_hoy,
        'pedidos_cancelados': pedidos_cancelados,
        'variacion_cancelados': variacion_cancelados,
        
        'platos_vendidos_hoy': platos_vendidos_hoy,
        'total_unidades_hoy': total_unidades_hoy,
        
        'insumos_hoy': insumos_hoy,
        'total_consumido_hoy': float(total_consumido_hoy),
        'gasto_estimado_hoy': float(gasto_estimado_hoy),
        
        'ventas_semanales_labels': ventas_semanales_labels,
        'ventas_semanales_data': ventas_semanales_data,
        
        'ganancia_total': float(ganancia_total),
        'margen_promedio': margen_promedio,
        'costo_total_insumos': float(costo_total_insumos),
        'porcentaje_costo_insumos': porcentaje_costo_insumos,
        
        'plato_mas_rentable': plato_mas_rentable,
        'plato_menos_rentable': plato_menos_rentable,
        'rentabilidad_por_plato': rentabilidad_por_plato,
        'totales': totales,
        
        'rentabilidad_labels': rentabilidad_labels,
        'rentabilidad_precios': rentabilidad_precios,
        'rentabilidad_costos': rentabilidad_costos,
        
        'total_pedidos_periodo': total_pedidos_periodo,
        'pedidos_entregados': pedidos_entregados,
        'ticket_promedio': float(ticket_promedio),
        'hora_pico': hora_pico,
        
        'productos_criticos': productos_criticos,
    }

def reportes_admin(request):
    if request.session.get('rol') != 'admin':
        return redirect('login')

    datos = _obtener_datos_reportes(request.GET)
    return render(request, 'admin/reportes/reportes.html', datos)
