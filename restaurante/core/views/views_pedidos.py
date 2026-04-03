# views_pedidos.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from datetime import datetime as dt
from ..models import (
    UsuarioAuth, Cliente, Pedido, DetallePedidoMenu,
    Barrio, TipoEvento, MesaEvento, Domicilio, Evento, Menu, TipoMenu,
    Empleado, Factura, MetodoPago, Pago,
)


def _get_cliente(request):
    usuario = UsuarioAuth.objects.get(id_auth_pk=request.session['usuario_id'])
    cliente = Cliente.objects.get(id_auth_fk=usuario)
    return usuario, cliente


def _ctx_cliente(cliente):
    return {'usuario_nombre': cliente.nom_clien, 'usuario_email': cliente.correo_clien}


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
    return render(request, 'usuarios/index-carta.html', {
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
            total_pedido       = 0,
            notas_pedido       = request.POST.get('notas_pedido', '').strip() or None,
            id_clien_pedido_fk = cliente,
        )

        error = _crear_subpedido(request, pedido, tipo_pedido)
        if error:
            pedido.delete()
            messages.error(request, error)
            return render(request, 'usuarios/index-pedido.html', ctx_base)

        request.session['pedido_activo_id'] = pedido.id_pedido_pk
        messages.success(request, '¡Pedido iniciado! Ahora selecciona los menús.')
        return redirect('carrito_compra')

    return render(request, 'usuarios/index-pedido.html', ctx_base)


def _crear_subpedido(request, pedido, tipo):
    if tipo == 'domicilio':
        direc  = request.POST.get('direc_domi', '').strip()
        barrio = request.POST.get('id_barrio_domi_fk')
        fecha  = request.POST.get('fecha_domi')
        hora   = request.POST.get('hora_entrega_domi')
        if not all([direc, barrio, fecha, hora]):
            return 'Completa todos los campos del domicilio.'
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
    pedido_id = request.session.get('pedido_activo_id')
    if not pedido_id:
        messages.error(request, 'No tienes un pedido activo.')
        return redirect('crear_pedido')
    try:
        _, cliente = _get_cliente(request)
    except Exception:
        return redirect('login')

    pedido = get_object_or_404(Pedido, id_pedido_pk=pedido_id, id_clien_pedido_fk=cliente)
    if pedido.estado_pedido != 'pendiente':
        messages.warning(request, 'Este pedido ya fue procesado.')
        return redirect('mis_pedidos')

    return render(request, 'usuarios/carrito-compra.html', {
        **_ctx_cliente(cliente),
        'pedido': pedido,
        'tipos':  TipoMenu.objects.prefetch_related('menu_set').order_by('id_tipo_menu_pk'),
    })


def guardar_carrito(request):
    if request.method != 'POST':
        return redirect('inicio_usuarios')
    if not request.session.get('usuario_id'):
        return redirect('login')

    pedido_id = request.POST.get('pedido_id') or request.session.get('pedido_activo_id')
    if not pedido_id:
        messages.error(request, 'Pedido no encontrado.')
        return redirect('crear_pedido')

    try:
        _, cliente = _get_cliente(request)
        pedido = Pedido.objects.get(id_pedido_pk=pedido_id, id_clien_pedido_fk=cliente)
    except Exception:
        messages.error(request, 'Error al procesar el pedido.')
        return redirect('crear_pedido')

    num_items = int(request.POST.get('num_items', 0))
    if num_items == 0:
        messages.error(request, 'Debes agregar al menos un menú al carrito.')
        return redirect('carrito_compra')

    DetallePedidoMenu.objects.filter(id_pedido_fk=pedido).delete()
    total = Decimal('0.00')

    for i in range(num_items):
        menu_id  = request.POST.get(f'menu_id_{i}')
        cantidad = request.POST.get(f'cantidad_{i}')
        precio   = request.POST.get(f'precio_{i}')
        if not all([menu_id, cantidad, precio]):
            continue
        try:
            menu     = get_object_or_404(Menu, id_menu_pk=menu_id, disponible_menu=True)
            cantidad = int(cantidad)
            precio_u = Decimal(precio)
            subtotal = precio_u * cantidad
            DetallePedidoMenu.objects.create(
                id_pedido_fk    = pedido,
                id_menu_fk      = menu,
                cant_detalle    = cantidad,
                precio_unitario = precio_u,
                subtotal        = subtotal,
            )
            total += subtotal
        except Exception:
            continue

    pedido.total_pedido = total
    pedido.save()
    messages.success(request, '¡Menús seleccionados! Completa el pago para confirmar.')
    return redirect(f'/usuario/pago/?pedido_id={pedido.id_pedido_pk}')


def cancelar_pedido(request):
    usuario_id = request.session.get('usuario_id')
    pedido_id  = request.session.get('pedido_activo_id')

    if pedido_id and usuario_id:
        try:
            _, cliente = _get_cliente(request)
            pedido = Pedido.objects.get(id_pedido_pk=pedido_id, id_clien_pedido_fk=cliente)
            for evento in pedido.eventos_set.all():
                evento.id_mesa_evento_fk.estado_mesa = 'disponible'
                evento.id_mesa_evento_fk.save()
            pedido.delete()
        except Exception:
            pass

    request.session.pop('pedido_activo_id', None)
    messages.info(request, 'Pedido cancelado.')
    return redirect('crear_pedido')


def cancelar_pedido_usuario(request, id_pedido):
    """Cancela un pedido desde la página Mis Pedidos (solo si está pendiente)."""
    if not request.session.get('usuario_id'):
        return redirect('login')
    if request.method != 'POST':
        return redirect('mis_pedidos')
    try:
        _, cliente = _get_cliente(request)
        pedido = get_object_or_404(Pedido, id_pedido_pk=id_pedido, id_clien_pedido_fk=cliente)
        if pedido.estado_pedido not in ('pendiente',):
            messages.error(request, 'Solo puedes cancelar pedidos en estado pendiente.')
            return redirect('mis_pedidos')
        # Liberar mesa si era evento
        for evento in pedido.eventos_set.all():
            evento.id_mesa_evento_fk.estado_mesa = 'disponible'
            evento.id_mesa_evento_fk.save()
        pedido.estado_pedido = 'cancelado'
        pedido.save()
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
        
        from ..models import Notificacion
        Notificacion.objects.filter(titulo=f'Nuevo pedido #{pedido.id_pedido_pk}', tipo='pedido').update(leida=True)
        
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

        messages.success(request, f'Pedido #{id_pedido} marcado como completado. ¡Gracias por confirmar!')
    except Exception as e:
        messages.error(request, f'No se pudo actualizar el pedido: {e}')
    return redirect('mis_pedidos')


# ── Stock AJAX ────────────────────────────────────────────

def verificar_stock_menu(request, menu_id):
    from django.http import JsonResponse
    from ..models import RecetaMenu
    try:
        qty = int(request.GET.get('qty', 1))
        menu    = get_object_or_404(Menu, id_menu_pk=menu_id, disponible_menu=True)
        recetas = RecetaMenu.objects.select_related(
            'id_produ_fk', 'id_uni_medi_fk'
        ).filter(id_menu_fk=menu)

        if not recetas.exists():
            return JsonResponse({
                'disponible': True, 'tiene_receta': False,
                'advertencia': False, 'ingredientes_bajos': [],
                'mensaje': 'Menú disponible.',
            })

        bajos = []
        for receta in recetas:
            prod  = receta.id_produ_fk
            stock = prod.stock_actual_produ  # en kg o base
            # La receta está en gramos → convertir a kg para comparar exactamente
            requerido_kg = round((receta.cantidad_reque / Decimal('1000')) * qty, 3)

            if stock < requerido_kg:
                bajos.append({
                    'ingrediente':  prod.nom_produ,
                    'stock_actual': float(stock),
                    'requerido':    float(requerido_kg),
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
        
        from ..models import Notificacion
        Notificacion.objects.create(
            tipo='inventario',
            titulo=f'Falta stock para: {menu}',
            mensaje=f'Cliente intentó pedir {menu}. {motivo}'
        )

        return JsonResponse({'ok': True, 'mensaje': '¡Notificación enviada al administrador!'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ── Pedidos admin ─────────────────────────────────────────

def pedidos_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')

    pedidos = Pedido.objects.select_related(
        'id_clien_pedido_fk', 'id_emple_pedido_fk',
    ).prefetch_related(
        'domicilios_set__id_barrio_domi_fk',
        'eventos_set__id_tipo_evento_fk',
    ).all().order_by('-fecha_pedido')

    return render(request, 'admin/pedido/pedido.html', {
        'pedidos':        pedidos,
        'empleados':      Empleado.objects.filter(estado_emple='activo').order_by('nom_emple'),
        'estados_pedido': Pedido.ESTADOS,
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
                from ..models import Notificacion
                Notificacion.objects.filter(titulo=f'Nuevo pedido #{pedido.id_pedido_pk}', tipo='pedido').update(leida=True)
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
            metodo  = get_object_or_404(MetodoPago, id_met_pago_pk=metodo_id)
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

            from ..models import Notificacion
            Notificacion.objects.create(
                tipo='pedido',
                titulo=f'Nuevo pedido #{pedido.id_pedido_pk}',
                mensaje=f'El cliente {cliente.nom_clien} ha realizado un nuevo pedido ({pedido.tipo_pedido}).'
            )

            # ── Descontar stock de ingredientes (g → kg) ──
            from ..models import RecetaMenu
            for detalle in pedido.detalles_set.select_related('id_menu_fk').all():
                menu     = detalle.id_menu_fk
                cantidad = detalle.cant_detalle  # porciones pedidas
                recetas  = RecetaMenu.objects.select_related(
                    'id_produ_fk'
                ).filter(id_menu_fk=menu)
                for receta in recetas:
                    prod          = receta.id_produ_fk
                    # receta.cantidad_reque está en gramos, stock_actual_produ está (o debe estar) en KG
                    consumo_kg    = round((receta.cantidad_reque / Decimal('1000')) * cantidad, 3)
                    prod.stock_actual_produ = max(Decimal('0'), round(prod.stock_actual_produ - consumo_kg, 3))
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
    if not usuario_id or not factura_id:
        return redirect('mis_pedidos')

    try:
        _, cliente = _get_cliente(request)
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
    domicilios = Domicilio.objects.select_related(
        'id_pedido_domi_fk__id_clien_pedido_fk',
        'id_barrio_domi_fk',
    ).order_by('-id_domi_pk')
    return render(request, 'admin/pedido/tabla-domicilio.html', {
        'domicilios': domicilios,
    })


def tabla_eventos_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    eventos = Evento.objects.select_related(
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
    return render(request, 'admin/pedido/detalle-domicilio.html', {
        'domicilio': domicilio,
        'pedido':    pedido,
        'factura':   factura,
        'pago':      pago,
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
        from ..models import Notificacion
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
    return render(request, 'admin/pedido/detalle-evento.html', {
        'evento':  evento,
        'pedido':  pedido,
        'factura': factura,
        'pago':    pago,
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
        from ..models import Notificacion
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
