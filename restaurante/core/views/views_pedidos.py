# views_pedidos.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from datetime import datetime as dt
from core.models import (
    UsuarioAuth, Cliente, Pedido, DetallePedidoMenu,
    Barrio, TipoEvento, MesaEvento, Domicilio, Evento, Menu, TipoMenu,
    Empleado, Factura, MetodoPago, Pago, Notificacion,
)


def _crear_notificacion(tipo, titulo, mensaje, destinatario_rol,
                        id_auth_destino=None, id_auth_origen=None,
                        pedido=None, evento=None, factura=None,
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
        id_evento_fk=evento,
        id_factura_fk=factura,
        id_producto_fk=producto,
        id_movi_fk=movimiento,
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
    
    FACTORES_CONVERSION = {
        ('g', 'kg'):  Decimal('0.001'),
        ('kg', 'kg'): Decimal('1'),
        ('g', 'g'):   Decimal('1'),
        ('kg', 'g'):  Decimal('1000'),
        ('ml', 'l'):  Decimal('0.001'),
        ('l', 'l'):   Decimal('1'),
        ('ml', 'ml'): Decimal('1'),
        ('l', 'ml'):  Decimal('1000'),
    }
    
    problemas = []
    
    for item in carrito_items:
        menu = Menu.objects.get(id_menu_pk=item['menu_id'])
        cantidad = item['cantidad']
        
        # Obtener todas las recetas del menú
        recetas = RecetaMenu.objects.select_related(
            'id_produ_fk', 'id_uni_medi_fk',
            'id_produ_fk__id_uni_medi_produ_fk'
        ).filter(id_menu_fk=menu)
        
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
            uni_receta = receta.id_uni_medi_fk.abreviatura.strip().lower()
            uni_stock  = prod.id_uni_medi_produ_fk.abreviatura.strip().lower()
            factor = FACTORES_CONVERSION.get((uni_receta, uni_stock))
            if factor is None:
                factor = Decimal('1') if uni_receta == uni_stock else Decimal('0.001')
            
            stock_actual = prod.stock_actual_produ
            requerido = round(receta.cantidad_reque * factor * cantidad, 3)
            
            if stock_actual < requerido:
                problemas.append({
                    'ingrediente': prod.nom_produ,
                    'menu': menu.nom_menu,
                    'razon': 'stock_insuficiente',
                    'stock_actual': float(stock_actual),
                    'requerido': float(requerido),
                    'unidad': prod.id_uni_medi_produ_fk.abreviatura,
                })
    
    if problemas:
        msg = 'No se puede procesar el pedido: '
        razon_principal = problemas[0]['razon']
        if razon_principal == 'inactivo':
            msg += f'El ingrediente "{problemas[0]["ingrediente"]}" no está disponible'
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
    tipos = TipoMenu.objects.prefetch_related('menu_set').all().order_by('id_tipo_menu_pk')
    return render(request, 'usuarios/carta.html', {
        **_ctx_cliente(cliente), 'tipos': tipos,
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
        'barrios':       Barrio.objects.select_related('id_local_barrio_fk').order_by('nom_barrio'),
        'tipos_eventos': TipoEvento.objects.all().order_by('nom_tipo_evento'),
        'mesas':         MesaEvento.objects.filter(estado_mesa='disponible').order_by('num_mesa'),
    }

    if request.method == 'POST':
        tipo_pedido = request.POST.get('tipo_pedido')
        if not tipo_pedido:
            messages.error(request, 'Debes seleccionar el tipo de pedido.')
            return render(request, 'usuarios/index-pedido.html', ctx_base)

        pedido = Pedido.objects.create(
            tipo_pedido        = tipo_pedido,
            estado_pedido      = 'pendiente',
            total_pedido       = Decimal(request.session.get('total_temporal', '0')),
            notas_pedido       = request.POST.get('notas_pedido', '').strip() or None,
            id_clien_pedido_fk = cliente,
        )

        error = _crear_subpedido(request, pedido, tipo_pedido)
        if error:
            pedido.delete()
            messages.error(request, error)
            return render(request, 'usuarios/index-pedido.html', ctx_base)

        for item in carrito_temp:
            menu = get_object_or_404(Menu, id_menu_pk=item['menu_id'])
            DetallePedidoMenu.objects.create(
                id_pedido_fk    = pedido,
                id_menu_fk      = menu,
                cant_detalle    = item['cantidad'],
                precio_unitario = Decimal(item['precio_u']),
                subtotal        = Decimal(item['subtotal']),
            )

        request.session.pop('carrito_temporal', None)
        request.session.pop('total_temporal', None)

        messages.success(request, '¡Información guardada! Procede al pago para confirmar.')
        return redirect(f'/usuario/pago/?pedido_id={pedido.id_pedido_pk}')

    return render(request, 'usuarios/index-pedido.html', ctx_base)


def _crear_subpedido(request, pedido, tipo):
    from datetime import datetime, timedelta
    now = datetime.now()

    if tipo == 'domicilio':
        if now.hour >= 20:
            return 'No se pueden realizar pedidos después de las 8:00 PM.'

        direc  = request.POST.get('direc_domi', '').strip()
        barrio = request.POST.get('id_barrio_domi_fk')
        fecha  = request.POST.get('fecha_domi')
        hora   = request.POST.get('hora_entrega_domi')
        if not all([direc, barrio, fecha, hora]):
            return 'Completa todos los campos del domicilio.'
            
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            if fecha_obj < now.date():
                return 'La fecha de entrega no puede ser en el pasado.'
        except ValueError:
            return 'Fecha inválida.'

        try:
            hora_obj = datetime.strptime(hora, '%H:%M').time()
            if hora_obj.hour >= 20:
                return 'La hora de entrega no puede ser después de las 8:00 PM.'
        except ValueError:
            return 'Hora inválida.'

        Domicilio.objects.create(
            direc_domi        = direc,
            fecha_domi        = fecha,
            hora_entrega_domi = hora,
            estado_domi       = 'pendiente',
            id_pedido_domi_fk = pedido,
            id_barrio_domi_fk = get_object_or_404(Barrio, id_barrio_pk=barrio),
        )

    elif tipo == 'evento':
        campos = [
            request.POST.get('nom_evento', '').strip(),
            request.POST.get('fecha_evento'),
            request.POST.get('hora_inicio_evento'),
            request.POST.get('hora_fin_evento'),
            request.POST.get('ubi_evento', '').strip(),
            request.POST.get('cant_invi_evento'),
            request.POST.get('id_tipo_evento_fk'),
            request.POST.get('id_mesa_evento_fk'),
        ]
        if not all(campos):
            return 'Completa todos los campos del evento.'
            
        try:
            fecha_obj = datetime.strptime(campos[1], '%Y-%m-%d').date()
            if fecha_obj < (now.date() + timedelta(days=7)):
                return 'Los eventos deben reservarse con al menos una semana de anticipación.'
        except ValueError:
            return 'Fecha de evento inválida.'

        try:
            hora_inicio = datetime.strptime(campos[2], '%H:%M').time()
            hora_fin = datetime.strptime(campos[3], '%H:%M').time()
            if hora_inicio.hour < 8 or hora_fin.hour > 23 or (hora_fin.hour == 23 and hora_fin.minute > 0):
                return 'El horario del evento debe estar entre las 8:00 AM y las 11:00 PM.'
        except ValueError:
            return 'Hora de evento inválida.'

        try:
            cant = int(campos[5])
            if cant <= 0 or cant > 500:
                return 'La cantidad de invitados debe ser un número entre 1 y 500.'
        except ValueError:
            return 'La cantidad de invitados debe ser un número válido.'

        mesa = get_object_or_404(MesaEvento, id_mesa_pk=campos[7])
        Evento.objects.create(
            nom_evento         = campos[0],
            fecha_evento       = campos[1],
            hora_inicio_evento = campos[2],
            hora_fin_evento    = campos[3],
            ubi_evento         = campos[4],
            cant_invi_evento   = campos[5],
            estado_evento      = 'pendiente',
            id_tipo_evento_fk  = get_object_or_404(TipoEvento, id_tipo_evento_pk=campos[6]),
            id_mesa_evento_fk  = mesa,
            id_pedido_evento_fk = pedido,
        )
        mesa.estado_mesa = 'reservada'
        mesa.save()
    return None


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
        'eventos_set__id_tipo_evento_fk',
        'eventos_set__id_mesa_evento_fk',
        'factura_set',
    ).order_by('-fecha_pedido')

    return render(request, 'usuarios/mis-pedidos.html', {
        **_ctx_cliente(cliente), 'pedidos': pedidos,
    })


# ── Carrito ───────────────────────────────────────────────

def carrito_compra(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
        
    try:
        _, cliente = _get_cliente(request)
    except Exception:
        return redirect('login')

    carrito_temp = request.session.get('carrito_temporal')
    
    return render(request, 'usuarios/carrito-compra.html', {
        **_ctx_cliente(cliente),
        'carrito_temp': carrito_temp,
        'tipos':  TipoMenu.objects.prefetch_related('menu_set').order_by('id_tipo_menu_pk'),
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
            
            _crear_notificacion(
                tipo='cancelacion',
                titulo=f'⚠️ Solicitud de cancelación Pedido #{id_pedido}',
                mensaje=f'El cliente {cliente.nom_clien} solicita cancelar el pedido #{id_pedido} (lleva >30m confirmado). Motivo: {motivo}',
                destinatario_rol='admin',
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

        # Liberar mesa si era evento
        for evento in pedido.eventos_set.all():
            evento.estado_evento = 'cancelado'
            evento.id_mesa_evento_fk.estado_mesa = 'disponible'
            evento.id_mesa_evento_fk.save()
            evento.save()
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
            titulo=f'❌ {cliente.nom_clien} canceló el pedido #{id_pedido}',
            mensaje=f'❌ {cliente.nom_clien} canceló el pedido #{id_pedido}. Motivo: {motivo}',
            destinatario_rol='admin',
            id_auth_origen=usuario_auth,
            pedido=pedido,
        )
        _crear_notificacion(
            tipo='cancelacion',
            titulo=f'❌ Tu pedido #{id_pedido} fue cancelado',
            mensaje=f'❌ Tu pedido #{id_pedido} ha sido cancelado exitosamente.',
            destinatario_rol='cliente',
            id_auth_destino=usuario_auth,
            pedido=pedido,
        )

        messages.success(request, f'Pedido #{id_pedido} cancelado correctamente.')
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
        
        Notificacion.objects.filter(titulo__contains=f'pedido #{pedido.id_pedido_pk}', tipo='pedido').update(leida=True)
        
        # Si es domicilio, marcarlo como entregado
        for domi in pedido.domicilios_set.all():
            domi.estado_domi = 'entregado'
            domi.save()
            
        # Si es evento, marcarlo como finalizado y liberar mesa
        for evento in pedido.eventos_set.all():
            evento.estado_evento = 'finalizado'
            evento.save()
            evento.id_mesa_evento_fk.estado_mesa = 'disponible'
            evento.id_mesa_evento_fk.save()

        # ── Notificaciones de entrega confirmada ──
        usuario_auth = UsuarioAuth.objects.get(id_auth_pk=request.session['usuario_id'])
        _crear_notificacion(
            tipo='pedido',
            titulo=f'🎉 Pedido #{id_pedido} fue entregado. ¡Buen provecho!',
            mensaje=f'🎉 Tu pedido #{id_pedido} fue entregado. ¡Buen provecho!',
            destinatario_rol='cliente',
            id_auth_destino=usuario_auth,
            pedido=pedido,
        )
        _crear_notificacion(
            tipo='pedido',
            titulo=f'🍽️ Pedido #{id_pedido} marcado como entregado',
            mensaje=f'🍽️ Pedido #{id_pedido} marcado como entregado por el cliente {cliente.nom_clien}',
            destinatario_rol='admin',
            id_auth_origen=usuario_auth,
            pedido=pedido,
        )

        messages.success(request, f'Pedido #{id_pedido} marcado como completado. ¡Gracias por confirmar!')
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

        FACTORES_CONVERSION = {
            ('g', 'kg'):  Decimal('0.001'),
            ('kg', 'kg'): Decimal('1'),
            ('g', 'g'):   Decimal('1'),
            ('kg', 'g'):  Decimal('1000'),
            ('ml', 'l'):  Decimal('0.001'),
            ('l', 'l'):   Decimal('1'),
            ('ml', 'ml'): Decimal('1'),
            ('l', 'ml'):  Decimal('1000'),
        }

        bajos = []
        for receta in recetas:
            prod  = receta.id_produ_fk
            stock = prod.stock_actual_produ
            uni_receta = receta.id_uni_medi_fk.abreviatura.strip().lower()
            uni_stock  = prod.id_uni_medi_produ_fk.abreviatura.strip().lower()
            factor = FACTORES_CONVERSION.get((uni_receta, uni_stock))
            if factor is None:
                factor = Decimal('1') if uni_receta == uni_stock else Decimal('0.001')
            requerido = round(receta.cantidad_reque * factor * qty, 3)

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
        usuario_id = request.session.get('usuario_id', 'anónimo')

        logger = logging.getLogger('django')
        logger.warning(
            f'[STOCK] Cliente {usuario_id} no pudo pedir "{menu}". Motivo: {motivo}'
        )
        
        from core.models import Notificacion
        Notificacion.objects.create(
            tipo='inventario',
            titulo=f'Falta stock para: {menu}',
            mensaje=f'Cliente intentó pedir {menu}. {motivo}'
        )

        return JsonResponse({'ok': True, 'mensaje': '¡Notificación enviada al administrador!'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ── Pedidos admin ─────────────────────────────────────────

from django.utils import timezone
from datetime import timedelta

def pedidos_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')

    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())

    pedidos = Pedido.objects.filter(factura__isnull=False).select_related(
        'id_clien_pedido_fk', 'id_emple_pedido_fk',
    ).prefetch_related(
        'domicilios_set__id_barrio_domi_fk',
        'eventos_set__id_tipo_evento_fk',
    ).all().order_by('-fecha_pedido')

    domicilios_hoy = Domicilio.objects.filter(fecha_domi=hoy, id_pedido_domi_fk__factura__isnull=False).count()
    domicilios_semana = Domicilio.objects.filter(fecha_domi__gte=inicio_semana, id_pedido_domi_fk__factura__isnull=False).count()
    eventos_hoy = Evento.objects.filter(fecha_evento=hoy, id_pedido_evento_fk__factura__isnull=False).count()
    eventos_semana = Evento.objects.filter(fecha_evento__gte=inicio_semana, id_pedido_evento_fk__factura__isnull=False).count()

    return render(request, 'admin/pedido/pedido.html', {
        'pedidos':        pedidos,
        'empleados':      Empleado.objects.filter(estado_emple='activo').order_by('nom_emple'),
        'estados_pedido': Pedido.ESTADOS,
        'domicilios_hoy': domicilios_hoy,
        'domicilios_semana': domicilios_semana,
        'eventos_hoy': eventos_hoy,
        'eventos_semana': eventos_semana,
    })


def cambiar_estado_pedido(request, id_pedido):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    if request.method == 'POST':
        pedido       = get_object_or_404(Pedido, id_pedido_pk=id_pedido)
        nuevo_estado = request.POST.get('estado_pedido')
        if nuevo_estado in [v for v, _ in Pedido.ESTADOS]:
            pedido.estado_pedido = nuevo_estado
            pedido.save()
            if nuevo_estado == 'entregado':
                Notificacion.objects.filter(titulo__contains=f'pedido #{pedido.id_pedido_pk}', tipo='pedido').update(leida=True)

            # ── Notificación al cliente sobre cambio de estado ──
            cliente = pedido.id_clien_pedido_fk
            if cliente and cliente.id_auth_fk:
                estados_msg = {
                    'confirmado': f'✅ Tu pedido #{pedido.id_pedido_pk} fue confirmado y está siendo preparado',
                    'en_preparacion': f'👨‍🍳 Tu pedido #{pedido.id_pedido_pk} está siendo preparado',
                    'en_camino': f'🛵 Tu pedido #{pedido.id_pedido_pk} ya está en camino',
                    'entregado': f'🎉 Tu pedido #{pedido.id_pedido_pk} fue entregado. ¡Buen provecho!',
                    'cancelado': f'❌ Tu pedido #{pedido.id_pedido_pk} fue cancelado por el administrador',
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
            'eventos_set__id_tipo_evento_fk',
            'eventos_set__id_mesa_evento_fk',
            'detalles_set__id_menu_fk',
        ),
        id_pedido_pk=id_pedido
    )
    return render(request, 'admin/pedido/detalle-pedido.html', {'pedido': pedido})


# ── Pago ──────────────────────────────────────────────────

def pago_pedido(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    pedido_id = request.GET.get('pedido_id') or request.POST.get('pedido_id')
    if not pedido_id:
        messages.error(request, 'No se encontró el pedido a pagar.')
        return redirect('mis_pedidos')

    try:
        _, cliente = _get_cliente(request)
        pedido = Pedido.objects.prefetch_related(
            'detalles_set__id_menu_fk',
            'domicilios_set__id_barrio_domi_fk',
            'eventos_set__id_tipo_evento_fk',
        ).get(id_pedido_pk=pedido_id, id_clien_pedido_fk=cliente)
    except Exception:
        messages.error(request, 'Pedido no encontrado.')
        return redirect('mis_pedidos')

    if pedido.estado_pedido not in ('pendiente', 'confirmado'):
        messages.warning(request, 'Este pedido ya fue procesado o cancelado.')
        return redirect('mis_pedidos')

    if request.method == 'POST':
        metodo_id  = request.POST.get('id_met_pago_fk')
        referencia = request.POST.get('referencia_pago', '').strip()

        if not metodo_id:
            messages.error(request, 'Selecciona un método de pago.')
            return redirect(f'/usuario/pago/?pedido_id={pedido_id}')

        try:
            metodo  = get_object_or_404(MetodoPago, tipo_met_pago=metodo_id)
            ahora   = dt.now()
            factura = Factura.objects.create(
                fecha_factu        = ahora.date(),
                hora_factu         = ahora.time(),
                total_factu        = pedido.total_pedido,
                id_clien_factu_fk  = cliente,
                id_pedido_factu_fk = pedido,
            )

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
                id_factu_pago_fk = factura,
                celular_origen   = celular or None,
                nombre_titular   = titular or None,
                comprobante_img  = comprobante,
                monto_con_el_que_paga = monto_efectivo
            )
            
            # El usuario pidió explícitamente: "cuando yo le de a realizar pago aqui aparezca pendiente".
            # pedido.estado_pedido = 'confirmado' 
            pedido.estado_pedido = 'pendiente'
            pedido.save()
            request.session.pop('pedido_activo_id', None)

            # ── Notificaciones de pedido confirmado y pago ──
            usuario_auth = UsuarioAuth.objects.get(id_auth_pk=request.session['usuario_id'])
            
            notas_extra = f" | Notas: {pedido.notas_pedido}" if pedido.notas_pedido else ""
            mensaje_admin = f'📦 Nuevo pedido #{pedido.id_pedido_pk} de {cliente.nom_clien} por ${pedido.total_pedido:,.0f}{notas_extra}'
            
            _crear_notificacion(
                tipo='pedido',
                titulo=f'📦 Nuevo pedido #{pedido.id_pedido_pk} de {cliente.nom_clien}',
                mensaje=mensaje_admin,
                destinatario_rol='admin',
                id_auth_origen=usuario_auth,
                pedido=pedido,
            )
            
            _crear_notificacion(
                tipo='pedido',
                titulo=f'📦 Nuevo pedido #{pedido.id_pedido_pk} de {cliente.nom_clien}',
                mensaje=mensaje_admin,
                destinatario_rol='empleado',
                id_auth_origen=usuario_auth,
                pedido=pedido,
            )

            # Notificación de Factura para cliente
            _crear_notificacion(
                tipo='pago',
                titulo=f'🧾 Factura #{factura.id_factu_pk} generada',
                mensaje=f'✅ Tu pedido #{pedido.id_pedido_pk} está confirmado. Tu factura #{factura.id_factu_pk} está disponible por un total de: ${pedido.total_pedido:,.0f}',
                destinatario_rol='cliente',
                id_auth_destino=usuario_auth,
                pedido=pedido,
                factura=factura,
            )

            if pedido.tipo_pedido == 'evento':
                ev = pedido.eventos_set.first()
                if ev:
                    _crear_notificacion(
                        tipo='evento',
                        titulo=f'🎉 Solicitud de evento de {cliente.nom_clien}',
                        mensaje=f'🎉 Solicitud de evento de {cliente.nom_clien} para {ev.fecha_evento} — {ev.cant_invi_evento} personas',
                        destinatario_rol='admin',
                        id_auth_origen=usuario_auth,
                        pedido=pedido,
                        evento=ev,
                    )
                    _crear_notificacion(
                        tipo='evento',
                        titulo=f'🎉 Solicitud de evento de {cliente.nom_clien}',
                        mensaje=f'🎉 Solicitud de evento de {cliente.nom_clien} para {ev.fecha_evento} — {ev.cant_invi_evento} personas',
                        destinatario_rol='empleado',
                        id_auth_origen=usuario_auth,
                        pedido=pedido,
                        evento=ev,
                    )

            # ── Descontar stock de ingredientes (conversión por unidad) ──
            from core.models import RecetaMenu
            # Tabla de factores: (unidad_receta, unidad_stock) → factor
            # consumo_en_stock = cantidad_reque * factor * porciones
            FACTORES_CONVERSION = {
                ('g', 'kg'):  Decimal('0.001'),
                ('kg', 'kg'): Decimal('1'),
                ('g', 'g'):   Decimal('1'),
                ('kg', 'g'):  Decimal('1000'),
                ('ml', 'l'):  Decimal('0.001'),
                ('l', 'l'):   Decimal('1'),
                ('ml', 'ml'): Decimal('1'),
                ('l', 'ml'):  Decimal('1000'),
            }
            for detalle in pedido.detalles_set.select_related('id_menu_fk').all():
                menu     = detalle.id_menu_fk
                cantidad = detalle.cant_detalle  # porciones pedidas
                recetas  = RecetaMenu.objects.select_related(
                    'id_produ_fk', 'id_uni_medi_fk',
                    'id_produ_fk__id_uni_medi_produ_fk'
                ).filter(id_menu_fk=menu)
                for receta in recetas:
                    prod = receta.id_produ_fk
                    uni_receta = receta.id_uni_medi_fk.abreviatura.strip().lower()
                    uni_stock  = prod.id_uni_medi_produ_fk.abreviatura.strip().lower()
                    factor = FACTORES_CONVERSION.get((uni_receta, uni_stock))
                    if factor is None:
                        # Si las unidades son iguales o no hay factor, asumir 1:1
                        factor = Decimal('1') if uni_receta == uni_stock else Decimal('0.001')
                    consumo = round(receta.cantidad_reque * factor * cantidad, 3)
                    prod.stock_actual_produ = max(Decimal('0'), round(prod.stock_actual_produ - consumo, 3))
                    prod.save()

            messages.success(request, f'¡Pago registrado! Factura #{factura.id_factu_pk}')
            return redirect(f'/usuario/pago/exito/?factura_id={factura.id_factu_pk}')
        except Exception as e:
            messages.error(request, f'Error al procesar el pago: {e}')
            return redirect(f'/usuario/pago/?pedido_id={pedido_id}')

    return render(request, 'usuarios/index-pago-factura.html', {
        **_ctx_cliente(cliente),
        'pedido':   pedido,
        'detalles': pedido.detalles_set.all(),
    })


def pago_exito(request):
    usuario_id = request.session.get('usuario_id')
    factura_id = request.GET.get('factura_id')
    stripe_success = request.GET.get('stripe_success')
    pedido_id = request.GET.get('pedido_id')
    
    if not usuario_id:
        return redirect('mis_pedidos')

    try:
        _, cliente = _get_cliente(request)

        # Procesar pago sincrono si viene redireccionado desde Stripe
        if stripe_success == 'true' and pedido_id:
            pedido = Pedido.objects.get(id_pedido_pk=pedido_id, id_clien_pedido_fk=cliente)
            if pedido.estado_pedido != 'confirmado':
                metodo, _ = MetodoPago.objects.get_or_create(tipo_met_pago='stripe')
                ahora = dt.now()
                factura = Factura.objects.create(
                    fecha_factu = ahora.date(),
                    hora_factu = ahora.time(),
                    total_factu = pedido.total_pedido,
                    id_clien_factu_fk = cliente,
                    id_pedido_factu_fk = pedido
                )
                Pago.objects.create(
                    fecha_pago = ahora.date(),
                    hora_pago = ahora.time(),
                    monto_pago = pedido.total_pedido,
                    estado_pago = 'completado',
                    id_met_pago_fk = metodo,
                    id_factu_pago_fk = factura
                )
                pedido.estado_pedido = 'confirmado'
                pedido.save()
            else:
                factura = pedido.factura_set.first()
            
            factura_id = factura.id_factu_pk if factura else None

        if not factura_id:
            return redirect('mis_pedidos')

        factura = Factura.objects.select_related(
            'id_pedido_factu_fk',
        ).prefetch_related(
            'id_pedido_factu_fk__detalles_set__id_menu_fk',
            'id_pedido_factu_fk__domicilios_set__id_barrio_domi_fk',
            'id_pedido_factu_fk__eventos_set__id_tipo_evento_fk',
            'pagos_set__id_met_pago_fk',
        ).get(id_factu_pk=factura_id, id_clien_factu_fk=cliente)
    except Exception:
        return redirect('mis_pedidos')

    pedido   = factura.id_pedido_factu_fk
    detalles = pedido.detalles_set.all()
    pago     = factura.pagos_set.first()

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
    cliente  = factura.id_clien_factu_fk
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
        <p>Pedido N°: <span>#{pedido.id_pedido_pk}</span></p>
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
        <p>Pedido N°: <span>#{pedido.id_pedido_pk}</span></p>
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
    domicilios = Domicilio.objects.filter(
        id_pedido_domi_fk__factura__isnull=False
    ).select_related(
        'id_pedido_domi_fk__id_clien_pedido_fk',
        'id_barrio_domi_fk',
    ).order_by('-id_domi_pk')
    return render(request, 'admin/pedido/tabla-domicilio.html', {
        'domicilios': domicilios,
    })


def tabla_eventos_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    eventos = Evento.objects.filter(
        id_pedido_evento_fk__factura__isnull=False
    ).select_related(
        'id_pedido_evento_fk__id_clien_pedido_fk',
        'id_tipo_evento_fk',
        'id_mesa_evento_fk',
    ).order_by('-id_evento_pk')
    return render(request, 'admin/pedido/tabla-evento.html', {
        'eventos': eventos,
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
    pago     = factura.pago_set.first() if factura else None
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
        from core.models import Notificacion
        Notificacion.objects.filter(titulo=f'Nuevo pedido #{pedido.id_pedido_pk}', tipo='pedido').update(leida=True)
        messages.success(request, f'Domicilio #{id_domicilio} marcado como entregado con éxito.')
    return redirect('detalle_domicilio', id_domicilio=id_domicilio)


def detalle_evento_admin(request, id_evento):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    evento = get_object_or_404(
        Evento.objects.select_related(
            'id_pedido_evento_fk__id_clien_pedido_fk',
            'id_pedido_evento_fk__id_emple_pedido_fk',
            'id_tipo_evento_fk',
            'id_mesa_evento_fk',
        ).prefetch_related(
            'id_pedido_evento_fk__detalles_set__id_menu_fk',
            'id_pedido_evento_fk__factura_set__pago_set__id_met_pago_fk',
        ),
        id_evento_pk=id_evento
    )
    pedido  = evento.id_pedido_evento_fk
    factura = pedido.factura_set.first()
    pago    = factura.pago_set.first() if factura else None
    from core.models import HistorialEstadoPedido
    historial = HistorialEstadoPedido.objects.filter(id_pedido_fk=pedido).select_related('id_auth_fk').order_by('fecha_cambio')
    empleados = Empleado.objects.filter(estado_emple='activo')
    return render(request, 'admin/pedido/detalle-evento.html', {
        'evento':  evento,
        'pedido':  pedido,
        'factura': factura,
        'pago':    pago,
        'historial': historial,
        'empleados': empleados,
    })


def marcar_evento_finalizado_admin(request, id_evento):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    if request.method == 'POST':
        evento = get_object_or_404(Evento, id_evento_pk=id_evento)
        pedido = evento.id_pedido_evento_fk
        
        if pedido.estado_pedido == 'cancelado':
            messages.error(request, 'No puedes finalizar un evento cuyo pedido fue cancelado.')
            return redirect('detalle_evento_admin', id_evento=id_evento)

        evento.estado_evento = 'finalizado'
        evento.save()
        
        # Liberar la mesa
        evento.id_mesa_evento_fk.estado_mesa = 'disponible'
        evento.id_mesa_evento_fk.save()
        
        pedido = evento.id_pedido_evento_fk
        pedido.estado_pedido = 'entregado'
        pedido.save()
        from core.models import Notificacion
        Notificacion.objects.filter(titulo=f'Nuevo pedido #{pedido.id_pedido_pk}', tipo='pedido').update(leida=True)
        messages.success(request, f'Evento #{id_evento} marcado como finalizado con éxito.')
    return redirect('detalle_evento_admin', id_evento=id_evento)
# ── Historial de Facturas (Admin) ────────────────────────────────

def tabla_facturas_todas(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    facturas = Factura.objects.select_related('id_pedido_factu_fk', 'id_clien_factu_fk').prefetch_related('pago_set__id_met_pago_fk').order_by('-fecha_factu', '-hora_factu')
    return render(request, 'admin/factura/tabla-facturas.html', {'facturas': facturas})

def tabla_facturas_domicilio(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    facturas = Factura.objects.filter(id_pedido_factu_fk__tipo_pedido='domicilio').select_related('id_pedido_factu_fk', 'id_clien_factu_fk').prefetch_related('pago_set__id_met_pago_fk').order_by('-fecha_factu', '-hora_factu')
    return render(request, 'admin/factura/tabla-factura-domicilio.html', {'facturas': facturas})

def tabla_facturas_evento(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    facturas = Factura.objects.filter(id_pedido_factu_fk__tipo_pedido='evento').select_related('id_pedido_factu_fk', 'id_clien_factu_fk').prefetch_related('pago_set__id_met_pago_fk').order_by('-fecha_factu', '-hora_factu')
    return render(request, 'admin/factura/tabla-factura-evento.html', {'facturas': facturas})

def detalle_factura_domicilio(request, id_factura):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    factura = get_object_or_404(Factura.objects.select_related('id_pedido_factu_fk', 'id_clien_factu_fk').prefetch_related('id_pedido_factu_fk__detalles_set__id_menu_fk', 'id_pedido_factu_fk__domicilios_set__id_barrio_domi_fk', 'pago_set__id_met_pago_fk'), id_factu_pk=id_factura)
    return render(request, 'admin/factura/detalle-factura-domicilio.html', {'factura': factura, 'pago': factura.pago_set.first(), 'pedido': factura.id_pedido_factu_fk, 'domicilio': factura.id_pedido_factu_fk.domicilios_set.first(), 'cliente': factura.id_clien_factu_fk})

def detalle_factura_evento(request, id_factura):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    factura = get_object_or_404(Factura.objects.select_related('id_pedido_factu_fk', 'id_clien_factu_fk').prefetch_related('id_pedido_factu_fk__detalles_set__id_menu_fk', 'id_pedido_factu_fk__eventos_set__id_tipo_evento_fk', 'id_pedido_factu_fk__eventos_set__id_mesa_evento_fk', 'pago_set__id_met_pago_fk'), id_factu_pk=id_factura)
    return render(request, 'admin/factura/detalle-factura-evento.html', {'factura': factura, 'pago': factura.pago_set.first(), 'pedido': factura.id_pedido_factu_fk, 'evento': factura.id_pedido_factu_fk.eventos_set.first(), 'cliente': factura.id_clien_factu_fk})

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
        host = request.scheme + '://' + request.get_host()
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'cop',
                    'product_data': {
                        'name': f'Pedido #{pedido.id_pedido_pk} - La Paella Real',
                    },
                    'unit_amount': int(pedido.total_pedido * 100),  # Stripe usa centavos
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=host + reverse('pago_exito') + f'?stripe_success=true&pedido_id={pedido.id_pedido_pk}',
            cancel_url=host + reverse('pago_pedido') + f'?pedido_id={pedido.id_pedido_pk}',
            client_reference_id=str(pedido.id_pedido_pk)
        )
        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(request, f'Error contactando a Stripe: {str(e)}')
        return redirect(f'/usuario/pago/?pedido_id={pedido_id}')

def cambiar_estado_pedido_detalle(request, id_pedido):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
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
        if pedido.tipo_pedido == 'domicilio':
            domi = pedido.domicilios_set.first()
            if domi: return redirect('detalle_domicilio', id_domicilio=domi.id_domi_pk)
        return redirect('pedidos_admin')

    # Validaciones especiales para cancelación
    if nuevo_estado == 'cancelado':
        factura = pedido.factura_set.first()
        pago = factura.pago_set.first() if factura else None
        # Si el pago está completado, requerimos nota de 20 caracteres
        if pago and pago.estado_pago == 'completado':
            if not notas or len(notas.strip()) < 20:
                messages.error(request, 'Al cancelar un pedido con pago verificado, la nota debe tener al menos 20 caracteres explicando el motivo/devolución.')
                if next_url: return redirect(next_url)
                if pedido.tipo_pedido == 'domicilio':
                    domi = pedido.domicilios_set.first()
                    if domi: return redirect('detalle_domicilio', id_domicilio=domi.id_domi_pk)
                return redirect('pedidos_admin')

    # Actualizar estado
    pedido.estado_pedido = nuevo_estado
    if notas is not None:
        pedido.notas_pedido = notas
    pedido.save()

    # Sincronizar estado con domicilio o evento
    if pedido.tipo_pedido == 'domicilio':
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
    else:
        for evt in pedido.eventos_set.all():
            if nuevo_estado == 'entregado':
                evt.estado_evento = 'finalizado'
                evt.id_mesa_evento_fk.estado_mesa = 'disponible'
                evt.id_mesa_evento_fk.save()
            elif nuevo_estado == 'cancelado':
                evt.estado_evento = 'cancelado'
                evt.id_mesa_evento_fk.estado_mesa = 'disponible'
                evt.id_mesa_evento_fk.save()
            elif nuevo_estado == 'preparando':
                evt.estado_evento = 'en progreso'
            elif nuevo_estado == 'confirmado':
                evt.estado_evento = 'aprobado'
            evt.save()

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
            'confirmado': f'Tu pedido #{pedido.id_pedido_pk} fue confirmado. Pronto comenzaremos a prepararlo',
            'preparando': f'¡Tu pedido #{pedido.id_pedido_pk} está siendo preparado!',
            'listo': f'Tu pedido #{pedido.id_pedido_pk} está listo y en camino',
            'entregado': f'Tu pedido #{pedido.id_pedido_pk} fue entregado. ¡Buen provecho!',
            'cancelado': f'Tu pedido #{pedido.id_pedido_pk} fue cancelado. Motivo: {notas or "No especificado"}',
        }
        msg = estados_msg.get(nuevo_estado)
        if msg:
            _crear_notificacion(
                tipo='pedido' if nuevo_estado != 'cancelado' else 'cancelacion',
                titulo=f'Actualización Pedido #{pedido.id_pedido_pk}',
                mensaje=msg,
                destinatario_rol='cliente',
                id_auth_destino=cliente.id_auth_fk,
                pedido=pedido,
            )

    messages.success(request, f'Estado del pedido actualizado a "{nuevo_estado}".')

    # Redirigir al detalle correcto
    if next_url:
        return redirect(next_url)
    if pedido.tipo_pedido == 'domicilio':
        domi = pedido.domicilios_set.first()
        if domi:
            return redirect('detalle_domicilio', id_domicilio=domi.id_domi_pk)
    else:
        evt = pedido.eventos_set.first()
        if evt:
            return redirect('detalle_evento_admin', id_evento=evt.id_evento_pk)
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
        if pedido.tipo_pedido == 'domicilio':
            for dom in pedido.domicilios_set.all():
                dom.estado_domi = 'cancelado'
                dom.save()
        else:
            for evt in pedido.eventos_set.all():
                evt.estado_evento = 'cancelado'
                evt.id_mesa_evento_fk.estado_mesa = 'disponible'
                evt.id_mesa_evento_fk.save()
                evt.save()

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
                titulo=f'Solicitud Aprobada - Pedido #{pedido.id_pedido_pk} Cancelado',
                mensaje=f'Tu solicitud de cancelación para el pedido #{pedido.id_pedido_pk} ha sido aprobada.',
                destinatario_rol='cliente',
                id_auth_destino=cliente.id_auth_fk,
                pedido=pedido,
            )
        
        messages.success(request, f'Solicitud aprobada. El pedido #{pedido.id_pedido_pk} fue cancelado.')

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
                titulo=f'Solicitud Rechazada - Pedido #{pedido.id_pedido_pk}',
                mensaje=f'Tu solicitud de cancelación para el pedido #{pedido.id_pedido_pk} fue rechazada. El pedido continuará su curso.',
                destinatario_rol='cliente',
                id_auth_destino=cliente.id_auth_fk,
                pedido=pedido,
            )
        
        messages.info(request, f'Solicitud rechazada. El pedido #{pedido.id_pedido_pk} continuará normal.')

    next_url = request.POST.get('next')
    return redirect(next_url if next_url else 'pedidos_admin')

