# views_personas.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date, datetime
from core.models import Empleado, Cliente, Proveedor, CategoriaProducto

FECHA_MAX = {'fecha_max': date.today().strftime('%Y-%m-%d')}


def _fecha_max_17():
    """Devuelve la fecha máxima de nacimiento para que el cliente tenga al menos 17 años."""
    hoy = date.today()
    try:
        return hoy.replace(year=hoy.year - 17).strftime('%Y-%m-%d')
    except ValueError:  # 29 feb en años no bisiestos
        return hoy.replace(year=hoy.year - 17, month=2, day=28).strftime('%Y-%m-%d')

def _fecha_max_18():
    """Devuelve la fecha máxima de nacimiento para que el individuo tenga al menos 18 años."""
    hoy = date.today()
    try:
        return hoy.replace(year=hoy.year - 18).strftime('%Y-%m-%d')
    except ValueError: 
        return hoy.replace(year=hoy.year - 18, month=2, day=28).strftime('%Y-%m-%d')


def _calcular_edad(fecha_str):
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    hoy = date.today()
    return hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))


def _check_duplicate_phone(phone, current_empleado_id=None, current_cliente_id=None, current_proveedor_id=None):
    if not phone: return False
    query_empleado = Empleado.objects.filter(tel_emple=phone)
    if current_empleado_id: query_empleado = query_empleado.exclude(id_emple_pk=current_empleado_id)
    if query_empleado.exists(): return True

    query_cliente = Cliente.objects.filter(tel_cliente=phone)
    if current_cliente_id: query_cliente = query_cliente.exclude(id_clien_pk=current_cliente_id)
    if query_cliente.exists(): return True

    query_proveedor = Proveedor.objects.filter(tel_provee=phone)
    if current_proveedor_id: query_proveedor = query_proveedor.exclude(id_provee_pk=current_proveedor_id)
    if query_proveedor.exists(): return True

    return False


def _check_duplicate_email(email, current_proveedor_id=None):
    if not email:
        return False
    query = Proveedor.objects.filter(correo_provee__iexact=email)
    if current_proveedor_id:
        query = query.exclude(id_provee_pk=current_proveedor_id)
    return query.exists()


def _fecha_opcional(value):
    valor = (value or '').strip()
    return valor or None


def _validar_telefono(phone):
    """
    Valida que el teléfono sea un string de 10 dígitos comenzando con 3.
    Retorna (es_válido, mensaje_error)
    """
    if not phone or not isinstance(phone, str):
        return False, "El teléfono es requerido."
    
    # Remover espacios
    phone = phone.strip()
    
    # Verificar que sea solo dígitos
    if not phone.isdigit():
        return False, "El teléfono solo debe contener dígitos."
    
    # Verificar longitud
    if len(phone) != 10:
        return False, "El teléfono debe tener exactamente 10 dígitos."
    
    # Verificar que comience con 3
    if not phone.startswith('3'):
        return False, "El teléfono debe comenzar con 3."
    
    return True, ""


# ── Dashboards ────────────────────────────────────────────

def dashboard_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
        
    from datetime import date, timedelta
    from django.db.models import Sum
    from core.models import Pedido, Factura, DetallePedidoMenu
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
        'cancelaciones_hoy': cancelaciones_hoy,
        'pedidos_entregados_hoy': pedidos_entregados_hoy,
        'platos_populares': platos_populares,
        'max_ventas': max_ventas,
    })



def inicio_usuarios(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    from core.models import UsuarioAuth
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
    from core.models import UsuarioAuth
    try:
        usuario = UsuarioAuth.objects.get(id_auth_pk=usuario_id)
        if not usuario.activo:
            request.session.flush()
            messages.error(request, 'Su sesión ha caducado o su cuenta fue desactivada.')
            return redirect('login')
        cliente = Cliente.objects.get(id_auth_fk=usuario)
    except (UsuarioAuth.DoesNotExist, Cliente.DoesNotExist):
        return redirect('login')

    if request.GET.get('reset_foto') == '1':
        if cliente.foto_cliente and cliente.foto_cliente != 'default.png':
            try:
                import os
                from django.core.files.storage import default_storage
                if default_storage.exists(cliente.foto_cliente):
                    default_storage.delete(cliente.foto_cliente)
            except Exception:
                pass
        cliente.foto_cliente = 'default.png'
        cliente.save()
        messages.success(request, 'Foto de perfil eliminada correctamente.')
        return redirect('mi_perfil')

    if request.method == 'POST':
        telefono = request.POST.get('telefono', '').strip()
        if _check_duplicate_phone(telefono, current_cliente_id=cliente.id_clien_pk):
            messages.error(request, 'El número de teléfono ya está registrado por otra persona.')
            return redirect('mi_perfil')

        nombre_usuario = request.POST.get('nombre_usuario', '').strip()
        if nombre_usuario:
            if UsuarioAuth.objects.filter(nombre_usuario=nombre_usuario).exclude(id_auth_pk=usuario.id_auth_pk).exists():
                messages.error(request, 'El nombre de usuario ya está registrado por otra persona.')
                return redirect('mi_perfil')
            usuario.nombre_usuario = nombre_usuario
            usuario.save()

        cliente.nom_clien          = request.POST.get('nombres', '').strip()
        cliente.apellido_clien     = request.POST.get('apellidos', '').strip()
        cliente.fecha_naci_cliente = request.POST.get('fecha_nacimiento', '')
        cliente.tel_cliente        = telefono
        cliente.direc_clien        = request.POST.get('direccion', '').strip()
        cliente.save()
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('mi_perfil')

    from core.models import Pedido
    pedidos_count = Pedido.objects.filter(id_clien_pedido_fk=cliente, tipo_pedido='domicilio').exclude(estado_pedido='cancelado').count()
    favoritos_count = 0

    return render(request, 'usuarios/mi-perfil.html', {
        'cliente': cliente,
        'pedidos_count': pedidos_count,
        'favoritos_count': favoritos_count
    })

def personas_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    from core.models import Empleado, Cliente
    total_empleados_activos = Empleado.objects.filter(estado_emple='activo').count()
    total_empleados = Empleado.objects.count()
    total_clientes = Cliente.objects.count()
    total_clientes_activos = Cliente.objects.filter(estado_clien='activo').count()
    
    return render(request, 'admin/personas/personas.html', {
        'total_empleados_activos': total_empleados_activos,
        'total_empleados': total_empleados,
        'total_clientes': total_clientes,
        'total_clientes_activos': total_clientes_activos,
    })

def inventario_admin(request):
    from core.models import Producto, Proveedor, MovimientoProducto
    from datetime import date, timedelta
    from django.db.models import Q, F

    total_productos = Producto.objects.count()
    bajo_stock = Producto.objects.filter(
        stock_actual_produ__lte=F('stock_minimo_produ')
    ).exclude(estado_produ='descontinuado').count()

    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    movimientos_mes = MovimientoProducto.objects.filter(fecha_movi__date__gte=inicio_mes).count()
    movimientos_hoy = MovimientoProducto.objects.filter(fecha_movi__date=hoy).count()

    proveedores_activos = Proveedor.objects.filter(estado_provee='activo').count()

    return render(request, 'admin/inventario/inventario.html', {
        'total_productos': total_productos,
        'bajo_stock': bajo_stock,
        'movimientos_mes': movimientos_mes,
        'movimientos_hoy': movimientos_hoy,
        'proveedores_activos': proveedores_activos,
    })

def historial_ventas(request):
    from django.db.models import Sum
    from datetime import date
    from core.models import Factura
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

    return render(request, 'admin/factura/factura.html', {
        'count_hoy': facturas_hoy.count(),
        'count_mes': facturas_mes.count(),
        'total_hoy': total_hoy,
        'total_mes': total_mes,
        'count_domi_hoy': facturas_domi_hoy.count(),
        'total_domi_hoy': total_domi_hoy,
    })


# ── Empleados ─────────────────────────────────────────────

from django.db import transaction

@transaction.atomic
def crear_empleado(request):
    if request.session.get("rol") != "admin":
        messages.error(request, "Acceso denegado. Permisos insuficientes.")
        return redirect("dashboard_admin")
    if request.method == 'POST':
        # Validar campos obligatorios básicos
        required_fields = ['nombre_usuario', 'password', 'nom_empleado', 'apellido_empleado', 'fecha_naci_empleado', 'tel_empleado', 'correo_empleado', 'direc_empleado', 'tipo_doc', 'num_doc', 'tipo_contrato', 'fecha_ingreso', 'salario_empleado']
        for field in required_fields:
            if not request.POST.get(field, '').strip():
                messages.error(request, 'Por favor, completa todos los campos obligatorios.')
                return render(request, 'admin/personas/index-empleado.html', {
                    'fecha_max': _fecha_max_18(),
                    'datos': request.POST
                })

        from core.models import UsuarioAuth, Rol
        nombre_usuario = request.POST.get('nombre_usuario', '').strip()
        password = request.POST.get('password', '')
        
        try:
            rol_empleado = Rol.objects.get(name='empleado')
        except Rol.DoesNotExist:
            messages.error(request, 'Error crítico: Rol empleado no existe.')
            return redirect('crear_empleado')

        if UsuarioAuth.objects.filter(nombre_usuario=nombre_usuario).exists():
            messages.error(request, 'El nombre de usuario ya está registrado.')
            return render(request, 'admin/personas/index-empleado.html', {
                'fecha_max': _fecha_max_18(),
                'datos': request.POST
            })
            
        if _check_duplicate_phone(request.POST.get('tel_empleado', '')):
            messages.error(request, 'El número de celular ya está registrado por otra persona.')
            return render(request, 'admin/personas/index-empleado.html', {
                'fecha_max': _fecha_max_18(),
                'datos': request.POST
            })

        correo = request.POST.get('correo_empleado', '').strip()
        from core.models import Empleado, Cliente
        if Empleado.objects.filter(correo_emple=correo).exists() or Cliente.objects.filter(correo_clien=correo).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return render(request, 'admin/personas/index-empleado.html', {
                'fecha_max': _fecha_max_18(),
                'datos': request.POST
            })

        num_doc = request.POST.get('num_doc', '').strip()
        if Empleado.objects.filter(num_doc=num_doc).exists():
            messages.error(request, 'El número de documento ya está registrado.')
            return render(request, 'admin/personas/index-empleado.html', {
                'fecha_max': _fecha_max_18(),
                'datos': request.POST
            })

        usuario_auth = UsuarioAuth(nombre_usuario=nombre_usuario, rol=rol_empleado, activo=True)
        usuario_auth.set_password(password)
        usuario_auth.save()

        TIPO_DOC_MAP = {
            'CC': 'Cédula de Ciudadanía',
            'CE': 'Cédula de Extranjería',
            'PP': 'Pasaporte',
            'TI': 'Tarjeta de Identidad'
        }
        TIPO_CONTRATO_MAP = {
            'indefinido': 'Término Indefinido',
            'fijo': 'Término Fijo',
            'obra': 'Obra o Labor',
            'aprendizaje': 'Contrato de Aprendizaje'
        }
        
        tipo_doc_db = TIPO_DOC_MAP.get(request.POST.get('tipo_doc'), '')
        tipo_contrato_db = TIPO_CONTRATO_MAP.get(request.POST.get('tipo_contrato'), '')

        Empleado.objects.create(
            nom_emple        = request.POST['nom_empleado'],
            apellido_emple   = request.POST['apellido_empleado'],
            fecha_naci_emple = request.POST['fecha_naci_empleado'],
            tel_emple        = request.POST['tel_empleado'],
            correo_emple     = request.POST['correo_empleado'],
            direc_emple      = request.POST['direc_empleado'],
            estado_emple     = 'activo',
            id_auth_fk       = usuario_auth,
            tipo_doc         = tipo_doc_db,
            num_doc          = request.POST.get('num_doc', '').strip(),
            fecha_ingreso    = request.POST.get('fecha_ingreso') or date.today().strftime('%Y-%m-%d'),
            tipo_contrato    = tipo_contrato_db,
            salario_empleado = request.POST.get('salario_empleado') or 0
        )
        messages.success(request, 'Empleado registrado correctamente')
        return redirect('tabla_empleados')
    return render(request, 'admin/personas/index-empleado.html', {'fecha_max': _fecha_max_18()})

def tabla_empleados(request):
    if request.session.get("rol") != "admin":
        messages.error(request, "Acceso denegado. Permisos insuficientes.")
        return redirect("dashboard_admin")
    return render(request, 'admin/personas/tabla-empleado.html', {
        'empleados': Empleado.objects.all().order_by('nom_emple')
    })

def editar_empleado(request, id):
    if request.session.get("rol") != "admin":
        messages.error(request, "Acceso denegado. Permisos insuficientes.")
        return redirect("dashboard_admin")
    empleado = get_object_or_404(Empleado, id_emple_pk=id)
    if request.method == 'POST':
        if _check_duplicate_phone(request.POST['tel_emple'], current_empleado_id=id):
            messages.error(request, 'El número de celular ya está registrado por otra persona.')
            return redirect('tabla_empleados')

        correo = request.POST.get('correo_emple', '').strip()
        from core.models import Cliente
        if Empleado.objects.exclude(id_emple_pk=id).filter(correo_emple=correo).exists() or Cliente.objects.filter(correo_clien=correo).exists():
            messages.error(request, 'El correo electrónico ya está registrado por otra persona.')
            return redirect('tabla_empleados')

        num_doc = request.POST.get('num_doc', '').strip()
        if Empleado.objects.exclude(id_emple_pk=id).filter(num_doc=num_doc).exists():
            messages.error(request, 'El número de documento ya está registrado.')
            return redirect('tabla_empleados')

        for campo in ('nom_emple', 'apellido_emple', 'fecha_naci_emple',
                      'tel_emple', 'correo_emple', 'direc_emple',
                      'tipo_doc', 'num_doc', 'tipo_contrato', 'fecha_ingreso', 'salario_empleado'):
            if campo in request.POST:
                setattr(empleado, campo, request.POST[campo])
        empleado.save()
        
        nombre_usuario = request.POST.get('nombre_usuario')
        if nombre_usuario and empleado.id_auth_fk:
            from core.models import UsuarioAuth
            if UsuarioAuth.objects.exclude(id_auth_pk=empleado.id_auth_fk.id_auth_pk).filter(nombre_usuario=nombre_usuario).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.')
                return redirect('tabla_empleados')
            empleado.id_auth_fk.nombre_usuario = nombre_usuario
            empleado.id_auth_fk.save()
            
        messages.success(request, 'Empleado actualizado correctamente')
    return redirect('tabla_empleados')

def cambiar_estado_empleado(request, id):
    if request.session.get("rol") != "admin":
        messages.error(request, "Acceso denegado. Permisos insuficientes.")
        return redirect("dashboard_admin")
    empleado = get_object_or_404(Empleado, id_emple_pk=id)
    empleado.estado_emple = 'inactivo' if empleado.estado_emple == 'activo' else 'activo'
    empleado.save()
    if empleado.id_auth_fk:
        empleado.id_auth_fk.activo = (empleado.estado_emple == 'activo')
        empleado.id_auth_fk.save()
    messages.success(request, f"Estado del empleado '{empleado.nom_emple} {empleado.apellido_emple}' actualizado a {empleado.estado_emple}.")
    return redirect('tabla_empleados')

def eliminar_empleado(request, id):
    empleado = get_object_or_404(Empleado, id_emple_pk=id)
    if request.method == 'POST':
        empleado.delete()
        messages.success(request, 'Empleado eliminado correctamente')
    return redirect('tabla_empleados')


# ── Clientes ──────────────────────────────────────────────

@transaction.atomic
def crear_cliente(request):
    fecha_max_17 = _fecha_max_17()
    ctx = {'fecha_max': fecha_max_17}
    if request.method == 'POST':
        # Validar campos obligatorios básicos
        required_fields = ['nom_clien', 'apellido_clien', 'fecha_naci_cliente', 'tel_cliente', 'correo_clien', 'direc_clien', 'nombre_usuario']
        for field in required_fields:
            if not request.POST.get(field, '').strip():
                messages.error(request, 'Por favor, completa todos los campos obligatorios.')
                return render(request, 'admin/personas/index-cliente.html', {
                    'fecha_max': fecha_max_17,
                    'datos': request.POST
                })

        fecha_str = request.POST.get('fecha_naci_cliente', '')
        if fecha_str and _calcular_edad(fecha_str) < 17:
            messages.error(request, 'El cliente debe tener al menos 17 años.')
            return render(request, 'admin/personas/index-cliente.html', {
                'fecha_max': fecha_max_17,
                'datos': request.POST
            })

        tel_cliente = request.POST.get('tel_cliente', '').strip()
        if _check_duplicate_phone(tel_cliente):
            messages.error(request, 'El número de celular ya está registrado por otra persona.')
            return render(request, 'admin/personas/index-cliente.html', {
                'fecha_max': fecha_max_17,
                'datos': request.POST
            })
        
        try:
            from core.models import UsuarioAuth, Rol, Empleado, Cliente
            import random, string

            correo = request.POST.get('correo_clien', '').strip()
            if Cliente.objects.filter(correo_clien=correo).exists() or Empleado.objects.filter(correo_emple=correo).exists():
                messages.error(request, 'Ya existe una persona registrada con este correo electrónico.')
                return render(request, 'admin/personas/index-cliente.html', {
                    'fecha_max': fecha_max_17,
                    'datos': request.POST
                })

            nombre_usuario = request.POST.get('nombre_usuario', '').strip()
            if not nombre_usuario or ' ' in nombre_usuario or len(nombre_usuario) > 20 or not any(c.isupper() for c in nombre_usuario):
                messages.error(request, 'El nombre de usuario no puede tener espacios, máximo 20 caracteres y debe tener al menos una letra mayúscula.')
                return render(request, 'admin/personas/index-cliente.html', {
                    'fecha_max': fecha_max_17,
                    'datos': request.POST
                })

            if UsuarioAuth.objects.filter(nombre_usuario=nombre_usuario).exists():
                messages.error(request, 'Ese nombre de usuario ya está en uso. Por favor, elige otro.')
                return render(request, 'admin/personas/index-cliente.html', {
                    'fecha_max': fecha_max_17,
                    'datos': request.POST
                })

            # Generar contraseña provisional
            caracteres = string.ascii_letters + string.digits
            rand_code = ''.join(random.choices(caracteres, k=6))
            temp_pass = f"Prov-{rand_code}"

            rol_cliente = Rol.objects.get(name='cliente')
            usuario = UsuarioAuth(nombre_usuario=nombre_usuario, rol=rol_cliente, activo=True)
            usuario.set_password(temp_pass)
            usuario.save()

            Cliente.objects.create(
                nom_clien          = request.POST['nom_clien'],
                apellido_clien     = request.POST['apellido_clien'],
                fecha_naci_cliente = fecha_str,
                tel_cliente        = tel_cliente,
                correo_clien       = correo,
                direc_clien        = request.POST['direc_clien'],
                estado_clien       = 'activo',
                id_auth_fk         = usuario
            )
            messages.success(request, f'Cliente registrado correctamente. Su contraseña provisional es: {temp_pass}')
            return redirect('tabla_clientes')
        except Exception as e:
            messages.error(request, f'Error al crear el cliente: {str(e)}')
            return render(request, 'admin/personas/index-cliente.html', {
                'fecha_max': fecha_max_17,
                'datos': request.POST
            })
            
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

        if _check_duplicate_phone(request.POST.get('tel_cliente', ''), current_cliente_id=id):
            messages.error(request, 'El número de celular ya está registrado por otra persona.')
            return redirect('tabla_clientes')

        cliente.nom_clien          = request.POST['nom_clien']
        cliente.apellido_clien     = request.POST['apellido_clien']
        cliente.fecha_naci_cliente = fecha_str
        cliente.tel_cliente        = request.POST['tel_cliente']
        cliente.correo_clien       = request.POST['correo_clien']
        cliente.direc_clien        = request.POST['direc_clien']
        cliente.save()
        
        nombre_usuario = request.POST.get('nombre_usuario')
        if nombre_usuario and cliente.id_auth_fk:
            cliente.id_auth_fk.nombre_usuario = nombre_usuario
            cliente.id_auth_fk.save()
            
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
    if request.session.get("rol") != "admin":
        messages.error(request, "Acceso denegado. Permisos insuficientes.")
        return redirect("dashboard_admin")
    
    categorias = CategoriaProducto.objects.all()
    
    if request.method == 'POST':
        tel = request.POST.get('tel_provee', '').strip()
        es_valido, msg_error = _validar_telefono(tel)
        if not es_valido:
            messages.error(request, f"Número de teléfono inválido: {msg_error}")
            return render(request, 'admin/inventario/index-proveedor.html', {'categorias': categorias})
        
        if _check_duplicate_phone(tel):
            messages.error(request, 'El número de celular ya está registrado por otra persona.')
            return render(request, 'admin/inventario/index-proveedor.html', {'categorias': categorias})
        if _check_duplicate_email(request.POST['correo_provee']):
            messages.error(request, 'El correo electrónico ya está registrado por otro proveedor.')
            return render(request, 'admin/inventario/index-proveedor.html', {'categorias': categorias})

        nit_cedula = request.POST.get('nit_cedula_provee', '').strip()
        if Proveedor.objects.filter(nit_cedula_provee=nit_cedula).exists():
            messages.error(request, 'El NIT o Cédula ya está registrado por otro proveedor.')
            return render(request, 'admin/inventario/index-proveedor.html', {'categorias': categorias})

        proveedor = Proveedor.objects.create(
            tipo_provee            = request.POST.get('tipo_provee', 'empresa'),
            nom_provee             = request.POST['nom_provee'],
            nit_cedula_provee      = nit_cedula,
            nombre_contacto_provee = request.POST.get('nombre_contacto_provee', ''),
            tel_provee             = tel,
            correo_provee          = request.POST['correo_provee'],
            direc_provee           = request.POST['direc_provee'],
            condicion_pago_provee  = request.POST.get('condicion_pago_provee', None),
            observaciones_provee   = request.POST.get('observaciones_provee', ''),
            estado_provee          = 'activo',
        )
        
        cats_ids = request.POST.getlist('categorias_provee')
        if cats_ids:
            proveedor.categorias_provee.set(cats_ids)

        messages.success(request, 'Proveedor registrado correctamente')
        return redirect('tabla_proveedores')
        
    return render(request, 'admin/inventario/index-proveedor.html', {'categorias': categorias})


def carga_proveedores(request):
    import csv
    import io
    from django.db import transaction

    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if not archivo:
            messages.error(request, 'No se ha seleccionado ningún archivo.')
            return render(request, 'admin/inventario/carga-proveedores.html')

        if not archivo.name.endswith('.csv'):
            messages.error(request, 'El archivo debe tener formato .csv.')
            return render(request, 'admin/inventario/carga-proveedores.html')

        try:
            # Decode the uploaded file
            decoded_file = archivo.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string, delimiter=',')
            header = next(reader, None)  # saltar header

            if not header or 'nit_cedula_provee' not in header:
                messages.error(request, 'El formato del CSV no coincide con las columnas esperadas.')
                return render(request, 'admin/inventario/carga-proveedores.html')

            with transaction.atomic():
                creados = 0
                for row in reader:
                    if not row or len(row) < 10:
                        continue
                    
                    tipo_provee            = row[0].strip()
                    nom_provee             = row[1].strip()
                    nit_cedula             = row[2].strip()
                    nombre_contacto_provee = row[3].strip()
                    tel_provee             = row[4].strip()
                    correo_provee          = row[5].strip()
                    direc_provee           = row[6].strip()
                    condicion_pago_provee  = row[7].strip() if row[7].strip() else None
                    observaciones_provee   = row[8].strip()
                    estado_provee          = row[9].strip()

                    # Validar si ya existe
                    if Proveedor.objects.filter(nit_cedula_provee=nit_cedula).exists():
                        continue

                    Proveedor.objects.create(
                        tipo_provee=tipo_provee,
                        nom_provee=nom_provee,
                        nit_cedula_provee=nit_cedula,
                        nombre_contacto_provee=nombre_contacto_provee,
                        tel_provee=tel_provee,
                        correo_provee=correo_provee,
                        direc_provee=direc_provee,
                        condicion_pago_provee=condicion_pago_provee,
                        observaciones_provee=observaciones_provee,
                        estado_provee=estado_provee
                    )
                    creados += 1

            messages.success(request, f'El archivo {archivo.name} procesado exitosamente. Se importaron {creados} proveedores.')
            return redirect('tabla_proveedores')

        except Exception as e:
            messages.error(request, f'Ocurrió un error al procesar el archivo: {e}')
            return render(request, 'admin/inventario/carga-proveedores.html')

    return render(request, 'admin/inventario/carga-proveedores.html')

def tabla_proveedores(request):
    if request.session.get("rol") != "admin":
        messages.error(request, "Acceso denegado. Permisos insuficientes.")
        return redirect("dashboard_admin")
    return render(request, 'admin/inventario/tabla-proveedor.html', {
        'proveedores': Proveedor.objects.all().order_by('id_provee_pk')
    })

def editar_proveedor(request, id):
    if request.session.get("rol") != "admin":
        messages.error(request, "Acceso denegado. Permisos insuficientes.")
        return redirect("dashboard_admin")
    proveedor = get_object_or_404(Proveedor, id_provee_pk=id)
    if request.method == 'POST':
        tel = request.POST.get('tel_provee', '').strip()
        es_valido, msg_error = _validar_telefono(tel)
        if not es_valido:
            messages.error(request, f"Número de teléfono inválido: {msg_error}")
            return redirect('tabla_proveedores')
        
        if _check_duplicate_phone(tel, current_proveedor_id=id):
            messages.error(request, 'El número de celular ya está registrado por otra persona.')
            return redirect('tabla_proveedores')
        if _check_duplicate_email(request.POST['correo_provee'], current_proveedor_id=id):
            messages.error(request, 'El correo electrónico ya está registrado por otro proveedor.')
            return redirect('tabla_proveedores')

        nit_cedula = request.POST.get('nit_cedula_provee', '').strip()
        if Proveedor.objects.filter(nit_cedula_provee=nit_cedula).exclude(id_provee_pk=id).exists():
            messages.error(request, 'El NIT o Cédula ya está registrado por otro proveedor.')
            return redirect('tabla_proveedores')

        proveedor.tipo_provee            = request.POST.get('tipo_provee', 'empresa')
        proveedor.nom_provee             = request.POST['nom_provee']
        proveedor.nit_cedula_provee      = nit_cedula
        proveedor.nombre_contacto_provee = request.POST.get('nombre_contacto_provee', '')
        proveedor.tel_provee             = tel
        proveedor.correo_provee          = request.POST['correo_provee']
        proveedor.direc_provee           = request.POST['direc_provee']
        proveedor.condicion_pago_provee  = request.POST.get('condicion_pago_provee', None)
        proveedor.observaciones_provee   = request.POST.get('observaciones_provee', '')
        proveedor.save()
        
        cats_ids = request.POST.getlist('categorias_provee')
        if cats_ids:
            proveedor.categorias_provee.set(cats_ids)
        else:
            proveedor.categorias_provee.clear()

        messages.success(request, 'Proveedor actualizado correctamente')
    return redirect('tabla_proveedores')

def cambiar_estado_proveedor(request, id):
    if request.session.get("rol") != "admin":
        messages.error(request, "Acceso denegado. Permisos insuficientes.")
        return redirect("dashboard_admin")
    proveedor = get_object_or_404(Proveedor, id_provee_pk=id)
    proveedor.estado_provee = 'inactivo' if proveedor.estado_provee == 'activo' else 'activo'
    proveedor.save()
    return redirect('tabla_proveedores')


# ── Perfil Admin ──────────────────────────────────────────

def editar_perfil_admin(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id or request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
        
    from core.models import UsuarioAuth, Empleado
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
        tel = request.POST.get('telefono', empleado.tel_emple)
        if _check_duplicate_phone(tel, current_empleado_id=empleado.id_emple_pk):
            messages.error(request, 'El número de celular ya está registrado por otra persona.')
            return redirect('editar_perfil_admin')

        empleado.nom_emple = request.POST.get('nombres', empleado.nom_emple)
        empleado.apellido_emple = request.POST.get('apellidos', empleado.apellido_emple)
        empleado.tel_emple = tel
        empleado.correo_emple = request.POST.get('correo', empleado.correo_emple)
        
        if 'fecha_naci_emple' in request.POST:
            empleado.fecha_naci_emple = request.POST.get('fecha_naci_emple')
        if 'direc_emple' in request.POST:
            empleado.direc_emple = request.POST.get('direc_emple')
        
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

def notificaciones_usuarios(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    from core.models import Notificacion, UsuarioAuth, Cliente
    usuario_id = request.session.get('usuario_id')

    try:
        usuario = UsuarioAuth.objects.get(id_auth_pk=usuario_id)
        cliente = Cliente.objects.get(id_auth_fk=usuario)
    except Exception:
        return redirect('login')

    # Notificaciones dirigidas a este cliente específico O de rol cliente sin destino
    from django.db.models import Q
    notif_list = Notificacion.objects.filter(
        Q(id_auth_destino_fk_id=usuario_id) |
        Q(destinatario_rol='cliente', id_auth_destino_fk__isnull=True)
    ).order_by('-fecha')
    
    cant_todas = notif_list.count()
    cant_noleidas = notif_list.filter(leida=False).count()
    cant_pedidos = notif_list.filter(tipo='pedido').count()
    cant_pagos = notif_list.filter(tipo__in=['pago', 'cancelacion']).count()

    return render(request, 'usuarios/notificaciones.html', {
        'notificaciones_todas': notif_list,
        'cant_todas': cant_todas,
        'cant_noleidas': cant_noleidas,
        'cant_pedidos': cant_pedidos,
        'cant_pagos': cant_pagos,
        'usuario_nombre': cliente.nom_clien,
    })

def favoritos_usuarios(request):
    return render(request, 'usuarios/favoritos.html')


def notificaciones_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    from core.models import Notificacion
    notif_list = Notificacion.objects.all().order_by('-fecha')
    
    # Calcular cantidades de filtros
    cant_todas = notif_list.count()
    cant_noleidas = notif_list.filter(leida=False).count()
    cant_pedidos = notif_list.filter(tipo='pedido').count()
    cant_inventario = notif_list.filter(tipo='inventario').count()
    cant_pagos = notif_list.filter(tipo='mensaje').count() # Usemos mensaje para pagos/mensajes indistintamente o lo que aplique
    
    return render(request, 'admin/notificaciones-admin.html', {
        'notificaciones_todas': notif_list,
        'cant_todas': cant_todas,
        'cant_noleidas': cant_noleidas,
        'cant_pedidos': cant_pedidos,
        'cant_inventario': cant_inventario,
        'cant_pagos': cant_pagos,
    })


def ajustes_admin(request):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    from core.models import UsuarioAuth, Empleado
    usuario_id = request.session.get('usuario_id')
    try:
        usuario = UsuarioAuth.objects.get(id_auth_pk=usuario_id)
        empleado = Empleado.objects.get(id_auth_fk=usuario)
    except (UsuarioAuth.DoesNotExist, Empleado.DoesNotExist):
        empleado = None
    return render(request, 'admin/ajustes.html', {'empleado': empleado})


def marcar_leida_notificacion(request, id):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    from core.models import Notificacion
    notif = get_object_or_404(Notificacion, id_notif_pk=id)
    notif.leida = True
    notif.save()
    messages.success(request, 'Notificación marcada como leída.')
    return redirect(request.META.get('HTTP_REFERER', 'notificaciones_admin'))


def eliminar_notificacion(request, id):
    if request.session.get('rol') not in ['admin', 'empleado']:
        return redirect('login')
    from core.models import Notificacion
    notif = get_object_or_404(Notificacion, id_notif_pk=id)
    notif.delete()
    messages.success(request, 'Notificación eliminada.')
    return redirect(request.META.get('HTTP_REFERER', 'notificaciones_admin'))


from django.http import JsonResponse

def subir_foto_perfil(request):
    if not request.session.get('usuario_id'):
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=401)
    
    if request.method == 'POST' and request.FILES.get('foto'):
        try:
            import os
            import uuid
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            from core.models import Cliente
            
            cliente = Cliente.objects.get(id_auth_fk_id=request.session['usuario_id'])
            foto = request.FILES['foto']
            
            # Validar formato
            ext = os.path.splitext(foto.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                return JsonResponse({'success': False, 'error': 'Formato de imagen no permitido'}, status=400)
            
            # Guardar
            filename = f"cliente_{uuid.uuid4().hex}{ext}"
            saved_path = default_storage.save(f"cliente/{filename}", ContentFile(foto.read()))
            
            # Borrar foto anterior si no es default
            if cliente.foto_cliente and cliente.foto_cliente != 'default.png':
                try:
                    if default_storage.exists(cliente.foto_cliente):
                        default_storage.delete(cliente.foto_cliente)
                except Exception:
                    pass
            
            cliente.foto_cliente = saved_path
            cliente.save()
            
            return JsonResponse({
                'success': True,
                'url': f"/media/{saved_path}"
            })
        except Cliente.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cliente no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    return JsonResponse({'success': False, 'error': 'Petición inválida'}, status=400)