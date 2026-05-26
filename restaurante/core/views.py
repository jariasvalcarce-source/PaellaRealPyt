from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date
from core.models import Rol, UsuarioAuth, Empleado, Cliente, Proveedor, Producto, UnidadMedida, CategoriaProducto

def inicio(request):
    return render(request, 'inicio.html')


# ══════════════════════════════════════════
# AUTENTICACIÓN
# ══════════════════════════════════════════

def login_view(request):
    if request.method == 'POST':
        email    = request.POST.get('email')
        password = request.POST.get('password')

        # --- ACCESO PROVISIONAL PARA CLIENTES ---
        if email == 'usuario@gmail.com' and password == 'usuario123':
            request.session['usuario_id'] = 0  # ID temporal o ficticio
            request.session['usuario']    = 'Cliente Provisional'
            request.session['rol']        = 'cliente'
            return redirect('inicio_usuarios')
        # ----------------------------------------

        try:
            # Buscar por correo electrónico
            user = UsuarioAuth.objects.select_related('rol').get(
                correo=email,
                activo=True
            )

            if user.check_password(password):
                request.session['usuario_id'] = user.id_auth_pk
                request.session['usuario']    = user.nombre_usuario
                request.session['rol']        = user.rol.name
                
                if user.requiere_cambio_pw:
                    request.session['cambio_pw_pendiente'] = True

                destinos = {
                    'admin':    'dashboard_admin',
                    'empleado': 'dashboard_empleado',
                    'cliente':  'inicio_usuarios',
                }
                return redirect(destinos[user.rol.name])
            else:
                messages.error(request, 'Contraseña incorrecta')

        except UsuarioAuth.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')

    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


def registro_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirmation = request.POST.get('password_confirmation')
        
        nom_clien = request.POST.get('nom_clien')
        apellido_clien = request.POST.get('apellido_clien')
        fecha_naci_cliente = request.POST.get('fecha_naci_cliente')
        tel_cliente = request.POST.get('tel_cliente')
        correo_clien = request.POST.get('correo_clien')
        direc_clien = request.POST.get('direc_clien')

        if password != password_confirmation:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('registro')

        if UsuarioAuth.objects.filter(correo=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return redirect('registro')

        try:
            # Obtener el rol de cliente, crearlo si no existe (robustez)
            rol_cliente, _ = Rol.objects.get_or_create(name='cliente', defaults={'name': 'cliente'})
            
            # Nombre de usuario único (<50 chars)
            base_username = email.split('@')[0][:40]
            import random
            unique_username = f"{base_username}_{random.randint(1000, 9999)}"
            
            # Crear credenciales de acceso (UsuarioAuth)
            usuario_auth = UsuarioAuth(
                nombre_usuario=unique_username,
                correo=email,
                rol=rol_cliente,
                activo=True
            )
            usuario_auth.set_password(password)
            usuario_auth.save()

            # Crear el perfil del cliente
            cliente = Cliente(
                nom_clien=nom_clien,
                apellido_clien=apellido_clien,
                fecha_naci_cliente=fecha_naci_cliente,
                tel_cliente=tel_cliente,
                correo_clien=correo_clien,
                direc_clien=direc_clien,
                estado_clien='activo',
                id_auth_fk=usuario_auth
            )
            cliente.save()

            messages.success(request, 'Cuenta creada exitosamente. Ahora puedes iniciar sesión.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error al registrar la cuenta: {str(e)}')
            return redirect('registro')

    hoy = date.today()
    try:
        max_date = hoy.replace(year=hoy.year - 17)
    except ValueError:
        max_date = hoy.replace(year=hoy.year - 17, day=28)
        
    return render(request, 'registro.html', {
        'fecha_max': max_date.strftime('%Y-%m-%d')
    })


# ══════════════════════════════════════════
# DASHBOARDS
# ══════════════════════════════════════════

def dashboard_admin(request):
    return render(request, 'admin/dashboard-admin.html')


def dashboard_empleado(request):
    return render(request, 'empleado/dashboard-empleado.html')


def inicio_usuarios(request):
    usuario_id = request.session.get('usuario_id')
    cliente = None
    if usuario_id and usuario_id != 0:
        cliente = Cliente.objects.filter(id_auth_fk=usuario_id).first()
        
    if request.method == 'POST' and request.POST.get('action') == 'cambiar_pw_provisional':
        nueva_pw = request.POST.get('nueva_password')
        conf_pw  = request.POST.get('conf_password')
        if nueva_pw and nueva_pw == conf_pw and usuario_id:
            user = UsuarioAuth.objects.get(id_auth_pk=usuario_id)
            user.set_password(nueva_pw)
            user.requiere_cambio_pw = False
            user.save()
            request.session.pop('cambio_pw_pendiente', None)
            messages.success(request, 'pw_changed_successfully')
            return redirect('inicio_usuarios')
        else:
            messages.error(request, 'Las contraseñas no coinciden o están vacías.')

    return render(request, 'usuarios/inicio-usuarios.html', {'cliente': cliente})

def mi_perfil(request):
    usuario_id = request.session.get('usuario_id')
    cliente = None
    if usuario_id and usuario_id != 0:
        cliente = Cliente.objects.filter(id_auth_fk=usuario_id).first()
        
        if request.method == 'POST' and cliente:
            try:
                cliente.nom_clien = request.POST.get('nombres')
                cliente.apellido_clien = request.POST.get('apellidos')
                cliente.fecha_naci_cliente = request.POST.get('fecha_nacimiento')
                cliente.tel_cliente = request.POST.get('telefono')
                cliente.direc_clien = request.POST.get('direccion')
                cliente.save()
                messages.success(request, '¡Perfil actualizado con éxito!')
                return redirect('mi_perfil')
            except Exception as e:
                messages.error(request, f'Error al actualizar: {str(e)}')

    return render(request, 'usuarios/mi-perfil.html', {'cliente': cliente})

def pedidos_usuario(request):
    return render(request, 'usuarios/index-pedido.html')

def carta_usuario(request):
    return render(request, 'usuarios/carta.html')

def carrito_usuario(request):
    return render(request, 'usuarios/carrito-compra.html')

def pago_usuario(request):
    return render(request, 'usuarios/index-pago-factura.html')


def personas_admin(request):
    return render(request, 'admin/personas/personas.html')

def inventario_admin(request):
    return render(request, 'admin/inventario/inventario.html')

def pedidos_admin(request):
    return render(request, 'admin/pedido/pedido.html')

def historial_ventas(request):
    return render(request, 'admin/factura/factura.html')


# ══════════════════════════════════════════
# EMPLEADOS
# ══════════════════════════════════════════

def crear_empleado(request):
    if request.method == 'POST':
        empleado = Empleado(
            nom_emple        = request.POST['nom_empleado'],
            apellido_emple   = request.POST['apellido_empleado'],
            fecha_naci_emple = request.POST['fecha_naci_empleado'],
            tel_emple        = request.POST['tel_empleado'],
            correo_emple     = request.POST['correo_empleado'],
            direc_emple      = request.POST['direc_empleado'],
            estado_emple     = 'activo'
        )
        empleado.save()
        messages.success(request, 'Empleado registrado correctamente')
        return redirect('tabla_empleados')

    return render(request, 'admin/personas/index-empleado.html', {
        'fecha_max': date.today().strftime('%Y-%m-%d')
    })


def tabla_empleados(request):
    empleados = Empleado.objects.all().order_by('nom_emple')
    return render(request, 'admin/personas/tabla-empleado.html', {
        'empleados': empleados
    })


def editar_empleado(request, id):
    empleado = get_object_or_404(Empleado, id_emple_pk=id)
    if request.method == 'POST':
        empleado.nom_emple        = request.POST['nom_emple']
        empleado.apellido_emple   = request.POST['apellido_emple']
        empleado.fecha_naci_emple = request.POST['fecha_naci_emple']
        empleado.tel_emple        = request.POST['tel_emple']
        empleado.correo_emple     = request.POST['correo_emple']
        empleado.direc_emple      = request.POST['direc_emple']
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


# ══════════════════════════════════════════
# CLIENTES
# ══════════════════════════════════════════

def crear_cliente(request):
    if request.method == 'POST':
        import random, string
        provisional_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        
        correo_clien = request.POST['correo_clien']
        nom_clien = request.POST['nom_clien']
        
        rol_cliente, _ = Rol.objects.get_or_create(name='cliente', defaults={'name': 'cliente'})
        base_username = correo_clien.split('@')[0][:40]
        unique_username = f"{base_username}_{random.randint(1000, 9999)}"
        
        usuario_auth = UsuarioAuth(
            nombre_usuario=unique_username,
            correo=correo_clien,
            rol=rol_cliente,
            activo=True,
            requiere_cambio_pw=True
        )
        usuario_auth.set_password(provisional_pass)
        usuario_auth.save()

        cliente = Cliente(
            nom_clien          = nom_clien,
            apellido_clien     = request.POST['apellido_clien'],
            fecha_naci_cliente = request.POST['fecha_naci_cliente'],
            tel_cliente        = request.POST['tel_cliente'],
            correo_clien       = correo_clien,
            direc_clien        = request.POST['direc_clien'],
            estado_clien       = 'activo',
            id_auth_fk         = usuario_auth
        )
        cliente.save()
        messages.success(request, f'Cliente registrado. Contraseña provisional: {provisional_pass}')
        return redirect('tabla_clientes')

    hoy = date.today()
    try:
        max_date = hoy.replace(year=hoy.year - 17)
    except ValueError:
        max_date = hoy.replace(year=hoy.year - 17, day=28)

    return render(request, 'admin/personas/index-cliente.html', {
        'fecha_max': max_date.strftime('%Y-%m-%d')
    })


def tabla_clientes(request):
    clientes = Cliente.objects.all().order_by('id_clien_pk')
    
    hoy = date.today()
    try:
        max_date = hoy.replace(year=hoy.year - 17)
    except ValueError:
        max_date = hoy.replace(year=hoy.year - 17, day=28)
        
    return render(request, 'admin/personas/tabla-cliente.html', {
        'clientes': clientes,
        'fecha_max': max_date.strftime('%Y-%m-%d')
    })


def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id_clien_pk=id)
    if request.method == 'POST':
        cliente.nom_clien          = request.POST['nom_clien']
        cliente.apellido_clien     = request.POST['apellido_clien']
        cliente.fecha_naci_cliente = request.POST['fecha_naci_cliente']
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
    return redirect('tabla_clientes')


def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id_clien_pk=id)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado correctamente')
    return redirect('tabla_clientes')

# ══════════════════════════════════════════
# PROVEEDORES
# ══════════════════════════════════════════

def crear_proveedor(request):
    if request.method == 'POST':
        proveedor = Proveedor(
            nom_provee        = request.POST['nom_provee'],
            apellido_provee   = request.POST.get('apellido_provee', ''),
            fecha_naci_provee = request.POST['fecha_naci_provee'],
            tel_provee        = request.POST['tel_provee'],
            correo_provee     = request.POST['correo_provee'],
            direc_provee      = request.POST['direc_provee'],
            estado_provee     = 'activo'
        )
        proveedor.save()
        messages.success(request, 'Proveedor registrado correctamente')
        return redirect('tabla_proveedores')

    return render(request, 'admin/inventario/index-proveedor.html', {
        'fecha_max': date.today().strftime('%Y-%m-%d')
    })


def tabla_proveedores(request):
    proveedores = Proveedor.objects.all().order_by('nom_provee')
    return render(request, 'admin/inventario/tabla-proveedor.html', {
        'proveedores': proveedores
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


# ══════════════════════════════════════════
# PRODUCTOS
# ══════════════════════════════════════════
def crear_producto(request):
    proveedores  = Proveedor.objects.filter(estado_provee='activo').order_by('nom_provee')
    unidades     = UnidadMedida.objects.all().order_by('nom_uni_medi')
    categorias   = CategoriaProducto.objects.all().order_by('nom_cate')

    if request.method == 'POST':
        producto = Producto(
            nom_produ            = request.POST['nom_produ'],
            stock_actual_produ   = request.POST['stock_actual_produ'],
            stock_minimo_produ   = request.POST['stock_minimo_produ'],
            fecha_venci_produ    = request.POST['fecha_venci_produ'],
            precio_uni_produ     = request.POST['precio_uni_produ'],
            des_produ            = request.POST['des_produ'],
            estado_produ         = 'disponible',
            id_provee_produ_fk   = get_object_or_404(Proveedor,       id_provee_pk=request.POST['id_provee_produ_fk']),
            id_uni_medi_produ_fk = get_object_or_404(UnidadMedida,    id_uni_medi_pk=request.POST['id_uni_medi_produ_fk']),
            id_cate_produ_fk     = get_object_or_404(CategoriaProducto, id_cate_produ_pk=request.POST['id_cate_produ_fk']),
        )
        producto.save()
        messages.success(request, 'Producto registrado correctamente')
        return redirect('tabla_productos')

    return render(request, 'admin/inventario/index-producto.html', {
        'proveedores': proveedores,
        'unidades':    unidades,
        'categorias':  categorias,
        'fecha_min':   date.today().strftime('%Y-%m-%d'),
    })


def tabla_productos(request):
    productos  = Producto.objects.select_related(
                    'id_provee_produ_fk',
                    'id_uni_medi_produ_fk',
                    'id_cate_produ_fk'
                ).all().order_by('nom_produ')
    return render(request, 'admin/inventario/tabla-productos.html', {
        'productos': productos
    })


def editar_producto(request, id):
    producto   = get_object_or_404(Producto, id_produ_pk=id)
    proveedores = Proveedor.objects.filter(estado_provee='activo').order_by('nom_provee')
    unidades    = UnidadMedida.objects.all().order_by('nom_uni_medi')
    categorias  = CategoriaProducto.objects.all().order_by('nom_cate')

    if request.method == 'POST':
        producto.nom_produ            = request.POST['nom_produ']
        producto.stock_actual_produ   = request.POST['stock_actual_produ']
        producto.stock_minimo_produ   = request.POST['stock_minimo_produ']
        producto.fecha_venci_produ    = request.POST['fecha_venci_produ']
        producto.precio_uni_produ     = request.POST['precio_uni_produ']
        producto.des_produ            = request.POST['des_produ']
        producto.id_provee_produ_fk   = get_object_or_404(Proveedor,         id_provee_pk=request.POST['id_provee_produ_fk'])
        producto.id_uni_medi_produ_fk = get_object_or_404(UnidadMedida,      id_uni_medi_pk=request.POST['id_uni_medi_produ_fk'])
        producto.id_cate_produ_fk     = get_object_or_404(CategoriaProducto, id_cate_produ_pk=request.POST['id_cate_produ_fk'])
        producto.save()
        messages.success(request, 'Producto actualizado correctamente')
        return redirect('tabla_productos')

    return render(request, 'admin/inventario/editar-producto.html', {
        'producto':    producto,
        'proveedores': proveedores,
        'unidades':    unidades,
        'categorias':  categorias,
    })

def cambiar_estado_producto(request, id):
    producto = get_object_or_404(Producto, id_produ_pk=id)
    estados  = ['disponible', 'no disponible', 'descontinuado']
    idx      = estados.index(producto.estado_produ)
    producto.estado_produ = estados[(idx + 1) % len(estados)]
    producto.save()
    return redirect('tabla_productos')