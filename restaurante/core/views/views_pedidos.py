# views_pedidos.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Prefetch, Sum
from decimal import Decimal
from datetime import datetime as dt
from django.utils import timezone
from django.db import transaction
from django.core.management import call_command
from core.models import (
    Pedido, DetallePedidoMenu, Domicilio, Menu, 
    Empleado, Factura, MetodoPago, Pago, Notificacion, Barrio, Localidad,
    UsuarioAuth, Cliente, TipoMenu, RecetaMenu
)

def migrate_db(request):
    try:
        call_command('makemigrations', interactive=False)
        call_command('migrate', interactive=False)
        return HttpResponse("Migrations run successfully.")
    except Exception as e:
        import traceback
        return HttpResponse(f"Migration failed: {e}\n{traceback.format_exc()}", status=200)


def _crear_notificacion(tipo, titulo, mensaje, destinatario_rol,
                        id_auth_destino=None, id_auth_origen=None,
                        pedido=None, factura=None,
                        producto=None, movimiento=None):
    """Crea una notificación en la base de datos."""
    Notificacion.objects.create(
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        destinatario_rol=destinatario_rol,
        id_auth_destino_fk=id_auth_destino,
        id_auth_origen_fk=id_auth_origen,
        id_pedido_fk=pedido,
        id_factura_fk=factura,
        id_producto_fk=producto,
        id_movi_fk=movimiento,
    )


def _generar_factura_si_entregado(pedido):
    """Genera la factura si no existe y asocia el pago si existe."""
    if pedido.estado_pedido != 'entregado':
        return None
    
    if Factura.objects.filter(id_pedido_factu_fk=pedido).exists():
        return Factura.objects.filter(id_pedido_factu_fk=pedido).first()

    ahora = dt.now()
    factura = Factura.objects.create(
        fecha_factu        = ahora.date(),
        hora_factu         = ahora.time(),
        total_factu        = pedido.total_pedido,
        id_clien_factu_fk  = pedido.id_clien_pedido_fk,
        id_pedido_factu_fk = pedido,
    )

    # Asociar pago existente si hay uno
    pago = pedido.pago_set.first()
    if pago:
        pago.id_factu_pago_fk = factura
        pago.save(update_fields=['id_factu_pago_fk'])

    # Notificar al cliente
    usuario_auth = pedido.id_clien_pedido_fk.id_auth_fk
    if usuario_auth:
        _crear_notificacion(
            tipo='pago',
            titulo=f'Factura #{factura.id_factu_pk} generada',
            mensaje=f'Tu pedido #PED-{pedido.id_pedido_pk:04d} fue entregado. La factura ha sido generada exitosamente.',
            destinatario_rol='cliente',
            id_auth_destino=usuario_auth,
            pedido=pedido,
            factura=factura,
        )
    return factura


def _descontar_stock_pedido(pedido):
    """
    Descuenta del inventario los ingredientes requeridos para cada menú del pedido,
    utilizando conversión de unidades de medida y garantizando que el stock no sea negativo.
    """
    from core.utils import convertir_a_unidad_base
    from core.models import RecetaMenu
    for detalle in pedido.detalles_set.all():
        menu = detalle.id_menu_fk
        recetas = RecetaMenu.objects.filter(id_menu_fk=menu)
        for receta in recetas:
            prod = receta.id_produ_fk
            try:
                # Convertir la cantidad requerida en la receta (que está en unidad receta)
                # a la unidad de medida del producto en el inventario
                cantidad_convertida = convertir_a_unidad_base(
                    receta.cantidad_reque,
                    receta.id_uni_medi_fk,
                    prod.id_uni_medi_produ_fk
                )
            except Exception:
                cantidad_convertida = receta.cantidad_reque
            
            descuento = cantidad_convertida * Decimal(str(detalle.cant_detalle))
            prod.stock_actual_produ = max(Decimal('0.000'), prod.stock_actual_produ - descuento)
            prod.save()
            
            if prod.stock_actual_produ == Decimal('0.000'):
                _crear_notificacion(
                    tipo='inventario',
                    titulo='Stock Crítico',
                    mensaje=f'El ingrediente {prod.nom_produ} ha llegado a 0 en el inventario.',
                    destinatario_rol='admin',
                    producto=prod
                )


def _get_cliente(request):
    usuario = UsuarioAuth.objects.get(id_auth_pk=request.session['usuario_id'])
    cliente = Cliente.objects.get(id_auth_fk=usuario)
    return usuario, cliente


def _ctx_cliente(cliente):
    return {'usuario_nombre': cliente.nom_clien, 'usuario_email': cliente.correo_clien}


def _validar_pedido(carrito_items):
    """
    Valida que todos los menús en el carrito tengan ingredientes activos y stock suficiente.
    
    Retorna: (es_valido, mensaje_error, ingredientes_problema)
    """
    from core.models import RecetaMenu
    
    if not carrito_items:
        return False, 'Carrito vacío', []
    
    from core.utils import convertir_a_unidad_base
    problemas = []
    
    # Agregar las cantidades requeridas por producto en todo el carrito
    requerimientos_totales = {} # {id_produ: {'producto': prod, 'requerido': Decimal, 'menus': set()}}
    
    for item in carrito_items:
        menu = Menu.objects.get(id_menu_pk=item['menu_id'])
        cantidad = item['cantidad']
        
        # Obtener todas las recetas del menú
        recetas = RecetaMenu.objects.select_related(
            'id_produ_fk', 'id_uni_medi_fk',
            'id_produ_fk__id_uni_medi_produ_fk'
        ).filter(id_menu_fk=menu)
        
        if not recetas.exists():
            problemas.append({
                'ingrediente': 'Ninguno',
                'menu': menu.nom_menu,
                'razon': 'sin_receta',
                'estado': 'n/a',
            })
            continue
        
        for receta in recetas:
            prod = receta.id_produ_fk
            
            # Validar que el producto esté activo
            if prod.estado_produ != 'disponible':
                problemas.append({
                    'ingrediente': prod.nom_produ,
                    'menu': menu.nom_menu,
                    'razon': 'inactivo',
                    'estado': prod.estado_produ,
                })
                continue
            
            # Conversión por unidad
            try:
                requerido = convertir_a_unidad_base(
                    receta.cantidad_reque,
                    receta.id_uni_medi_fk,
                    prod.id_uni_medi_produ_fk
                ) * Decimal(str(cantidad))
            except ValueError as e:
                # Fallback to direct deduction if something is completely wrong
                requerido = receta.cantidad_reque * Decimal(str(cantidad))
            
            prod_id = prod.id_produ_pk
            if prod_id not in requerimientos_totales:
                requerimientos_totales[prod_id] = {
                    'producto': prod,
                    'requerido': Decimal('0'),
                    'menus': set(),
                }
            requerimientos_totales[prod_id]['requerido'] += requerido
            requerimientos_totales[prod_id]['menus'].add(menu.nom_menu)
            
    # Validar el stock agrupado
    for req in requerimientos_totales.values():
        prod = req['producto']
        total_requerido = req['requerido']
        stock_actual = prod.stock_actual_produ
        
        if stock_actual < total_requerido:
            problemas.append({
                'ingrediente': prod.nom_produ,
                'menu': ', '.join(req['menus']),
                'razon': 'stock_insuficiente',
                'stock_actual': float(stock_actual),
                'requerido': float(total_requerido),
                'unidad': prod.id_uni_medi_produ_fk.abreviatura,
            })
    
    if problemas:
        msg = 'No se puede procesar el pedido: '
        razon_principal = problemas[0]['razon']
        if razon_principal == 'inactivo':
            msg += f'El ingrediente "{problemas[0]["ingrediente"]}" no está disponible'
        elif razon_principal == 'sin_receta':
            msg += f'El plato "{problemas[0]["menu"]}" aún no tiene receta configurada'
        else:
            msg += f'Falta stock: {problemas[0]["ingrediente"]}'
        return False, msg, problemas
    
    return True, '', []


# ── Carta usuarios ────────────────────────────────────────

def carta_usuarios(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    try:
        _, cliente = _get_cliente(request)
    except Exception:
        return redirect('login')
    tipos = TipoMenu.objects.prefetch_related(
        Prefetch('menu_set', queryset=Menu.objects.filter(disponible_menu=True))
    ).all().order_by('id_tipo_menu_pk')
    
    # Precalcular menús agotados (stock insuficiente para 1 unidad)
    agotados_ids = []
    for tipo in tipos:
        for menu in tipo.menu_set.all():
            es_valido, _, _ = _validar_pedido([{'menu_id': menu.id_menu_pk, 'cantidad': 1}])
            if not es_valido:
                agotados_ids.append(menu.id_menu_pk)

    return render(request, 'usuarios/carta.html', {
        **_ctx_cliente(cliente), 'tipos': tipos, 'agotados_ids': agotados_ids,
    })


# ── Crear pedido ──────────────────────────────────────────

def crear_pedido(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    try:
        _, cliente = _get_cliente(request)
    except Exception:
        return redirect('login')

    carrito_temp = request.session.get('carrito_temporal')
    if not carrito_temp:
        messages.error(request, 'Tu carrito está vacío. Agrega platos antes de continuar.')
        return redirect('carrito_compra')

    ctx_base = {
        **_ctx_cliente(cliente),
        'localidades':   Localidad.objects.all().order_by('nom_local'),
    }

    if request.method == 'POST':
        # CAPA 3: Revalidar stock justo antes de crear pedido
        es_valido, mensaje_error, _ = _validar_pedido(carrito_temp)
        if not es_valido:
            messages.error(request, f"Lo sentimos, el stock cambió: {mensaje_error}")
            return redirect('carrito_compra')

        datos_entrega, errores = _validar_datos_entrega(request)
        if errores:
            ctx_base['post_data'] = request.POST
            ctx_base['errores'] = errores
            return render(request, 'usuarios/index-pedido.html', ctx_base)
            
        request.session['tipo_pedido'] = 'domicilio'
        request.session['datos_entrega'] = datos_entrega
        request.session['notas_pedido'] = request.POST.get('notas_pedido', '').strip() or None

        messages.success(request, '¡Información guardada! Procede al pago para confirmar.')
        return redirect('/usuario/pago/')

    return render(request, 'usuarios/index-pedido.html', ctx_base)


def _validar_datos_entrega(request):
    """Valida los datos de entrega para domicilio con reglas estrictas. Retorna (datos, dict_errores)"""
    import re
    from datetime import datetime, timedelta
    now = datetime.now()

    direc  = request.POST.get('direc_domi', '').strip()
    barrio = request.POST.get('id_barrio_domi_fk')
    fecha  = request.POST.get('fecha_domi')
    hora   = request.POST.get('hora_entrega_domi')
    localidad = request.POST.get('id_localidad')

    errores = {}

    if not direc:
        errores['direc_domi'] = 'La dirección es obligatoria.'
    elif len(direc) < 10:
        errores['direc_domi'] = 'La dirección debe tener al menos 10 caracteres.'
    elif len(direc) > 200:
        errores['direc_domi'] = 'La dirección no puede exceder 200 caracteres.'
    elif not re.search(r'\d', direc):
        errores['direc_domi'] = 'La dirección debe incluir al menos un número (ej: Calle 123 #45-67).'

    if not localidad:
        errores['id_localidad'] = 'Debe seleccionar una localidad.'
        
    if not barrio:
        errores['id_barrio_domi_fk'] = 'Debe seleccionar un barrio.'

    # Como el frontend ahora es "Lo antes posible", forzamos fecha y hora actual
    fecha_obj = now.date()
    hora_obj = now.time()
    
    # Inyectamos de vuelta en POST o datos que devuelve para la base de datos
    request.POST = request.POST.copy()
    request.POST['fecha_domi'] = fecha_obj.strftime('%Y-%m-%d')
    request.POST['hora_entrega_domi'] = hora_obj.strftime('%H:%M')

    notas = request.POST.get('notas_pedido', '').strip()
    if len(notas) > 300:
        errores['notas_pedido'] = 'Las notas no pueden exceder 300 caracteres.'

    if errores:
        return None, errores

    return {
        'direc_domi': direc,
        'fecha_domi': fecha_obj.strftime('%Y-%m-%d'),
        'hora_entrega_domi': hora_obj.strftime('%H:%M'),
        'id_barrio_domi_fk': barrio,
    }, None
# ── Mis pedidos ───────────────────────────────────────────

def mis_pedidos(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    try:
        _, cliente = _get_cliente(request)
    except Exception:
        return redirect('login')

    pedidos = Pedido.objects.filter(
        id_clien_pedido_fk=cliente
    ).prefetch_related(
        'detalles_set__id_menu_fk',
        'domicilios_set__id_barrio_domi_fk',
        'pago_set__id_met_pago_fk',
        'factura_set',
    ).order_by('-fecha_pedido')

    from django.utils import timezone
    from core.models import HistorialEstadoPedido
    now = timezone.now()

    for pedido in pedidos:
        pedido.pago_obj = pedido.pago_set.first()

        if pedido.estado_pedido == 'confirmado':
            historial = HistorialEstadoPedido.objects.filter(
                id_pedido_fk=pedido,
                estado_nuevo='confirmado'
            ).order_by('-fecha_cambio').first()
            fecha_ref = historial.fecha_cambio if historial else pedido.fecha_pedido
            pedido.tiempo_confirmado_excedido = (now - fecha_ref).total_seconds() > 1800
        else:
            pedido.tiempo_confirmado_excedido = False

    context = {
        **_ctx_cliente(cliente), 'pedidos': pedidos,
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'usuarios/_lista_mis_pedidos.html', context)
        
    return render(request, 'usuarios/mis-pedidos.html', context)


# ── Carrito ───────────────────────────────────────────────

def carrito_compra(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
        
    try:
        _, cliente = _get_cliente(request)
    except Exception:
        return redirect('login')

    carrito_temp = request.session.get('carrito_temporal')
    tipos = TipoMenu.objects.prefetch_related('menu_set').order_by('id_tipo_menu_pk')
    
    # Precalcular menús agotados (stock insuficiente para 1 unidad)
    agotados_ids = []
    for tipo in tipos:
        for menu in tipo.menu_set.all():
            es_valido, _, _ = _validar_pedido([{'menu_id': menu.id_menu_pk, 'cantidad': 1}])
            if not es_valido:
                agotados_ids.append(menu.id_menu_pk)
    
    return render(request, 'usuarios/carrito-compra.html', {
        **_ctx_cliente(cliente),
        'carrito_temp': carrito_temp,
        'tipos': tipos,
        'agotados_ids': agotados_ids,
    })


def guardar_carrito(request):
    if request.method != 'POST':
        return redirect('inicio_usuarios')
    if not request.session.get('usuario_id'):
        return redirect('login')

    num_items = int(request.POST.get('num_items', 0))
    if num_items == 0:
        messages.error(request, 'Debes agregar al menos un menú al carrito.')
        return redirect('carrito_compra')

    carrito_temp = []
    total = Decimal('0.00')

    for i in range(num_items):
        menu_id  = request.POST.get(f'menu_id_{i}')
        cantidad = request.POST.get(f'cantidad_{i}')
        if not all([menu_id, cantidad]):
            continue
        try:
            menu = get_object_or_404(Menu, id_menu_pk=menu_id, disponible_menu=True)
            cantidad = int(cantidad)
            precio_u = menu.precio_menu
            subtotal = precio_u * cantidad
            carrito_temp.append({
                'menu_id': menu.id_menu_pk,
                'cantidad': cantidad,
                'precio_u': str(precio_u),
                'subtotal': str(subtotal),
            })
            total += subtotal
        except Exception:
            continue

    # Validar que el pedido sea posible
    es_valido, mensaje_error, problemas = _validar_pedido(carrito_temp)
    if not es_valido:
        messages.error(request, mensaje_error)
        return redirect('carrito_compra')

    request.session['carrito_temporal'] = carrito_temp
    request.session['total_temporal'] = str(total)
    
    messages.info(request, 'Carrito guardado. Ahora completa los datos de entrega.')
    return redirect('crear_pedido')

def alertar_falta_stock(request, id_menu):
    if request.method == 'POST':
        menu = get_object_or_404(Menu, id_menu_pk=id_menu)
        
        for rol in ['admin', 'empleado']:
            _crear_notificacion(
                tipo='sistema',
                titulo='Falta de stock reportada',
                mensaje=f"Un cliente intentó pedir '{menu.nom_menu}' pero no hay ingredientes suficientes.",
                destinatario_rol=rol,
            )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


def cancelar_pedido(request):
    request.session.pop('carrito_temporal', None)
    request.session.pop('total_temporal', None)
    messages.info(request, 'Pedido cancelado. El carrito ha sido vaciado.')
    return redirect('inicio_usuarios')


def cancelar_pedido_usuario(request, id_pedido):
    """Cancela un pedido desde la página Mis Pedidos siguiendo las reglas de pago y tiempo."""
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.method != 'POST':
        return redirect('mis_pedidos')
    try:
        _, cliente = _get_cliente(request)
        pedido = get_object_or_404(Pedido, id_pedido_pk=id_pedido, id_clien_pedido_fk=cliente)
        
        # Validar si ya está cancelado o entregado
        if pedido.estado_pedido in ['cancelado', 'entregado', 'listo']:
            messages.error(request, 'No puedes cancelar este pedido en su estado actual.')
            return redirect('mis_pedidos')

        # Buscar estado de pago
        factura = pedido.factura_set.first()
        pago = factura.pago_set.first() if factura else None
        
        # Reglas por método de pago
        metodo = pago.id_met_pago_fk.tipo_met_pago if pago else 'efectivo'
        if metodo == 'efectivo':
            if pedido.estado_pedido == 'preparando':
                messages.error(request, 'No puedes cancelar un pedido que ya se está preparando.')
                return redirect('mis_pedidos')
        elif metodo in ['nequi', 'bancolombia']:
            if pago and pago.estado_pago == 'completado':
                messages.error(request, 'El pago de este pedido ya fue verificado. Debes contactar al restaurante para cancelarlo y gestionar la devolución.')
                return redirect('mis_pedidos')
        elif metodo == 'stripe':
            if pago and pago.estado_pago == 'completado':
                messages.error(request, 'El pago ya fue procesado por Stripe. Debes contactar al restaurante para la cancelación y reembolso.')
                return redirect('mis_pedidos')

        motivo = request.POST.get('motivo_cancelacion') or 'Cancelado por el cliente'

        # Regla de límite de tiempo (>30 mins confirmado)
        from django.utils import timezone
        import datetime
        now = timezone.now()
        # Buscamos cuándo pasó a confirmado
        from core.models import HistorialEstadoPedido, Notificacion, UsuarioAuth
        historial = HistorialEstadoPedido.objects.filter(id_pedido_fk=pedido, estado_nuevo='confirmado').order_by('-fecha_cambio').first()
        fecha_ref = historial.fecha_cambio if historial else pedido.fecha_pedido
        
        if pedido.estado_pedido == 'confirmado' and (now - fecha_ref).total_seconds() > 1800:
            # Enviar solicitud de cancelación
            pedido.solicitud_cancelacion_pendiente = True
            pedido.motivo_solicitud_cancelacion = motivo
            pedido.fecha_solicitud_cancelacion = now
            pedido.save()
            
            for rol in ['admin', 'empleado']:
                _crear_notificacion(
                    tipo='cancelacion',
                    titulo=f'Solicitud de cancelación Pedido #PED-{id_pedido:04d}',
                    mensaje=f'El cliente {cliente.nom_clien} solicita cancelar el pedido #PED-{id_pedido:04d} (lleva >30m confirmado). Motivo: {motivo}',
                    destinatario_rol=rol,
                    id_auth_origen=get_object_or_404(UsuarioAuth, id_auth_pk=request.session['usuario_id']),
                    pedido=pedido,
                )
            messages.success(request, 'Se ha enviado tu solicitud de cancelación. Te notificaremos cuando el restaurante la apruebe.')
            return redirect('mis_pedidos')

        # Si pasa todas las validaciones, procedemos a cancelar directamente
        estado_anterior = pedido.estado_pedido
        pedido.estado_pedido = 'cancelado'
        pedido.notas_pedido = motivo
        pedido.save()


        for dom in pedido.domicilios_set.all():
            dom.estado_domi = 'cancelado'
            dom.save()

        usuario_auth = get_object_or_404(UsuarioAuth, id_auth_pk=request.session['usuario_id'])
        HistorialEstadoPedido.objects.create(
            id_pedido_fk=pedido,
            estado_anterior=estado_anterior,
            estado_nuevo='cancelado',
            id_auth_fk=usuario_auth,
            notas=motivo
        )

        # ── Notificaciones de cancelación ──
        _crear_notificacion(
            tipo='cancelacion',
            titulo=f'{cliente.nom_clien} canceló el pedido #PED-{id_pedido:04d}',
            mensaje=f'{cliente.nom_clien} canceló el pedido #PED-{id_pedido:04d}. Motivo: {motivo}',
            destinatario_rol='admin',
            id_auth_origen=usuario_auth,
            pedido=pedido,
        )
        _crear_notificacion(
            tipo='cancelacion',
            titulo=f'Tu pedido #PED-{id_pedido:04d} fue cancelado',
            mensaje=f'Tu pedido #PED-{id_pedido:04d} ha sido cancelado exitosamente.',
            destinatario_rol='cliente',
            id_auth_destino=usuario_auth,
            pedido=pedido,
        )

        messages.success(request, f'Pedido #PED-{id_pedido:04d} cancelado correctamente.')
    except Exception as e:
        messages.error(request, f'No se pudo cancelar el pedido: {e}')
    return redirect('mis_pedidos')


def marcar_entregado_usuario(request, id_pedido):
    """Marca un pedido como entregado desde la página Mis Pedidos."""
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.method != 'POST':
        return redirect('mis_pedidos')
    try:
        _, cliente = _get_cliente(request)
        pedido = get_object_or_404(Pedido, id_pedido_pk=id_pedido, id_clien_pedido_fk=cliente)
        if pedido.estado_pedido in ('cancelado', 'entregado'):
            messages.error(request, 'No puedes marcar este pedido como entregado en su estado actual.')
            return redirect('mis_pedidos')
            
        pedido.estado_pedido = 'entregado'
        pedido.save()
        
        # Generar factura y asociar pago
        _generar_factura_si_entregado(pedido)
        
        Notificacion.objects.filter(titulo__contains=f'pedido #PED-{pedido.id_pedido_pk:04d}', tipo='pedido').update(leida=True)
        
        # Marcar domicilios como entregados
        for domi in pedido.domicilios_set.all():
            domi.estado_domi = 'entregado'
            domi.save()

        # ── Notificaciones de entrega confirmada ──
        usuario_auth = UsuarioAuth.objects.get(id_auth_pk=request.session['usuario_id'])
        _crear_notificacion(
            tipo='pedido',
            titulo=f'Pedido #PED-{id_pedido:04d} fue entregado. ¡Buen provecho!',
            mensaje=f'Tu pedido #PED-{id_pedido:04d} fue entregado. ¡Buen provecho!',
            destinatario_rol='cliente',
            id_auth_destino=usuario_auth,
            pedido=pedido,
        )
        _crear_notificacion(
            tipo='pedido',
            titulo=f'Pedido #PED-{id_pedido:04d} marcado como entregado',
            mensaje=f'Pedido #PED-{id_pedido:04d} marcado como entregado por el cliente {cliente.nom_clien}',
            destinatario_rol='admin',
            id_auth_origen=usuario_auth,
            pedido=pedido,
        )

        messages.success(request, f'Pedido #PED-{id_pedido:04d} marcado como completado. ¡Gracias por confirmar!')
    except Exception as e:
        messages.error(request, f'No se pudo actualizar el pedido: {e}')
    return redirect('mis_pedidos')


# ── Stock AJAX ────────────────────────────────────────────

def verificar_stock_menu(request, menu_id):
    from django.http import JsonResponse
    from core.models import RecetaMenu
    try:
        qty = int(request.GET.get('qty', 1))
        menu    = get_object_or_404(Menu, id_menu_pk=menu_id, disponible_menu=True)
        recetas = RecetaMenu.objects.select_related(
            'id_produ_fk', 'id_uni_medi_fk',
            'id_produ_fk__id_uni_medi_produ_fk'
        ).filter(id_menu_fk=menu)

        if not recetas.exists():
            return JsonResponse({
                'disponible': True, 'tiene_receta': False,
                'advertencia': False, 'ingredientes_bajos': [],
                'mensaje': 'Menú disponible.',
            })

        FACTORES_CONVERSION = None  # replaced by utils
        from core.utils import convertir_a_unidad_base

        bajos = []
        for receta in recetas:
            prod  = receta.id_produ_fk
            stock = prod.stock_actual_produ
            try:
                requerido = convertir_a_unidad_base(
                    receta.cantidad_reque,
                    receta.id_uni_medi_fk,
                    prod.id_uni_medi_produ_fk
                ) * Decimal(str(qty))
            except ValueError:
                requerido = receta.cantidad_reque * Decimal(str(qty))

            if stock < requerido:
                bajos.append({
                    'ingrediente':  prod.nom_produ,
                    'stock_actual': float(stock),
                    'requerido':    float(requerido),
                    'unidad':       prod.id_uni_medi_produ_fk.abreviatura,
                })

        if bajos:
            nombres = ', '.join(i['ingrediente'] for i in bajos[:3])
            return JsonResponse({
                'disponible': False, 'tiene_receta': True,
                'advertencia': True, 'ingredientes_bajos': bajos,
                'mensaje': f'Falta inventario (ej: {nombres}). No se puede preparar la cantidad solicitada.',
            })

        return JsonResponse({
            'disponible': True, 'tiene_receta': True,
            'advertencia': False, 'ingredientes_bajos': [],
            'mensaje': 'Stock suficiente.',
        })

    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({
            'disponible': True, 'advertencia': False,
            'mensaje': 'No se pudo verificar el stock.', 'error': str(e),
        })


def notificar_stock_admin(request):
    """Recibe aviso AJAX de stock insuficiente desde el carrito del cliente."""
    from django.http import JsonResponse
    import logging
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)

    try:
        import json
        datos  = json.loads(request.body)
        menu   = datos.get('menu_nombre', 'Desconocido')
        motivo = datos.get('mensaje', '')
        
        # Obtener nombre real del cliente desde BD
        try:
            _, cliente = _get_cliente(request)
            nombre_cliente = cliente.nom_clien
        except Exception:
            nombre_cliente = request.session.get('usuario', 'Un cliente')

        # Obtener UsuarioAuth para FK de notificación
        auth_origen = None
        uid = request.session.get('usuario_id')
        if uid:
            try:
                auth_origen = UsuarioAuth.objects.get(id_auth_pk=uid)
            except UsuarioAuth.DoesNotExist:
                pass

        logger = logging.getLogger('django')
        logger.warning(f'[STOCK] {nombre_cliente} no pudo pedir "{menu}". Motivo: {motivo}')
        
        mensaje = f'El cliente {nombre_cliente} intentó agregar "{menu}" pero {motivo}'

        _crear_notificacion(
            tipo='inventario',
            titulo=f'Falta stock para: {menu}',
            mensaje=mensaje,
            destinatario_rol='admin',
            id_auth_origen=auth_origen
        )
        _crear_notificacion(
            tipo='inventario',
            titulo=f'Falta stock para: {menu}',
            mensaje=mensaje,
            destinatario_rol='empleado',
            id_auth_origen=auth_origen
        )

        return JsonResponse({'ok': True, 'mensaje': '¡Notificación enviada al restaurante!'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


def verificar_carrito_completo(request):
    """Verifica si el carrito completo se puede preparar con el stock actual."""
    from django.http import JsonResponse
    import json
    
    if request.method != 'POST':
        return JsonResponse({'es_valido': False, 'mensaje_error': 'Método no permitido'}, status=405)
        
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        
        # Validar el pedido completo
        es_valido, msg_error, problemas = _validar_pedido(items)
        
        return JsonResponse({
            'es_valido': es_valido,
            'mensaje_error': msg_error,
        })
    except Exception as e:
        return JsonResponse({'es_valido': False, 'mensaje_error': str(e)}, status=500)


# ── Pedidos admin ─────────────────────────────────────────

from django.utils import timezone
from datetime import timedelta

def pedidos_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')

    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())

    pedidos = Pedido.objects.select_related(
        'id_clien_pedido_fk', 'id_emple_pedido_fk',
    ).prefetch_related(
        'domicilios_set__id_barrio_domi_fk',
    ).distinct().order_by('-fecha_pedido')

    domicilios_hoy = Domicilio.objects.filter(fecha_domi=hoy).distinct().count()
    domicilios_semana = Domicilio.objects.filter(fecha_domi__gte=inicio_semana).distinct().count()

    return render(request, 'admin/pedido/pedido.html', {
        'pedidos':        pedidos,
        'empleados':      Empleado.objects.filter(estado_emple='activo').order_by('nom_emple'),
        'estados_pedido': Pedido.ESTADOS,
        'domicilios_hoy': domicilios_hoy,
        'domicilios_semana': domicilios_semana,
    })


def cambiar_estado_pedido(request, id_pedido):
    rol = request.session.get('rol')
    if rol not in ['admin', 'empleado']:
        return redirect('login')
        
    if rol == 'empleado':
        from core.models import ConfiguracionSistema
        permite_empleados, _ = ConfiguracionSistema.objects.get_or_create(clave='permite_empleados_cambiar_estado', defaults={'valor_booleano': False})
        if not permite_empleados.valor_booleano:
            messages.error(request, 'No tienes permiso para cambiar el estado de los pedidos. Solicita autorización al administrador.')
            return redirect('pedidos_empleado')

    if request.method == 'POST':
        pedido       = get_object_or_404(Pedido, id_pedido_pk=id_pedido)
        nuevo_estado = request.POST.get('estado_pedido')
        if nuevo_estado in [v for v, _ in Pedido.ESTADOS]:
            estado_anterior = pedido.estado_pedido
            pedido.estado_pedido = nuevo_estado
            pedido.save()
            
            # Descontar stock al iniciar preparación
            if nuevo_estado == 'preparando' and estado_anterior != 'preparando':
                _descontar_stock_pedido(pedido)
            
            # Confirmar pago automáticamente al iniciar preparación
            if nuevo_estado in ['preparando', 'listo', 'entregado']:
                pago = pedido.pago_set.first()
                if pago and pago.estado_pago == 'pendiente':
                    pago.estado_pago = 'completado'
                    pago.save()

            if nuevo_estado == 'entregado':
                # Generar factura y asociar pago
                _generar_factura_si_entregado(pedido)
                Notificacion.objects.filter(titulo__contains=f'pedido #PED-{pedido.id_pedido_pk:04d}', tipo='pedido').update(leida=True)

            # ── Notificación al cliente sobre cambio de estado ──
            cliente = pedido.id_clien_pedido_fk
            if cliente and cliente.id_auth_fk:
                estados_msg = {
                    'confirmado': f'Tu pedido #PED-{pedido.id_pedido_pk:04d} fue confirmado y está siendo preparado',
                    'en_preparacion': f'Tu pedido #PED-{pedido.id_pedido_pk:04d} está siendo preparado',
                    'en_camino': f'Tu pedido #PED-{pedido.id_pedido_pk:04d} ya está en camino',
                    'entregado': f'Tu pedido #PED-{pedido.id_pedido_pk:04d} fue entregado. ¡Buen provecho!',
                    'cancelado': f'Tu pedido #PED-{pedido.id_pedido_pk:04d} fue cancelado por el administrador',
                }
                msg = estados_msg.get(nuevo_estado)
                if msg:
                    _crear_notificacion(
                        tipo='pedido' if nuevo_estado != 'cancelado' else 'cancelacion',
                        titulo=msg,
                        mensaje=msg,
                        destinatario_rol='cliente',
                        id_auth_destino=cliente.id_auth_fk,
                        pedido=pedido,
                    )

            messages.success(request, f'Estado actualizado a "{nuevo_estado}".')
        else:
            messages.error(request, 'Estado no válido.')
    return redirect('pedidos_admin')


def asignar_empleado_pedido(request, id_pedido):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    if request.method == 'POST':
        pedido      = get_object_or_404(Pedido, id_pedido_pk=id_pedido)
        id_empleado = request.POST.get('id_emple_pedido_fk')
        pedido.id_emple_pedido_fk = (
            get_object_or_404(Empleado, id_emple_pk=id_empleado) if id_empleado else None
        )
        pedido.save()
        messages.success(request, 'Empleado asignado correctamente.')
    return redirect('pedidos_admin')


def detalle_pedido(request, id_pedido):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    pedido = get_object_or_404(
        Pedido.objects.select_related(
            'id_clien_pedido_fk', 'id_emple_pedido_fk',
        ).prefetch_related(
            'domicilios_set__id_barrio_domi_fk',
            'detalles_set__id_menu_fk',
        ),
        id_pedido_pk=id_pedido
    )
    return render(request, 'admin/pedido/detalle-domicilio.html', {'pedido': pedido})


# ── Pago ──────────────────────────────────────────────────

def pago_pedido(request):
    from django.db import transaction

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    try:
        _, cliente = _get_cliente(request)
    except Exception:
        return redirect('login')

    # Si no hay carrito temporal en la sesión, significa que no hay pedido pendiente por pagar
    carrito_temp = request.session.get('carrito_temporal')
    total_temp = request.session.get('total_temporal')
    tipo_pedido = request.session.get('tipo_pedido')
    datos_entrega = request.session.get('datos_entrega')
    
    if not carrito_temp or not total_temp or not tipo_pedido or not datos_entrega:
        messages.error(request, 'No hay ningún pedido pendiente de pago.')
        return redirect('mis_pedidos')

    if request.method == 'POST':
        metodo_id  = request.POST.get('id_met_pago_fk')
        referencia = request.POST.get('referencia_pago', '').strip()

        if not metodo_id:
            messages.error(request, 'Selecciona un método de pago.')
            return redirect('/usuario/pago/')

        try:
            with transaction.atomic():
                # 1. Revalidar stock
                es_valido, msg_error, _ = _validar_pedido(carrito_temp)
                if not es_valido:
                    raise ValueError(f"Falta stock: {msg_error}")

                # 2. Crear Pedido
                pedido = Pedido.objects.create(
                    estado_pedido      = 'pendiente',
                    total_pedido       = Decimal(str(total_temp)),
                    notas_pedido       = request.session.get('notas_pedido'),
                    id_clien_pedido_fk = cliente,
                )

                # 3. Crear Domicilio
                Domicilio.objects.create(
                    direc_domi        = datos_entrega['direc_domi'],
                    fecha_domi        = datos_entrega['fecha_domi'],
                    hora_entrega_domi = datos_entrega['hora_entrega_domi'],
                    estado_domi       = 'pendiente',
                    id_pedido_domi_fk = pedido,
                    id_barrio_domi_fk = get_object_or_404(Barrio, id_barrio_pk=datos_entrega['id_barrio_domi_fk']),
                )

                # 4. Crear Detalles
                for item in carrito_temp:
                    menu = get_object_or_404(Menu, id_menu_pk=item['menu_id'])
                    DetallePedidoMenu.objects.create(
                        id_pedido_fk    = pedido,
                        id_menu_fk      = menu,
                        cant_detalle    = item['cantidad'],
                        precio_unitario = Decimal(str(item['precio_u'])),
                        subtotal        = Decimal(str(item['subtotal'])),
                    )

                # 6. Pago
                metodo, _ = MetodoPago.objects.get_or_create(tipo_met_pago=metodo_id)
                ahora   = dt.now()

                # Capturar los campos nuevos
                comprobante = None
                celular = None
                titular = None
                monto_efectivo = None

                if metodo.tipo_met_pago == 'nequi':
                    celular = request.POST.get('celular_origen', '').strip()
                    if 'comprobante_img' in request.FILES:
                        comprobante = request.FILES['comprobante_img']
                
                elif metodo.tipo_met_pago == 'bancolombia':
                    titular = request.POST.get('nombre_titular', '').strip()
                    referencia = request.POST.get('referencia_pago', '').strip()
                    if 'comprobante_img' in request.FILES:
                        comprobante = request.FILES['comprobante_img']
                
                elif metodo.tipo_met_pago == 'efectivo':
                    m_txt = request.POST.get('monto_con_el_que_paga')
                    if m_txt:
                        try:
                            monto_efectivo = Decimal(m_txt)
                        except:
                            pass

                Pago.objects.create(
                    fecha_pago       = ahora.date(),
                    hora_pago        = ahora.time(),
                    monto_pago       = pedido.total_pedido,
                    estado_pago      = 'pendiente',
                    referencia_pago  = referencia or None,
                    id_met_pago_fk   = metodo,
                    id_pedido_pago_fk = pedido,
                    celular_origen   = celular or None,
                    nombre_titular   = titular or None,
                    comprobante_img  = comprobante,
                    monto_con_el_que_paga = monto_efectivo
                )

                # ── Notificaciones de pedido confirmado y pago ──
                usuario_auth = UsuarioAuth.objects.get(id_auth_pk=request.session['usuario_id'])
                
                notas_extra = f" | Notas: {pedido.notas_pedido}" if pedido.notas_pedido else ""
                mensaje_admin = f'Nuevo pedido #PED-{pedido.id_pedido_pk:04d} de {cliente.nom_clien} por ${pedido.total_pedido:,.0f}{notas_extra}'
                
                _crear_notificacion(
                    tipo='pedido',
                    titulo=f'Nuevo pedido #PED-{pedido.id_pedido_pk:04d} de {cliente.nom_clien}',
                    mensaje=mensaje_admin,
                    destinatario_rol='admin',
                    id_auth_origen=usuario_auth,
                    pedido=pedido,
                )
                
                _crear_notificacion(
                    tipo='pedido',
                    titulo=f'Nuevo pedido #PED-{pedido.id_pedido_pk:04d} de {cliente.nom_clien}',
                    mensaje=mensaje_admin,
                    destinatario_rol='empleado',
                    id_auth_origen=usuario_auth,
                    pedido=pedido,
                )

                # Notificación de Pago para cliente
                _crear_notificacion(
                    tipo='pago',
                    titulo=f'Pago del pedido #PED-{pedido.id_pedido_pk:04d} registrado',
                    mensaje=f'El pago de tu pedido #PED-{pedido.id_pedido_pk:04d} por ${pedido.total_pedido:,.0f} ha sido registrado exitosamente.',
                    destinatario_rol='cliente',
                    id_auth_destino=usuario_auth,
                    pedido=pedido,
                    factura=None,
                )



            # ── Limpiar sesión (fuera del atomic, después de commit exitoso) ──
            request.session.pop('carrito_temporal', None)
            request.session.pop('total_temporal', None)
            request.session.pop('tipo_pedido', None)
            request.session.pop('datos_entrega', None)
            request.session.pop('notas_pedido', None)
            request.session.pop('pedido_activo_id', None)

            if metodo.tipo_met_pago == 'stripe':
                return redirect('iniciar_pago_stripe', pedido_id=pedido.id_pedido_pk)
            else:
                messages.success(request, f'¡Pago registrado exitosamente para el Pedido #PED-{pedido.id_pedido_pk:04d}!')
                return redirect(f'/usuario/pago/exito/?pedido_id={pedido.id_pedido_pk}')
        except ValueError as ve:
            messages.error(request, str(ve))
            return redirect('/usuario/pago/')
        except Exception as e:
            messages.error(request, f'Error al procesar el pago: {e}')
            return redirect('/usuario/pago/')

    # ── GET: Construir contexto de "vista previa" usando la sesión ──
    from types import SimpleNamespace

    detalles_preview = []
    for item in carrito_temp:
        det = SimpleNamespace(
            id_menu_fk=SimpleNamespace(nom_menu=item.get('nombre', '')),
            cant_detalle=item['cantidad'],
            subtotal=Decimal(str(item['subtotal'])),
        )
        detalles_preview.append(det)

    pedido_preview = SimpleNamespace(
        id_pedido_pk='(nuevo)',
        tipo_pedido=tipo_pedido,
        total_pedido=Decimal(str(total_temp)),
        notas_pedido=request.session.get('notas_pedido'),
        domicilios_set=SimpleNamespace(all=lambda: []),
    )

    return render(request, 'usuarios/index-pago-factura.html', {
        **_ctx_cliente(cliente),
        'pedido':   pedido_preview,
        'detalles': detalles_preview,
    })


def pago_exito(request):
    usuario_id = request.session.get('usuario_id')
    stripe_success = request.GET.get('stripe_success')
    pedido_id = request.GET.get('pedido_id')
    
    if not usuario_id:
        return redirect('mis_pedidos')

    try:
        _, cliente = _get_cliente(request)
        pedido = Pedido.objects.get(id_pedido_pk=pedido_id, id_clien_pedido_fk=cliente)

        # Procesar pago sincrono si viene redireccionado desde Stripe
        if stripe_success == 'true' and pedido_id:
            if pedido.estado_pedido != 'confirmado':
                # Buscar pago existente creado al enviar el pedido
                pago = pedido.pago_set.first()
                if pago:
                    pago.estado_pago = 'completado'
                    pago.save()
                else:
                    # Fallback si por alguna razón no se crearon
                    metodo, _ = MetodoPago.objects.get_or_create(tipo_met_pago='stripe')
                    from datetime import datetime as dt
                    ahora = dt.now()
                    Pago.objects.create(
                        fecha_pago = ahora.date(),
                        hora_pago = ahora.time(),
                        monto_pago = pedido.total_pedido,
                        estado_pago = 'completado',
                        id_met_pago_fk = metodo,
                        id_pedido_pago_fk = pedido
                    )
                pedido.estado_pedido = 'confirmado'
                pedido.save()


        if not pedido_id:
            return redirect('mis_pedidos')

        pedido = Pedido.objects.select_related(
            'id_clien_pedido_fk'
        ).prefetch_related(
            'detalles_set__id_menu_fk',
            'domicilios_set__id_barrio_domi_fk',
            'pago_set__id_met_pago_fk',
        ).get(id_pedido_pk=pedido_id, id_clien_pedido_fk=cliente)
    except Exception as e:
        return redirect('mis_pedidos')

    detalles = pedido.detalles_set.all()
    pago     = pedido.pago_set.first()
    # Factura no existe todavía, por lo que factura=None
    factura  = None

    return render(request, 'usuarios/pago-exito.html', {
        **_ctx_cliente(cliente),
        'factura':  factura,
        'pedido':   pedido,
        'detalles': detalles,
        'pago':     pago,
    })


def descargar_factura(request, factura_id):
    from django.http import HttpResponse
    usuario_id = request.session.get('usuario_id')
    rol = request.session.get('rol')
    if not usuario_id:
        return redirect('login')

    try:
        es_admin = rol in ['admin', 'empleado']
        cliente = None
        if not es_admin:
            _, cliente = _get_cliente(request)
            
        factura = Factura.objects.select_related(
            'id_pedido_factu_fk',
        ).prefetch_related(
            'id_pedido_factu_fk__detalles_set__id_menu_fk',
            'id_pedido_factu_fk__pago_set__id_met_pago_fk',
        ).get(id_factu_pk=int(factura_id))

        if not es_admin and factura.id_clien_factu_fk != cliente:
            messages.error(request, 'No tienes permiso para ver esta factura.')
            return redirect('mis_pedidos')

    except Factura.DoesNotExist:
        messages.error(request, f'Factura #{factura_id} no existe.')
        return redirect('mis_pedidos')
    except Exception as e:
        messages.error(request, f'Error técnico: {e}')
        return redirect('mis_pedidos')

    pedido   = factura.id_pedido_factu_fk
    cliente  = factura.id_clien_factu_fk
    detalles = pedido.detalles_set.all()
    pago     = pedido.pago_set.first()
    metodo = pago.id_met_pago_fk.tipo_met_pago if pago else 'No registrado'

    filas = ''.join(
        f"<tr><td>{d.id_menu_fk.nom_menu}</td>"
        f"<td style='text-align:center'>{d.cant_detalle}</td>"
        f"<td style='text-align:right'>${d.precio_unitario:,.0f}</td>"
        f"<td style='text-align:right'>${d.subtotal:,.0f}</td></tr>"
        for d in detalles
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Factura #{factura.id_factu_pk} — La Paella Real</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 2.5rem; color: #1A1510; max-width: 750px; margin: auto; }}
        h1   {{ color: #C8973A; font-size: 1.6rem; margin-bottom: .25rem; }}
        .sub {{ color: #6B6560; font-size: .9rem; margin-bottom: 1.5rem; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: .5rem 2rem; margin-bottom: 1.5rem; }}
        .info-grid p {{ margin: 0; font-size: .9rem; }}
        .info-grid span {{ font-weight: 700; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th    {{ background: #f5f0ea; padding: .6rem 1rem; text-align: left; font-size: .85rem; }}
        td    {{ padding: .6rem 1rem; border-bottom: 1px solid #EDE8E2; font-size: .9rem; }}
        .total-row {{ background: #9B2335; color: #fff; font-weight: 700; font-size: 1rem; }}
        .total-row td {{ border: none; padding: .8rem 1rem; }}
        .footer {{ margin-top: 2rem; font-size: .8rem; color: #6B6560; text-align: center; border-top: 1px solid #EDE8E2; padding-top: 1rem; }}
    </style>
</head>
<body>
    <h1>La Paella Real</h1>
    <p class="sub">Factura de compra</p>
    <div class="info-grid">
        <p>Factura N°: <span>#{factura.id_factu_pk}</span></p>
        <p>Pedido N°: <span>#PED-{pedido.id_pedido_pk:04d}</span></p>
        <p>Fecha: <span>{factura.fecha_factu}</span></p>
        <p>Hora: <span>{factura.hora_factu}</span></p>
        <p>Cliente: <span>{cliente.nom_clien} {cliente.apellido_clien}</span></p>
        <p>Método de pago: <span>{metodo}</span></p>
    </div>
    <table>
        <thead>
            <tr>
                <th>Menú</th>
                <th style="text-align:center">Cantidad</th>
                <th style="text-align:right">Precio unitario</th>
                <th style="text-align:right">Subtotal</th>
            </tr>
        </thead>
        <tbody>
            {filas}
            <tr class="total-row">
                <td colspan="3">Total Pagado</td>
                <td style="text-align:right">${pedido.total_pedido:,.0f}</td>
            </tr>
        </tbody>
    </table>
    <p class="footer">Gracias por tu pedido · La Paella Real · 300 123 4567</p>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script>
        window.onload = function() {{
            var element = document.body;
            var opt = {{
              margin:       0.5,
              filename:     'factura-{factura.id_factu_pk}.pdf',
              image:        {{ type: 'jpeg', quality: 0.98 }},
              html2canvas:  {{ scale: 2 }},
              jsPDF:        {{ unit: 'in', format: 'letter', orientation: 'portrait' }}
            }};
            html2pdf().set(opt).from(element).save().then(function() {{ setTimeout(function() {{ window.close(); }}, 500); }});
        }}
    </script>
</body>
</html>"""

    response = HttpResponse(html, content_type='text/html; charset=utf-8')
    return response


def ver_factura(request, factura_id):
    from django.http import HttpResponse
    usuario_id = request.session.get('usuario_id')
    rol = request.session.get('rol')
    if not usuario_id:
        return redirect('login')

    try:
        es_admin = rol in ['admin', 'empleado']
        cliente = None
        if not es_admin:
            _, cliente = _get_cliente(request)
            
        factura = Factura.objects.select_related(
            'id_pedido_factu_fk',
        ).prefetch_related(
            'id_pedido_factu_fk__detalles_set__id_menu_fk',
            'pago_set__id_met_pago_fk',
        ).get(id_factu_pk=int(factura_id))

        if not es_admin and factura.id_clien_factu_fk != cliente:
            messages.error(request, 'No tienes permiso para ver esta factura.')
            return redirect('mis_pedidos')

    except Factura.DoesNotExist:
        messages.error(request, f'Factura #{factura_id} no existe.')
        return redirect('mis_pedidos')
    except Exception as e:
        messages.error(request, f'Error técnico: {e}')
        return redirect('mis_pedidos')

    pedido   = factura.id_pedido_factu_fk
    detalles = pedido.detalles_set.all()
    pago     = factura.pago_set.first()
    metodo = pago.id_met_pago_fk.tipo_met_pago if pago else 'No registrado'

    filas = ''.join(
        f"<tr><td>{d.id_menu_fk.nom_menu}</td>"
        f"<td style='text-align:center'>{d.cant_detalle}</td>"
        f"<td style='text-align:right'>${d.precio_unitario:,.0f}</td>"
        f"<td style='text-align:right'>${d.subtotal:,.0f}</td></tr>"
        for d in detalles
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Factura #{factura.id_factu_pk} — La Paella Real</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 2.5rem; color: #1A1510; max-width: 750px; margin: auto; }}
        h1   {{ color: #C8973A; font-size: 1.6rem; margin-bottom: .25rem; }}
        .sub {{ color: #6B6560; font-size: .9rem; margin-bottom: 1.5rem; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: .5rem 2rem; margin-bottom: 1.5rem; }}
        .info-grid p {{ margin: 0; font-size: .9rem; }}
        .info-grid span {{ font-weight: 700; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th    {{ background: #f5f0ea; padding: .6rem 1rem; text-align: left; font-size: .85rem; }}
        td    {{ padding: .6rem 1rem; border-bottom: 1px solid #EDE8E2; font-size: .9rem; }}
        .total-row {{ background: #9B2335; color: #fff; font-weight: 700; font-size: 1rem; }}
        .total-row td {{ border: none; padding: .8rem 1rem; }}
        .footer {{ margin-top: 2rem; font-size: .8rem; color: #6B6560; text-align: center; border-top: 1px solid #EDE8E2; padding-top: 1rem; }}
    </style>
</head>
<body>
    <h1>La Paella Real</h1>
    <p class="sub">Factura de compra</p>
    <div class="info-grid">
        <p>Factura N°: <span>#{factura.id_factu_pk}</span></p>
        <p>Pedido N°: <span>#PED-{pedido.id_pedido_pk:04d}</span></p>
        <p>Fecha: <span>{factura.fecha_factu}</span></p>
        <p>Hora: <span>{factura.hora_factu}</span></p>
        <p>Cliente: <span>{cliente.nom_clien} {cliente.apellido_clien}</span></p>
        <p>Método de pago: <span>{metodo}</span></p>
    </div>
    <table>
        <thead>
            <tr>
                <th>Menú</th>
                <th style="text-align:center">Cantidad</th>
                <th style="text-align:right">Precio unitario</th>
                <th style="text-align:right">Subtotal</th>
            </tr>
        </thead>
        <tbody>
            {filas}
            <tr class="total-row">
                <td colspan="3">Total Pagado</td>
                <td style="text-align:right">${pedido.total_pedido:,.0f}</td>
            </tr>
        </tbody>
    </table>
    <p class="footer">Gracias por tu pedido · La Paella Real · 300 123 4567</p>
    <div style="text-align:center; margin-top: 30px;" class="no-print">
        <button onclick="window.print()" style="background:#C8973A; color:white; border:none; padding:10px 20px; font-size:16px; border-radius:5px; cursor:pointer;">Imprimir Factura</button>
    </div>
    <style>
        @media print {{
            .no-print {{ display: none !important; }}
        }}
    </style>
</body>
</html>"""

    response = HttpResponse(html, content_type='text/html; charset=utf-8')
    return response


def tabla_domicilios_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    domicilios = Domicilio.objects.select_related(
        'id_pedido_domi_fk__id_clien_pedido_fk',
        'id_barrio_domi_fk',
    ).order_by('-id_domi_pk')
    
    if request.headers.get('HX-Request'):
        return render(request, 'admin/pedido/_lista_domicilios_admin.html', {
            'domicilios': domicilios,
        })
        
    return render(request, 'admin/pedido/tabla-domicilio.html', {
        'domicilios': domicilios,
    })





def detalle_domicilio(request, id_domicilio):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    domicilio = get_object_or_404(
        Domicilio.objects.select_related(
            'id_pedido_domi_fk__id_clien_pedido_fk',
            'id_barrio_domi_fk',
            'id_pedido_domi_fk__id_emple_pedido_fk',
        ).prefetch_related(
            'id_pedido_domi_fk__detalles_set__id_menu_fk',
            'id_pedido_domi_fk__factura_set__pago_set__id_met_pago_fk',
        ),
        id_domi_pk=id_domicilio
    )
    pedido   = domicilio.id_pedido_domi_fk
    factura  = pedido.factura_set.first()
    pago     = pedido.pago_set.first() or (factura.pago_set.first() if factura else None)
    from core.models import HistorialEstadoPedido
    historial = HistorialEstadoPedido.objects.filter(id_pedido_fk=pedido).select_related('id_auth_fk').order_by('fecha_cambio')
    empleados = Empleado.objects.filter(estado_emple='activo')
    return render(request, 'admin/pedido/detalle-domicilio.html', {
        'domicilio': domicilio,
        'pedido':    pedido,
        'factura':   factura,
        'pago':      pago,
        'historial': historial,
        'empleados': empleados,
    })


def marcar_domicilio_entregado_admin(request, id_domicilio):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    if request.method == 'POST':
        domicilio = get_object_or_404(Domicilio, id_domi_pk=id_domicilio)
        pedido = domicilio.id_pedido_domi_fk
        
        if pedido.estado_pedido == 'cancelado':
            messages.error(request, 'No puedes entregar un pedido que está cancelado.')
            return redirect('detalle_domicilio', id_domicilio=id_domicilio)

        domicilio.estado_domi = 'entregado'
        domicilio.save()
        
        pedido.estado_pedido = 'entregado'
        pedido.save()

        # Generar factura y asociar pago
        _generar_factura_si_entregado(pedido)

        from core.models import Notificacion
        Notificacion.objects.filter(titulo=f'Nuevo pedido #PED-{pedido.id_pedido_pk:04d}', tipo='pedido').update(leida=True)
        messages.success(request, f'Domicilio #{id_domicilio} marcado como entregado con éxito.')
    return redirect('detalle_domicilio', id_domicilio=id_domicilio)



# ── Historial de Facturas (Admin) ────────────────────────────────

def tabla_facturas_todas(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    facturas = Factura.objects.filter(id_pedido_factu_fk__estado_pedido='entregado').select_related('id_pedido_factu_fk', 'id_clien_factu_fk').prefetch_related('id_pedido_factu_fk__pago_set__id_met_pago_fk').order_by('-fecha_factu', '-hora_factu')
    return render(request, 'admin/factura/tabla-facturas.html', {'facturas': facturas})

def tabla_facturas_domicilio(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    
    facturas_qs = Factura.objects.filter(
        id_pedido_factu_fk__tipo_pedido='domicilio',
        id_pedido_factu_fk__estado_pedido='entregado'
    ).select_related(
        'id_pedido_factu_fk', 'id_clien_factu_fk'
    ).prefetch_related(
        'id_pedido_factu_fk__pago_set__id_met_pago_fk'
    ).order_by('-fecha_factu', '-hora_factu')

    facturas_unicas = []
    pedidos_vistos = set()
    for f in facturas_qs:
        if f.id_pedido_factu_fk_id not in pedidos_vistos:
            facturas_unicas.append(f)
            pedidos_vistos.add(f.id_pedido_factu_fk_id)

    return render(request, 'admin/factura/tabla-factura-domicilio.html', {'facturas': facturas_unicas})



def detalle_factura_domicilio(request, id_factura):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    factura = get_object_or_404(
        Factura.objects.select_related('id_pedido_factu_fk', 'id_clien_factu_fk').prefetch_related(
            'id_pedido_factu_fk__detalles_set__id_menu_fk', 
            'id_pedido_factu_fk__domicilios_set__id_barrio_domi_fk', 
            'id_pedido_factu_fk__pago_set__id_met_pago_fk'
        ), 
        id_factu_pk=id_factura
    )
    return render(request, 'admin/factura/detalle-factura-domicilio.html', {
        'factura': factura, 
        'pago': factura.pago_set.first() or factura.id_pedido_factu_fk.pago_set.first(), 
        'pedido': factura.id_pedido_factu_fk, 
        'domicilio': factura.id_pedido_factu_fk.domicilios_set.first(), 
        'cliente': factura.id_clien_factu_fk
    })



import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY

def iniciar_pago_stripe(request, pedido_id):
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    try:
        _, cliente = _get_cliente(request)
        pedido = Pedido.objects.get(id_pedido_pk=pedido_id, id_clien_pedido_fk=cliente)
    except Exception:
        messages.error(request, 'Pedido no encontrado.')
        return redirect('mis_pedidos')

    if pedido.estado_pedido not in ('pendiente',):
        messages.warning(request, 'El pedido no puede ser pagado.')
        return redirect('mis_pedidos')

    try:
        from dotenv import load_dotenv
        import os
        load_dotenv(override=True)
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY') or settings.STRIPE_SECRET_KEY
        
        host = request.scheme + '://' + request.get_host()
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'cop',
                    'product_data': {
                        'name': f'Pedido #PED-{pedido.id_pedido_pk:04d} - La Paella Real',
                    },
                    'unit_amount': int(pedido.total_pedido * 100),  # Stripe usa centavos
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=host + reverse('pago_exito') + f'?stripe_success=true&pedido_id={pedido.id_pedido_pk}',
            cancel_url=host + reverse('mis_pedidos'),
            client_reference_id=str(pedido.id_pedido_pk)
        )
        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(request, f'Error contactando a Stripe: {str(e)}')
        return redirect('mis_pedidos')

def cambiar_estado_pedido_detalle(request, id_pedido):
    rol = request.session.get('rol')
    if rol not in ['admin', 'empleado']:
        return redirect('login')
        
    if rol == 'empleado':
        from core.models import ConfiguracionSistema
        permite_empleados, _ = ConfiguracionSistema.objects.get_or_create(clave='permite_empleados_cambiar_estado', defaults={'valor_booleano': False})
        if not permite_empleados.valor_booleano:
            messages.error(request, 'No tienes permiso para cambiar el estado de los pedidos. Solicita autorización al administrador.')
            next_url = request.POST.get('next')
            if next_url: return redirect(next_url)
            return redirect('pedidos_empleado')

    if request.method != 'POST':
        return redirect('pedidos_admin')
    
    pedido = get_object_or_404(Pedido, id_pedido_pk=id_pedido)
    nuevo_estado = request.POST.get('estado_pedido')
    notas = request.POST.get('notas_pedido')
    next_url = request.POST.get('next')
    estado_anterior = pedido.estado_pedido

    # Validar transiciones unidireccionales
    transiciones_validas = {
        'pendiente': ['confirmado', 'cancelado'],
        'confirmado': ['preparando', 'cancelado'],
        'preparando': ['listo'],
        'listo': ['entregado'],
        'entregado': [],
        'cancelado': []
    }

    if nuevo_estado not in transiciones_validas.get(estado_anterior, []):
        messages.error(request, f'Transición no válida de {estado_anterior} a {nuevo_estado}.')
        # Redirigir al detalle correcto
        if next_url: return redirect(next_url)
        return redirect('pedidos_admin')

    # Validaciones especiales para cancelación
    if nuevo_estado == 'cancelado':
        pago = pedido.pago_set.first()
        # Si el pago está completado, requerimos nota de 20 caracteres
        if pago and pago.estado_pago == 'completado':
            if not notas or len(notas.strip()) < 20:
                messages.error(request, 'Al cancelar un pedido con pago verificado, la nota debe tener al menos 20 caracteres explicando el motivo/devolución.')
                if next_url: return redirect(next_url)
                domi = pedido.domicilios_set.first()
                if domi: return redirect('detalle_domicilio', id_domicilio=domi.id_domi_pk)
                return redirect('pedidos_admin')

    # Actualizar estado
    pedido.estado_pedido = nuevo_estado
    if notas is not None:
        pedido.notas_pedido = notas
    pedido.save()
    
    # Descontar stock al iniciar preparación
    if nuevo_estado == 'preparando' and estado_anterior != 'preparando':
        _descontar_stock_pedido(pedido)
    
    # Confirmar pago automáticamente al iniciar preparación
    if nuevo_estado in ['preparando', 'listo', 'entregado']:
        pago = pedido.pago_set.first()
        if pago and pago.estado_pago == 'pendiente':
            pago.estado_pago = 'completado'
            pago.save()

    if nuevo_estado == 'entregado':
        # Generar factura y asociar pago
        _generar_factura_si_entregado(pedido)

    # Sincronizar estado con domicilio
    for dom in pedido.domicilios_set.all():
        if nuevo_estado == 'pendiente' or nuevo_estado == 'confirmado' or nuevo_estado == 'preparando':
            pass # Se queda igual
        elif nuevo_estado == 'listo':
            dom.estado_domi = 'en camino'
        elif nuevo_estado == 'entregado':
            dom.estado_domi = 'entregado'
        elif nuevo_estado == 'cancelado':
            dom.estado_domi = 'cancelado'
        dom.save()

    # Registrar en el Historial
    from core.models import HistorialEstadoPedido
    usuario_auth = None
    if request.session.get('usuario_id'):
        usuario_auth = get_object_or_404(UsuarioAuth, id_auth_pk=request.session['usuario_id'])
    
    HistorialEstadoPedido.objects.create(
        id_pedido_fk=pedido,
        estado_anterior=estado_anterior,
        estado_nuevo=nuevo_estado,
        id_auth_fk=usuario_auth,
        notas=notas
    )

    # Notificación al cliente
    cliente = pedido.id_clien_pedido_fk
    if cliente and cliente.id_auth_fk:
        estados_msg = {
            'confirmado': f'Tu pedido #PED-{pedido.id_pedido_pk:04d} fue confirmado. Pronto comenzaremos a prepararlo',
            'preparando': f'¡Tu pedido #PED-{pedido.id_pedido_pk:04d} está siendo preparado!',
            'listo': f'Tu pedido #PED-{pedido.id_pedido_pk:04d} está listo y en camino',
            'entregado': f'Tu pedido #PED-{pedido.id_pedido_pk:04d} fue entregado. ¡Buen provecho!',
            'cancelado': f'Tu pedido #PED-{pedido.id_pedido_pk:04d} fue cancelado. Motivo: {notas or "No especificado"}',
        }
        msg = estados_msg.get(nuevo_estado)
        if msg:
            _crear_notificacion(
                tipo='pedido' if nuevo_estado != 'cancelado' else 'cancelacion',
                titulo=f'Actualización Pedido #PED-{pedido.id_pedido_pk:04d}',
                mensaje=msg,
                destinatario_rol='cliente',
                id_auth_destino=cliente.id_auth_fk,
                pedido=pedido,
            )

    messages.success(request, f'Estado del pedido actualizado a "{nuevo_estado}".')

    # Redirigir al detalle correcto
    if next_url:
        return redirect(next_url)
    domi = pedido.domicilios_set.first()
    if domi:
        return redirect('detalle_domicilio', id_domicilio=domi.id_domi_pk)
    return redirect('pedidos_admin')


def aprobar_solicitud_cancelacion(request, id_pedido):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id_pedido_pk=id_pedido)
        estado_anterior = pedido.estado_pedido
        pedido.estado_pedido = 'cancelado'
        pedido.solicitud_cancelacion_pendiente = False
        pedido.notas_pedido = pedido.motivo_solicitud_cancelacion or 'Cancelado por administrador (Solicitado por cliente)'
        pedido.save()

        # Sincronizar
        for dom in pedido.domicilios_set.all():
            dom.estado_domi = 'cancelado'
            dom.save()

        # Historial
        from core.models import HistorialEstadoPedido
        usuario_auth = get_object_or_404(UsuarioAuth, id_auth_pk=request.session['usuario_id'])
        HistorialEstadoPedido.objects.create(
            id_pedido_fk=pedido,
            estado_anterior=estado_anterior,
            estado_nuevo='cancelado',
            id_auth_fk=usuario_auth,
            notas=pedido.notas_pedido
        )

        # Notificar al cliente
        cliente = pedido.id_clien_pedido_fk
        if cliente and cliente.id_auth_fk:
            _crear_notificacion(
                tipo='cancelacion',
                titulo=f'Solicitud Aprobada - Pedido #PED-{pedido.id_pedido_pk:04d} Cancelado',
                mensaje=f'Tu solicitud de cancelación para el pedido #PED-{pedido.id_pedido_pk:04d} ha sido aprobada.',
                destinatario_rol='cliente',
                id_auth_destino=cliente.id_auth_fk,
                pedido=pedido,
            )
        
        messages.success(request, f'Solicitud aprobada. El pedido #PED-{pedido.id_pedido_pk:04d} fue cancelado.')

    next_url = request.POST.get('next')
    return redirect(next_url if next_url else 'pedidos_admin')


def rechazar_solicitud_cancelacion(request, id_pedido):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id_pedido_pk=id_pedido)
        pedido.solicitud_cancelacion_pendiente = False
        pedido.save()

        # Notificar al cliente
        cliente = pedido.id_clien_pedido_fk
        if cliente and cliente.id_auth_fk:
            _crear_notificacion(
                tipo='pedido',
                titulo=f'Solicitud Rechazada - Pedido #PED-{pedido.id_pedido_pk:04d}',
                mensaje=f'Tu solicitud de cancelación para el pedido #PED-{pedido.id_pedido_pk:04d} fue rechazada. El pedido continuará su curso.',
                destinatario_rol='cliente',
                id_auth_destino=cliente.id_auth_fk,
                pedido=pedido,
            )
        
        messages.info(request, f'Solicitud rechazada. El pedido #PED-{pedido.id_pedido_pk:04d} continuará normal.')

    next_url = request.POST.get('next')
    return redirect(next_url if next_url else 'pedidos_admin')



def obtener_barrios_por_localidad(request, id_localidad):
    barrios = Barrio.objects.filter(id_local_barrio_fk=id_localidad).values('id_barrio_pk', 'nom_barrio')
    return JsonResponse(list(barrios), safe=False)
