# views_inventario.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from datetime import date
from decimal import Decimal
from ..models import (
    Producto, Proveedor, UnidadMedida, CategoriaProducto,
    MovimientoProducto, Menu, TipoMenu, RecetaMenu, Empleado
)

ROLES_STAFF = ('admin', 'empleado')


def _staff_required(request):
    return request.session.get('rol') not in ROLES_STAFF


# ── Helpers ───────────────────────────────────────────────

def _contexto_producto():
    return {
        'proveedores': Proveedor.objects.filter(estado_provee='activo').order_by('nom_provee'),
        'unidades':    UnidadMedida.objects.all().order_by('nom_uni_medi'),
        'categorias':  CategoriaProducto.objects.all().order_by('nom_cate'),
    }


# ── Productos ─────────────────────────────────────────────

def crear_producto(request):
    ctx = {**_contexto_producto(), 'fecha_min': date.today().strftime('%Y-%m-%d')}
    if request.method == 'POST':
        Producto.objects.create(
            nom_produ            = request.POST['nom_produ'],
            stock_actual_produ   = request.POST['stock_actual_produ'],
            stock_minimo_produ   = request.POST['stock_minimo_produ'],
            fecha_venci_produ    = request.POST['fecha_venci_produ'],
            precio_uni_produ     = request.POST['precio_uni_produ'],
            des_produ            = request.POST['des_produ'],
            estado_produ         = 'disponible',
            id_provee_produ_fk   = get_object_or_404(Proveedor,         id_provee_pk=request.POST['id_provee_produ_fk']),
            id_uni_medi_produ_fk = get_object_or_404(UnidadMedida,      id_uni_medi_pk=request.POST['id_uni_medi_produ_fk']),
            id_cate_produ_fk     = get_object_or_404(CategoriaProducto, id_cate_produ_pk=request.POST['id_cate_produ_fk']),
        )
        messages.success(request, 'Producto registrado correctamente')
        return redirect('tabla_productos')
    return render(request, 'admin/inventario/index-producto.html', ctx)


def tabla_productos(request):
    ctx = {
        **_contexto_producto(),
        'productos': Producto.objects.select_related(
            'id_provee_produ_fk', 'id_uni_medi_produ_fk', 'id_cate_produ_fk'
        ).all().order_by('id_cate_produ_fk__nom_cate', 'nom_produ'),
    }
    return render(request, 'admin/inventario/tabla-productos.html', ctx)


def editar_producto(request, id):
    producto = get_object_or_404(Producto, id_produ_pk=id)
    ctx      = _contexto_producto()

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
        **ctx, 'producto': producto,
    })


def cambiar_estado_producto(request, id):
    producto = get_object_or_404(Producto, id_produ_pk=id)
    estados  = ['disponible', 'no disponible', 'descontinuado']
    producto.estado_produ = estados[(estados.index(producto.estado_produ) + 1) % 3]
    producto.save()
    return redirect('tabla_productos')


# ── Movimientos ───────────────────────────────────────────

def _actualizar_stock(producto, tipo, cantidad):
    anterior = producto.stock_actual_produ
    if tipo == 'entrada':
        producto.stock_actual_produ += cantidad
    else:
        producto.stock_actual_produ -= cantidad
    
    # Redondear a 3 decimales
    producto.stock_actual_produ = round(producto.stock_actual_produ, 3)
    posterior = producto.stock_actual_produ

    if posterior <= 0:
        producto.estado_produ = 'no disponible'
    elif producto.estado_produ == 'no disponible':
        producto.estado_produ = 'disponible'

    producto.save()
    return anterior, posterior


def crear_movimiento(request):
    empleados = lambda: Empleado.objects.filter(estado_emple='activo').order_by('nom_emple')
    productos  = lambda: Producto.objects.exclude(estado_produ='descontinuado').order_by('nom_produ')
    plantilla  = 'admin/inventario/index-movimiento-producto.html'

    if request.method == 'POST':
        tipo         = request.POST.get('tipo_movi')
        motivo       = request.POST.get('motivo_movi')
        cantidad_raw = request.POST.get('cant_movi')
        id_emple     = request.POST.get('id_emple_movi_fk')
        id_produ     = request.POST.get('id_produ_movi_fk')

        ctx = {'empleados': empleados(), 'productos': productos()}

        if not all([tipo, motivo, cantidad_raw, id_emple, id_produ]):
            messages.error(request, 'Todos los campos son obligatorios')
            return render(request, plantilla, ctx)

        try:
            cantidad = Decimal(cantidad_raw)
            if cantidad <= 0:
                raise ValueError
        except (ValueError, Exception):
            messages.error(request, 'La cantidad debe ser un número mayor a 0')
            return render(request, plantilla, ctx)

        producto = get_object_or_404(Producto, id_produ_pk=id_produ)
        empleado = get_object_or_404(Empleado, id_emple_pk=id_emple)

        if tipo == 'salida' and cantidad > producto.stock_actual_produ:
            messages.error(
                request,
                f'Stock insuficiente. Disponible: '
                f'{producto.stock_actual_produ} {producto.id_uni_medi_produ_fk.abreviatura}'
            )
            return render(request, plantilla, ctx)

        anterior, posterior = _actualizar_stock(producto, tipo, cantidad)
        MovimientoProducto.objects.create(
            tipo_movi        = tipo,
            motivo_movi      = motivo,
            cant_movi        = cantidad,
            stock_anterior   = anterior,
            stock_posterior  = posterior,
            id_emple_movi_fk = empleado,
            id_produ_movi_fk = producto,
        )
        messages.success(request, f'Movimiento de {tipo} registrado correctamente')
        return redirect('tabla_movimientos')

    return render(request, plantilla, {
        'empleados': empleados(), 'productos': productos()
    })


def tabla_movimientos(request):
    movimientos = MovimientoProducto.objects.select_related(
        'id_produ_movi_fk',
        'id_emple_movi_fk',
        'id_produ_movi_fk__id_uni_medi_produ_fk'
    ).all().order_by('-fecha_movi')
    return render(request, 'admin/inventario/tabla-movimiento-producto.html', {
        'movimientos': movimientos,
        'empleados': Empleado.objects.filter(estado_emple='activo')
    })


# ── Menús ─────────────────────────────────────────────────

def crear_menu(request):
    tipos = TipoMenu.objects.all().order_by('nom_tipo_menu')
    if request.method == 'POST':
        menu = Menu(
            nom_menu        = request.POST['nom_menu'],
            precio_menu     = request.POST['precio_menu'],
            des_menu        = request.POST['des_menu'],
            id_tipo_menu_fk = get_object_or_404(TipoMenu, id_tipo_menu_pk=request.POST['id_tipo_menu_fk']),
            disponible_menu = 1,
        )
        if 'img_menu' in request.FILES:
            menu.img_menu = request.FILES['img_menu']
        menu.save()
        messages.success(request, 'Menú registrado correctamente')
        return redirect('tabla_menus')
    return render(request, 'admin/inventario/index-menu.html', {'tipos': tipos})


def tabla_menus(request):
    tipos = TipoMenu.objects.all().order_by('nom_tipo_menu')
    
    orden_tipos = Case(
        When(id_tipo_menu_fk__nom_tipo_menu__icontains='paella', then=1),
        When(id_tipo_menu_fk__nom_tipo_menu__icontains='aperitivo', then=2),
        When(id_tipo_menu_fk__nom_tipo_menu__icontains='postre', then=3),
        When(id_tipo_menu_fk__nom_tipo_menu__icontains='bebida', then=4),
        default=5,
        output_field=IntegerField(),
    )

    menus = Menu.objects.select_related('id_tipo_menu_fk').all().order_by(orden_tipos, 'nom_menu')
    return render(request, 'admin/inventario/tabla-menus.html', {
        'menus': menus, 'tipos': tipos,
    })


def editar_menu(request, id):
    menu = get_object_or_404(Menu, id_menu_pk=id)
    if request.method == 'POST':
        menu.nom_menu        = request.POST['nom_menu']
        menu.precio_menu     = request.POST['precio_menu']
        menu.des_menu        = request.POST['des_menu']
        menu.id_tipo_menu_fk = get_object_or_404(TipoMenu, id_tipo_menu_pk=request.POST['id_tipo_menu_fk'])
        menu.disponible_menu = 1 if request.POST.get('disponible_menu') else 0
        if 'img_menu' in request.FILES:
            menu.img_menu = request.FILES['img_menu']
        menu.save()
        messages.success(request, 'Menú actualizado correctamente')
    return redirect('tabla_menus')


def cambiar_disponibilidad_menu(request, id):
    menu = get_object_or_404(Menu, id_menu_pk=id)
    menu.disponible_menu = 0 if menu.disponible_menu else 1
    menu.save()
    return redirect('tabla_menus')


def eliminar_menu(request, id):
    menu = get_object_or_404(Menu, id_menu_pk=id)
    if request.method == 'POST':
        menu.delete()
        messages.success(request, 'Menú eliminado correctamente')
    return redirect('tabla_menus')


# ── Recetas ───────────────────────────────────────────────

def crear_receta(request):
    if _staff_required(request):
        return redirect('login')

    menus                = Menu.objects.all()
    productos            = Producto.objects.filter(estado_produ='disponible')
    unidades             = UnidadMedida.objects.all()
    menu_preseleccionado = request.GET.get('menu', '')
    
    ingredientes_actuales = []
    if menu_preseleccionado:
        ingredientes_actuales = RecetaMenu.objects.filter(id_menu_fk=menu_preseleccionado).select_related('id_produ_fk', 'id_uni_medi_fk')

    if request.method == 'POST':
        id_menu = request.POST.get('id_menu_fk')
        total   = int(request.POST.get('total_ingredientes', 0))

        ctx = {
            'menus': menus, 'productos': productos,
            'unidades': unidades, 'menu_preseleccionado': menu_preseleccionado,
            'ingredientes_actuales': ingredientes_actuales,
        }

        if not id_menu:
            messages.error(request, 'Debes seleccionar un menú.')
            return render(request, 'admin/inventario/index-receta.html', ctx)

        if total == 0:
            messages.error(request, 'Agrega al menos un ingrediente a la receta.')
            return render(request, 'admin/inventario/index-receta.html', ctx)

        errores   = []
        guardados = 0

        for i in range(total):
            id_produ  = request.POST.get(f'id_produ_fk_{i}')
            cantidad  = request.POST.get(f'cantidad_reque_{i}')
            id_unidad = request.POST.get(f'id_uni_medi_fk_{i}')
            notas     = request.POST.get(f'notas_{i}', '').strip()

            if not all([id_produ, cantidad, id_unidad]):
                continue

            if RecetaMenu.objects.filter(id_menu_fk=id_menu, id_produ_fk=id_produ).exists():
                producto = Producto.objects.filter(id_produ_pk=id_produ).first()
                errores.append(f'"{producto.nom_produ}" ya está en la receta de ese menú.')
                continue

            try:
                RecetaMenu.objects.create(
                    id_menu_fk_id     = id_menu,
                    id_produ_fk_id    = id_produ,
                    cantidad_reque    = cantidad,
                    id_uni_medi_fk_id = id_unidad,
                    notas             = notas or None,
                )
                guardados += 1
            except Exception as e:
                errores.append(f'Error al guardar ingrediente {i+1}: {e}')

        for err in errores:
            messages.error(request, err)

        if guardados > 0:
            messages.success(request, f'{guardados} ingrediente(s) guardados correctamente.')
            return redirect('tabla_recetas')

        return render(request, 'admin/inventario/index-receta.html', ctx)

    return render(request, 'admin/inventario/index-receta.html', {
        'menus': menus, 'productos': productos,
        'unidades': unidades, 'menu_preseleccionado': menu_preseleccionado,
        'ingredientes_actuales': ingredientes_actuales,
    })


def tabla_recetas(request):
    if _staff_required(request):
        return redirect('login')

    orden_tipos = Case(
        When(id_menu_fk__id_tipo_menu_fk__nom_tipo_menu__icontains='paella', then=1),
        When(id_menu_fk__id_tipo_menu_fk__nom_tipo_menu__icontains='aperitivo', then=2),
        When(id_menu_fk__id_tipo_menu_fk__nom_tipo_menu__icontains='postre', then=3),
        When(id_menu_fk__id_tipo_menu_fk__nom_tipo_menu__icontains='bebida', then=4),
        default=5,
        output_field=IntegerField(),
    )

    recetas = RecetaMenu.objects.select_related(
        'id_menu_fk', 'id_produ_fk', 'id_uni_medi_fk', 'id_menu_fk__id_tipo_menu_fk'
    ).all().order_by(orden_tipos, 'id_menu_fk__nom_menu', 'id_produ_fk__nom_produ')

    # Estructura: [ { 'nom_tipo': 'Bebidas', 'menus': [ {'menu': <Menu>, 'ingredientes': [...] } ] } ]
    categorias_dict = {}

    for receta in recetas:
        menu = receta.id_menu_fk
        tipo_nombre = menu.id_tipo_menu_fk.nom_tipo_menu

        if tipo_nombre not in categorias_dict:
            categorias_dict[tipo_nombre] = {}
            
        if menu.id_menu_pk not in categorias_dict[tipo_nombre]:
            categorias_dict[tipo_nombre][menu.id_menu_pk] = {
                'menu': menu,
                'ingredientes': []
            }
            
        categorias_dict[tipo_nombre][menu.id_menu_pk]['ingredientes'].append(receta)

    # Convertir a lista plana para el template
    categorias_lista = []
    for tipo, menus_dict in categorias_dict.items():
        categorias_lista.append({
            'nom_tipo': tipo,
            'menus': menus_dict.values()
        })

    return render(request, 'admin/inventario/tabla-receta.html', {
        'categorias':        categorias_lista,
        'menus':             Menu.objects.all(),
        'productos':         Producto.objects.filter(estado_produ='disponible'),
        'unidades':          UnidadMedida.objects.all(),
    })


def editar_receta(request, id_receta):
    if _staff_required(request):
        return redirect('login')

    receta = get_object_or_404(RecetaMenu, id_receta_pk=id_receta)

    if request.method == 'POST':
        id_menu   = request.POST.get('id_menu_fk')
        id_produ  = request.POST.get('id_produ_fk')
        cantidad  = request.POST.get('cantidad_reque')
        id_unidad = request.POST.get('id_uni_medi_fk')
        notas     = request.POST.get('notas', '').strip()

        if not all([id_menu, id_produ, cantidad, id_unidad]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('tabla_recetas')

        if RecetaMenu.objects.filter(
            id_menu_fk=id_menu, id_produ_fk=id_produ
        ).exclude(id_receta_pk=id_receta).exists():
            messages.error(request, 'Ese producto ya existe en la receta de ese menú.')
            return redirect('tabla_recetas')

        receta.id_menu_fk_id     = id_menu
        receta.id_produ_fk_id    = id_produ
        receta.cantidad_reque    = cantidad
        receta.id_uni_medi_fk_id = id_unidad
        receta.notas             = notas if notas else None
        receta.save()
        messages.success(request, 'Receta actualizada correctamente.')

    return redirect('tabla_recetas')


def eliminar_receta(request, id_receta):
    if _staff_required(request):
        return redirect('login')
    receta = get_object_or_404(RecetaMenu, id_receta_pk=id_receta)
    receta.delete()
    messages.success(request, 'Ingrediente eliminado de la receta.')
    return redirect('tabla_recetas')


def editar_unidad_receta(request, id_unidad):
    if _staff_required(request):
        return redirect('login')

    unidad = get_object_or_404(UnidadMedida, id_uni_medi_pk=id_unidad)

    if request.method == 'POST':
        nom  = request.POST.get('nom_uni_medi', '').strip()
        abr  = request.POST.get('abreviatura', '').strip()
        tipo = request.POST.get('tipo_uni_medi', '').strip()

        if not all([nom, abr, tipo]):
            messages.error(request, 'Todos los campos de la unidad son obligatorios.')
            return redirect('crear_receta')

        unidad.nom_uni_medi  = nom
        unidad.abreviatura   = abr
        unidad.tipo_uni_medi = tipo
        unidad.save()
        messages.success(request, f'Unidad "{nom}" actualizada.')

    return redirect('crear_receta')


def eliminar_unidad_receta(request, id_unidad):
    if _staff_required(request):
        return redirect('login')

    unidad = get_object_or_404(UnidadMedida, id_uni_medi_pk=id_unidad)

    if RecetaMenu.objects.filter(id_uni_medi_fk=unidad).exists():
        messages.error(request, 'No se puede eliminar: la unidad está en uso en una o más recetas.')
    else:
        nombre = unidad.nom_uni_medi
        unidad.delete()
        messages.success(request, f'Unidad "{nombre}" eliminada.')

    return redirect('crear_receta')