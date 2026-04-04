# views_personas.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date, datetime
from ..models import Empleado, Cliente, Proveedor

FECHA_MAX = {'fecha_max': date.today().strftime('%Y-%m-%d')}


def _fecha_max_17():
    """Devuelve la fecha máxima de nacimiento para que el cliente tenga al menos 17 años."""
    hoy = date.today()
    try:
        return hoy.replace(year=hoy.year - 17).strftime('%Y-%m-%d')
    except ValueError:  # 29 feb en años no bisiestos
        return hoy.replace(year=hoy.year - 17, month=2, day=28).strftime('%Y-%m-%d')


def _calcular_edad(fecha_str):
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    hoy = date.today()
    return hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))


# ── Dashboards ────────────────────────────────────────────

def dashboard_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
        
    from datetime import date, timedelta
    from django.db.models import Sum
    from ..models import Pedido, Factura, Evento, DetallePedidoMenu
    from decimal import Decimal

    hoy = date.today()
    manana = hoy + timedelta(days=1)

    # Pedidos Activos
    pedidos_activos = Pedido.objects.filter(estado_pedido__in=['pendiente', 'preparando', 'listo'])
    total_pedidos_activos = pedidos_activos.count()
    pedidos_cocina = pedidos_activos.filter(estado_pedido='preparando').count()
    pedidos_listos = pedidos_activos.filter(estado_pedido='listo').count()

    # Ventas del Día
    ventas_hoy = Factura.objects.filter(fecha_factu=hoy).aggregate(Sum('total_factu'))['total_factu__sum'] or Decimal('0.0')
    
    # Reservas Especiales
    reservas_hoy = Evento.objects.filter(fecha_evento=hoy).count()
    reservas_manana = Evento.objects.filter(fecha_evento=manana).count()

    # Cancelaciones
    cancelaciones_hoy = Pedido.objects.filter(estado_pedido='cancelado', fecha_pedido__date=hoy).count()

    # Pedidos Entregados
    pedidos_entregados_hoy = Pedido.objects.filter(estado_pedido='entregado', fecha_pedido__date=hoy).count()

    # Platos Más Vendidos Hoy
    platos_qs = DetallePedidoMenu.objects.filter(
        id_pedido_fk__fecha_pedido__date=hoy
    ).values(
        'id_menu_fk__nom_menu'
    ).annotate(
        total_vendido=Sum('cant_detalle')
    ).order_by('-total_vendido')[:3]
    
    max_ventas = platos_qs[0]['total_vendido'] if platos_qs else 1
    platos_populares = []
    for p in platos_qs:
        r = p.copy()
        r['porcentaje'] = int((r['total_vendido'] / max_ventas) * 100) if max_ventas else 0
        platos_populares.append(r)

    return render(request, 'admin/dashboard-admin.html', {
        'total_pedidos_activos': total_pedidos_activos,
        'pedidos_cocina': pedidos_cocina,
        'pedidos_listos': pedidos_listos,
        'ventas_hoy': ventas_hoy,
        'reservas_hoy': reservas_hoy,
        'reservas_manana': reservas_manana,
        'cancelaciones_hoy': cancelaciones_hoy,
        'pedidos_entregados_hoy': pedidos_entregados_hoy,
        'platos_populares': platos_populares,
        'max_ventas': max_ventas,
    })

def dashboard_empleado(request):
    return render(request, 'empleado/dashboard-empleado.html')

def inicio_usuarios(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    from ..models import UsuarioAuth
    try:
        usuario = UsuarioAuth.objects.get(id_auth_pk=usuario_id)
        if not usuario.activo:
            request.session.flush()
            messages.error(request, 'Su sesión ha caducado o su cuenta fue desactivada.')
            return redirect('login')
        cliente = Cliente.objects.get(id_auth_fk=usuario)
    except (UsuarioAuth.DoesNotExist, Cliente.DoesNotExist):
        return redirect('login')

    if request.method == 'POST' and request.POST.get('action') == 'cambiar_pw_provisional':
        nueva_pass = request.POST.get('nueva_password')
        conf_pass = request.POST.get('conf_password')
        if nueva_pass and nueva_pass == conf_pass:
            usuario.set_password(nueva_pass)
            usuario.save()
            request.session.pop('cambio_pw_pendiente', None)
            messages.success(request, 'Contraseña actualizada correctamente. ¡Bienvenido!')
            return redirect('inicio_usuarios')
        else:
            messages.error(request, 'Las contraseñas no coinciden o son inválidas.')

    return render(request, 'usuarios/inicio-usuarios.html', {
        'usuario_nombre': cliente.nom_clien,
        'usuario_email':  cliente.correo_clien,
    })

def mi_perfil(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    from ..models import UsuarioAuth
    try:
        usuario = UsuarioAuth.objects.get(id_auth_pk=usuario_id)
        if not usuario.activo:
            request.session.flush()
            messages.error(request, 'Su sesión ha caducado o su cuenta fue desactivada.')
            return redirect('login')
        cliente = Cliente.objects.get(id_auth_fk=usuario)
    except (UsuarioAuth.DoesNotExist, Cliente.DoesNotExist):
        return redirect('login')

    if request.method == 'POST':
        cliente.nom_clien          = request.POST.get('nombres', '').strip()
        cliente.apellido_clien     = request.POST.get('apellidos', '').strip()
        cliente.fecha_naci_cliente = request.POST.get('fecha_nacimiento', '')
        cliente.tel_cliente        = request.POST.get('telefono', '').strip()
        cliente.direc_clien        = request.POST.get('direccion', '').strip()
        cliente.save()
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('mi_perfil')

    from ..models import Pedido
    pedidos_count = Pedido.objects.filter(id_clien_pedido_fk=cliente, tipo_pedido='domicilio').exclude(estado_pedido='cancelado').count()
    reservas_count = Pedido.objects.filter(id_clien_pedido_fk=cliente, tipo_pedido='evento').exclude(estado_pedido='cancelado').count()
    favoritos_count = 0

    return render(request, 'usuarios/mi-perfil.html', {
        'cliente': cliente,
        'pedidos_count': pedidos_count,
        'reservas_count': reservas_count,
        'favoritos_count': favoritos_count
    })

def personas_admin(request):
    return render(request, 'admin/personas/personas.html')

def inventario_admin(request):
    return render(request, 'admin/inventario/inventario.html')

def historial_ventas(request):
    from django.db.models import Sum
    from datetime import date
    from ..models import Factura
    from decimal import Decimal
    
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
        
    hoy = date.today()
    
    facturas_hoy = Factura.objects.filter(fecha_factu=hoy)
    total_hoy = facturas_hoy.aggregate(Sum('total_factu'))['total_factu__sum'] or Decimal('0.0')
    
    facturas_mes = Factura.objects.filter(fecha_factu__year=hoy.year, fecha_factu__month=hoy.month)
    total_mes = facturas_mes.aggregate(Sum('total_factu'))['total_factu__sum'] or Decimal('0.0')
    
    facturas_domi_hoy = facturas_hoy.filter(id_pedido_factu_fk__tipo_pedido='domicilio')
    total_domi_hoy = facturas_domi_hoy.aggregate(Sum('total_factu'))['total_factu__sum'] or Decimal('0.0')
    
    facturas_eventos_hoy = facturas_hoy.filter(id_pedido_factu_fk__tipo_pedido='evento')
    total_eventos_hoy = facturas_eventos_hoy.aggregate(Sum('total_factu'))['total_factu__sum'] or Decimal('0.0')
    
    return render(request, 'admin/factura/factura.html', {
        'count_hoy': facturas_hoy.count(),
        'count_mes': facturas_mes.count(),
        'total_hoy': total_hoy,
        'total_mes': total_mes,
        'count_domi_hoy': facturas_domi_hoy.count(),
        'total_domi_hoy': total_domi_hoy,
        'count_eventos_hoy': facturas_eventos_hoy.count(),
        'total_eventos_hoy': total_eventos_hoy,
    })


# ── Empleados ─────────────────────────────────────────────

def crear_empleado(request):
    if request.method == 'POST':
        Empleado.objects.create(
            nom_emple        = request.POST['nom_empleado'],
            apellido_emple   = request.POST['apellido_empleado'],
            fecha_naci_emple = request.POST['fecha_naci_empleado'],
            tel_emple        = request.POST['tel_empleado'],
            correo_emple     = request.POST['correo_empleado'],
            direc_emple      = request.POST['direc_empleado'],
            estado_emple     = 'activo',
        )
        messages.success(request, 'Empleado registrado correctamente')
        return redirect('tabla_empleados')
    return render(request, 'admin/personas/index-empleado.html', FECHA_MAX)

def tabla_empleados(request):
    return render(request, 'admin/personas/tabla-empleado.html', {
        'empleados': Empleado.objects.all().order_by('nom_emple')
    })

def editar_empleado(request, id):
    empleado = get_object_or_404(Empleado, id_emple_pk=id)
    if request.method == 'POST':
        for campo in ('nom_emple', 'apellido_emple', 'fecha_naci_emple',
                      'tel_emple', 'correo_emple', 'direc_emple'):
            setattr(empleado, campo, request.POST[campo])
        empleado.save()
        messages.success(request, 'Empleado actualizado correctamente')
    return redirect('tabla_empleados')

def cambiar_estado_empleado(request, id):
    empleado = get_object_or_404(Empleado, id_emple_pk=id)
    empleado.estado_emple = 'inactivo' if empleado.estado_emple == 'activo' else 'activo'
    empleado.save()
    return redirect('tabla_empleados')

def eliminar_empleado(request, id):
    empleado = get_object_or_404(Empleado, id_emple_pk=id)
    if request.method == 'POST':
        empleado.delete()
        messages.success(request, 'Empleado eliminado correctamente')
    return redirect('tabla_empleados')


# ── Clientes ──────────────────────────────────────────────

def crear_cliente(request):
    fecha_max_17 = _fecha_max_17()
    ctx = {'fecha_max': fecha_max_17}
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha_naci_cliente', '')
        if fecha_str and _calcular_edad(fecha_str) < 17:
            messages.error(request, 'El cliente debe tener al menos 17 años.')
            return render(request, 'admin/personas/index-cliente.html', ctx)
        
        try:
            from ..models import UsuarioAuth, Rol
            import random, string

            if UsuarioAuth.objects.filter(nombre_usuario=request.POST['correo_clien']).exists():
                messages.error(request, 'Ya existe un usuario con este correo.')
                return render(request, 'admin/personas/index-cliente.html', ctx)

            # Generar contraseña provisional
            caracteres = string.ascii_letters + string.digits
            rand_code = ''.join(random.choices(caracteres, k=6))
            temp_pass = f"Prov-{rand_code}"

            rol_cliente = Rol.objects.get(name='cliente')
            usuario = UsuarioAuth(nombre_usuario=request.POST['correo_clien'], rol=rol_cliente, activo=True)
            usuario.set_password(temp_pass)
            usuario.save()

            Cliente.objects.create(
                nom_clien          = request.POST['nom_clien'],
                apellido_clien     = request.POST['apellido_clien'],
                fecha_naci_cliente = fecha_str,
                tel_cliente        = request.POST['tel_cliente'],
                correo_clien       = request.POST['correo_clien'],
                direc_clien        = request.POST['direc_clien'],
                estado_clien       = 'activo',
                id_auth_fk         = usuario
            )
            messages.success(request, f'Cliente registrado correctamente. Su contraseña provisional es: {temp_pass}')
            return redirect('tabla_clientes')
        except Exception as e:
            messages.error(request, f'Error al crear el cliente: {str(e)}')
            return render(request, 'admin/personas/index-cliente.html', ctx)
            
    return render(request, 'admin/personas/index-cliente.html', ctx)

def tabla_clientes(request):
    return render(request, 'admin/personas/tabla-cliente.html', {
        'clientes': Cliente.objects.all().order_by('id_clien_pk')
    })

def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id_clien_pk=id)
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha_naci_cliente', '')
        if fecha_str and _calcular_edad(fecha_str) < 17:
            messages.error(request, 'El cliente debe tener al menos 17 años.')
            return redirect('tabla_clientes')
        cliente.nom_clien          = request.POST['nom_clien']
        cliente.apellido_clien     = request.POST['apellido_clien']
        cliente.fecha_naci_cliente = fecha_str
        cliente.tel_cliente        = request.POST['tel_cliente']
        cliente.correo_clien       = request.POST['correo_clien']
        cliente.direc_clien        = request.POST['direc_clien']
        cliente.save()
        messages.success(request, 'Cliente actualizado correctamente')
    return redirect('tabla_clientes')

def cambiar_estado_cliente(request, id):
    cliente = get_object_or_404(Cliente, id_clien_pk=id)
    cliente.estado_clien = 'inactivo' if cliente.estado_clien == 'activo' else 'activo'
    cliente.save()
    # Sincronizar el acceso al login: si está inactivo, no puede iniciar sesión
    if cliente.id_auth_fk:
        cliente.id_auth_fk.activo = (cliente.estado_clien == 'activo')
        cliente.id_auth_fk.save()
    return redirect('tabla_clientes')

def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id_clien_pk=id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado correctamente')
    return redirect('tabla_clientes')


# ── Proveedores ───────────────────────────────────────────

def crear_proveedor(request):
    if request.method == 'POST':
        Proveedor.objects.create(
            nom_provee        = request.POST['nom_provee'],
            apellido_provee   = request.POST.get('apellido_provee', ''),
            fecha_naci_provee = request.POST['fecha_naci_provee'],
            tel_provee        = request.POST['tel_provee'],
            correo_provee     = request.POST['correo_provee'],
            direc_provee      = request.POST['direc_provee'],
            estado_provee     = 'activo',
        )
        messages.success(request, 'Proveedor registrado correctamente')
        return redirect('tabla_proveedores')
    return render(request, 'admin/inventario/index-proveedor.html', FECHA_MAX)

def tabla_proveedores(request):
    return render(request, 'admin/inventario/tabla-proveedor.html', {
        'proveedores': Proveedor.objects.all().order_by('id_provee_pk')
    })

def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id_provee_pk=id)
    if request.method == 'POST':
        proveedor.nom_provee        = request.POST['nom_provee']
        proveedor.apellido_provee   = request.POST.get('apellido_provee', '')
        proveedor.fecha_naci_provee = request.POST['fecha_naci_provee']
        proveedor.tel_provee        = request.POST['tel_provee']
        proveedor.correo_provee     = request.POST['correo_provee']
        proveedor.direc_provee      = request.POST['direc_provee']
        proveedor.save()
        messages.success(request, 'Proveedor actualizado correctamente')
    return redirect('tabla_proveedores')

def cambiar_estado_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id_provee_pk=id)
    proveedor.estado_provee = 'inactivo' if proveedor.estado_provee == 'activo' else 'activo'
    proveedor.save()
    return redirect('tabla_proveedores')


# ── Perfil Admin ──────────────────────────────────────────

def editar_perfil_admin(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id or request.session.get('rol') != 'admin':
        return redirect('login')
        
    from ..models import UsuarioAuth, Empleado
    try:
        usuario = UsuarioAuth.objects.get(id_auth_pk=usuario_id)
    except UsuarioAuth.DoesNotExist:
        return redirect('login')

    try:
        empleado = Empleado.objects.get(id_auth_fk=usuario)
    except Empleado.DoesNotExist:
        import datetime
        empleado = Empleado.objects.create(
            nom_emple="Administrador",
            apellido_emple="Sistema",
            fecha_naci_emple=datetime.date(1990, 1, 1),
            tel_emple=0,
            correo_emple=usuario.nombre_usuario,
            direc_emple="N/A",
            estado_emple='activo',
            id_auth_fk=usuario
        )

    if request.method == 'POST':
        empleado.nom_emple = request.POST.get('nombres', empleado.nom_emple)
        empleado.apellido_emple = request.POST.get('apellidos', empleado.apellido_emple)
        empleado.tel_emple = request.POST.get('telefono', empleado.tel_emple)
        empleado.correo_emple = request.POST.get('correo', empleado.correo_emple)
        
        # Si se quiere cambiar la contraseña
        nueva_pass = request.POST.get('nueva_password')
        conf_pass = request.POST.get('conf_password')
        if nueva_pass and nueva_pass == conf_pass:
            usuario.set_password(nueva_pass)
            usuario.save()

        empleado.save()
        
        request.session['usuario'] = f"{empleado.nom_emple} {empleado.apellido_emple}"
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('dashboard_admin')
    
    return render(request, 'admin/edit-perfil-admin.html', {'empleado': empleado})