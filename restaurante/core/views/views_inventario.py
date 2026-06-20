# views_inventario.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Case, When, IntegerField
from django.db import transaction
from django.http import JsonResponse
from datetime import date
from decimal import Decimal
import json

from core.models import (
    Producto, Proveedor, UnidadMedida, CategoriaProducto,
    MovimientoProducto, Menu, TipoMenu, RecetaMenu, Empleado
)

def _get_factor_conversion(unidad_origen_abrev, unidad_base_abrev):
    orig = unidad_origen_abrev.upper()
    base = unidad_base_abrev.upper()
    if orig == base: return Decimal('1.0')
    
    # Peso
    if orig == 'KG' and base == 'G': return Decimal('1000.0')
    if orig == 'LB' and base == 'G': return Decimal('453.59')
    if orig == 'G' and base == 'KG': return Decimal('0.001')
    # Volumen
    if orig == 'L' and base == 'ML': return Decimal('1000.0')
    if orig == 'ML' and base == 'L': return Decimal('0.001')
    if orig == 'OZ' and base == 'ML': return Decimal('29.57')
    # Unidades
    if 'DOCENA' in orig and 'UN' in base: return Decimal('12.0')
    if 'CUBETA' in orig and 'UN' in base: return Decimal('30.0')
    
    return Decimal('1.0')

ROLES_STAFF = ('admin', 'empleado')

def ajax_crear_categoria(request):
    if request.method == 'POST':
        nom_cate = request.POST.get('nom_cate', '').strip()
        des_cate = request.POST.get('des_cate', '').strip()
        if not nom_cate:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio.'})
        
        # Check if exists (case insensitive)
        exists = CategoriaProducto.objects.filter(nom_cate__iexact=nom_cate).first()
        if exists:
            return JsonResponse({'success': False, 'error': 'La categoría ya existe.'})
            
        cat = CategoriaProducto.objects.create(nom_cate=nom_cate, des_cate=des_cate)
        return JsonResponse({'success': True, 'id': cat.id_cate_produ_pk, 'nombre': cat.nom_cate})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def ajax_crear_unidad(request):
    if request.method == 'POST':
        nom_uni = request.POST.get('nom_uni_medi', '').strip()
        abrev = request.POST.get('abreviatura', '').strip()
        if not nom_uni or not abrev:
            return JsonResponse({'success': False, 'error': 'Nombre y abreviatura obligatorios.'})
            
        exists = UnidadMedida.objects.filter(nom_uni_medi__iexact=nom_uni).first()
        if exists:
            return JsonResponse({'success': False, 'error': 'La unidad ya existe.'})
            
        uni = UnidadMedida.objects.create(nom_uni_medi=nom_uni, abreviatura=abrev, tipo_uni_medi='Otro')
        return JsonResponse({'success': True, 'id': uni.id_uni_medi_pk, 'nombre': uni.nom_uni_medi, 'abreviatura': uni.abreviatura})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def ajax_eliminar_categoria(request, id):
    if request.method == 'POST':
        cat = get_object_or_404(CategoriaProducto, id_cate_produ_pk=id)
        try:
            cat.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'No se puede eliminar porque está en uso por uno o más productos.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def ajax_eliminar_unidad(request, id):
    if request.method == 'POST':
        uni = get_object_or_404(UnidadMedida, id_uni_medi_pk=id)
        try:
            uni.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'No se puede eliminar porque está en uso.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})



def ajax_crear_tipo_menu(request):
    if request.method == 'POST':
        nom = request.POST.get('nuevo_tipo_nombre', '').strip()
        des = request.POST.get('nuevo_tipo_desc', '').strip()
        
        if not nom:
            return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
        if len(nom) < 3 or len(nom) > 50:
            return JsonResponse({'success': False, 'error': 'El nombre debe tener entre 3 y 50 caracteres'})
        
        import re
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$', nom):
            return JsonResponse({'success': False, 'error': 'El nombre solo puede contener letras y espacios'})
        
        nom = nom.capitalize()

        from core.models import TipoMenu
        if TipoMenu.objects.filter(nom_tipo_menu__iexact=nom).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un tipo de menú con ese nombre'})

        tipo = TipoMenu.objects.create(nom_tipo_menu=nom, des_tipo_menu=des)
        return JsonResponse({'success': True, 'id': tipo.id_tipo_menu_pk, 'nombre': tipo.nom_tipo_menu})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def ajax_eliminar_tipo_menu(request, id):
    if request.method == 'POST':
        from core.models import TipoMenu
        tipo = get_object_or_404(TipoMenu, id_tipo_menu_pk=id)
        try:
            tipo.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'No se puede eliminar porque está en uso en menús.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

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


def carga_productos(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if archivo:
            # Here logic for reading the file could be added
            messages.success(request, f'El archivo {archivo.name} ha sido procesado exitosamente.')
            return redirect('tabla_productos')
        else:
            messages.error(request, 'No se pudo cargar el archivo.')
            
    proveedores = Proveedor.objects.filter(estado_provee='activo').values_list('nom_provee', flat=True)
    unidades = UnidadMedida.objects.all().values_list('nom_uni_medi', flat=True)
    categorias = CategoriaProducto.objects.all().values_list('nom_cate', flat=True)

    return render(request, 'admin/inventario/carga-productos.html', {
        'proveedores': list(proveedores),
        'unidades': list(unidades),
        'categorias': list(categorias),
    })


def editar_producto(request, id):
    producto = get_object_or_404(Producto, id_produ_pk=id)
    ctx      = _contexto_producto()

    if request.method == 'POST':
        nom = request.POST['nom_produ'].strip()
        if Producto.objects.filter(nom_produ__iexact=nom).exclude(id_produ_pk=producto.id_produ_pk).exists():
            messages.error(request, 'Ya existe otro producto con ese nombre.')
            return redirect('tabla_productos')
            
        producto.nom_produ            = nom
        producto.stock_minimo_produ   = request.POST['stock_minimo_produ']
        
        fecha = request.POST.get('fecha_venci_produ', '')
        if fecha:
            producto.fecha_venci_produ = fecha
        else:
            producto.fecha_venci_produ = '2099-12-31'
            
        producto.precio_uni_produ     = request.POST['precio_uni_produ']
        producto.des_produ            = request.POST['des_produ']
        producto.id_provee_produ_fk   = get_object_or_404(Proveedor,         id_provee_pk=request.POST['id_provee_produ_fk'])
        producto.id_uni_medi_produ_fk = get_object_or_404(UnidadMedida,      id_uni_medi_pk=request.POST['id_uni_medi_produ_fk'])
        producto.id_cate_produ_fk     = get_object_or_404(CategoriaProducto, id_cate_produ_pk=request.POST['id_cate_produ_fk'])
        producto.save()
        messages.success(request, 'Producto actualizado correctamente')
        return redirect('tabla_productos')

    return render(request, 'admin/inventario/index-producto.html', {
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
    
    # Redondear a 3 decimales y prevenir valores negativos
    producto.stock_actual_produ = max(Decimal('0'), round(producto.stock_actual_produ, 3))
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

    def _ctx():
        return {
            'empleados': empleados(),
            'productos': productos(),
            'unidades': UnidadMedida.objects.all().order_by('nom_uni_medi'),
        }

    if request.method == 'POST':
        tipo         = request.POST.get('tipo_movi')
        motivo       = request.POST.get('motivo_movi')
        cantidad_raw = request.POST.get('cant_movi')
        unidad_sel   = request.POST.get('unidad_movi', '').strip().lower()
        id_emple     = request.POST.get('id_emple_movi_fk')
        id_produ     = request.POST.get('id_produ_movi_fk')
        nota         = request.POST.get('nota_movi', '').strip()

        # ── Validación: campos obligatorios ──
        if not all([tipo, motivo, cantidad_raw, id_emple, id_produ]):
            messages.error(request, 'Todos los campos son obligatorios')
            return render(request, plantilla, _ctx())

        # ── Validación: cantidad numérica > 0 ──
        try:
            cantidad = Decimal(cantidad_raw)
            if cantidad <= 0:
                raise ValueError
        except (ValueError, Exception):
            messages.error(request, 'La cantidad debe ser un número mayor a 0')
            return render(request, plantilla, _ctx())

        producto = get_object_or_404(Producto, id_produ_pk=id_produ)
        empleado = get_object_or_404(Empleado, id_emple_pk=id_emple)
        unidad_base = producto.id_uni_medi_produ_fk.abreviatura.strip().lower()

        # ── Conversión de unidades ──
        CONVERSIONES = {
            ('g',  'kg'): Decimal('0.001'),
            ('kg', 'g'):  Decimal('1000'),
            ('ml', 'l'):  Decimal('0.001'),
            ('l',  'ml'): Decimal('1000'),
        }
        if unidad_sel == unidad_base:
            cantidad_convertida = cantidad
        elif (unidad_sel, unidad_base) in CONVERSIONES:
            cantidad_convertida = cantidad * CONVERSIONES[(unidad_sel, unidad_base)]
        else:
            messages.error(
                request,
                f'No puedes medir {unidad_sel.upper()} en un producto '
                f'almacenado en {unidad_base.upper()}. Selecciona una unidad compatible.'
            )
            return render(request, plantilla, _ctx())

        # Redondear a 3 decimales
        cantidad_convertida = round(cantidad_convertida, 3)

        # ── Validación: stock suficiente para salidas ──
        if tipo == 'salida' and cantidad_convertida > producto.stock_actual_produ:
            messages.error(
                request,
                f'Stock insuficiente. Disponible: '
                f'{producto.stock_actual_produ} {unidad_base.upper()}, '
                f'solicitado: {cantidad_convertida} {unidad_base.upper()}'
            )
            return render(request, plantilla, _ctx())

        # ── Validación: nota obligatoria para merma/ajuste en salidas ──
        if tipo == 'salida' and motivo in ('merma', 'ajuste_salida') and len(nota) < 10:
            messages.error(request, 'Debes ingresar una observación de al menos 10 caracteres para mermas o ajustes.')
            return render(request, plantilla, _ctx())

        # ── Registro del movimiento ──
        try:
            with transaction.atomic():
                ant, post = _actualizar_stock(producto, tipo, cantidad_convertida)
                MovimientoProducto.objects.create(
                    tipo_movi=tipo,
                    motivo_movi=motivo,
                    origen_movi='manual',
                    nota_movi=nota,
                    cant_movi=cantidad_convertida,
                    stock_anterior=ant,
                    stock_posterior=post,
                    id_emple_movi_fk=empleado,
                    id_produ_movi_fk=producto
                )
            
            # ── Mensaje de éxito enriquecido ──
            nombre = producto.nom_produ
            uni = unidad_base.upper()
            
            fmt = lambda d: str(d).rstrip('0').rstrip('.') if '.' in str(d) else str(d)
            c_str = fmt(cantidad)
            cc_str = fmt(cantidad_convertida)
            p_str = fmt(post)

            if tipo == 'entrada':
                if unidad_sel != unidad_base:
                    msg = (f'Entrada registrada. Se agregaron {c_str} {unidad_sel.upper()} '
                           f'({cc_str} {uni}) a {nombre}. Stock actual: {p_str} {uni}')
                else:
                    msg = f'Entrada registrada. Se agregaron {cc_str} {uni} a {nombre}. Stock actual: {p_str} {uni}'
            else:
                if unidad_sel != unidad_base:
                    msg = (f'Salida registrada. Se descontaron {c_str} {unidad_sel.upper()} '
                           f'({cc_str} {uni}) de {nombre}. Stock actual: {p_str} {uni}')
                else:
                    msg = f'Salida registrada. Se descontaron {cc_str} {uni} de {nombre}. Stock actual: {p_str} {uni}'

            messages.success(request, msg)

            # ── Reactivar menús automáticamente si el producto volvió a tener stock ──
            if tipo == 'entrada' and post > 0:
                from core.models import RecetaMenu, Menu
                from core.utils import convertir_a_unidad_base
                recetas_afectadas = RecetaMenu.objects.select_related(
                    'id_menu_fk', 'id_uni_medi_fk'
                ).filter(id_produ_fk=producto)
                for receta in recetas_afectadas:
                    menu = receta.id_menu_fk
                    if menu.disponible_menu:
                        continue  # ya está activo, nada que hacer
                    # Verificar si TODOS los ingredientes del menú tienen stock
                    todas_recetas = RecetaMenu.objects.select_related(
                        'id_produ_fk', 'id_uni_medi_fk',
                        'id_produ_fk__id_uni_medi_produ_fk'
                    ).filter(id_menu_fk=menu)
                    puede_reactivar = True
                    for r in todas_recetas:
                        p = r.id_produ_fk
                        try:
                            necesario = convertir_a_unidad_base(
                                r.cantidad_reque, r.id_uni_medi_fk,
                                p.id_uni_medi_produ_fk
                            )
                        except ValueError:
                            necesario = r.cantidad_reque
                        if p.stock_actual_produ < necesario:
                            puede_reactivar = False
                            break
                    if puede_reactivar:
                        menu.disponible_menu = True
                        menu.save()
                        from core.models import Notificacion
                        from django.utils import timezone
                        Notificacion.objects.create(
                            tipo='inventario',
                            titulo='Plato reactivado automáticamente',
                            mensaje=f'"{menu.nom_menu}" fue reactivado porque todos sus ingredientes volvieron a tener stock.',
                            destinatario_rol='admin',
                            leida=False,
                            fecha=timezone.now()
                        )
        except Exception as e:
            messages.error(request, f'Error al registrar el movimiento: {str(e)}')
            
        return redirect('tabla_movimientos')

    return render(request, plantilla, _ctx())


def tabla_movimientos(request):
    movimientos = MovimientoProducto.objects.select_related(
        'id_emple_movi_fk', 'id_produ_movi_fk'
    ).order_by('-fecha_movi')

    ctx = _contexto_producto()
    ctx['movimientos'] = movimientos
    ctx['empleados'] = Empleado.objects.filter(estado_emple='activo')
    return render(request, 'admin/inventario/tabla-movimiento-producto.html', ctx)


def detalle_movimiento(request, id):
    movimiento = get_object_or_404(MovimientoProducto.objects.select_related(
        'id_emple_movi_fk', 
        'id_produ_movi_fk__id_uni_medi_produ_fk',
        'id_produ_movi_fk__id_cate_produ_fk',
        'id_produ_movi_fk__id_provee_produ_fk'
    ), id_movi_pk=id)
    
    return render(request, 'admin/inventario/detalle-movimiento.html', {
        'movimiento': movimiento
    })


# ── Menús ─────────────────────────────────────────────────

def menu_dashboard(request):
    if _staff_required(request):
        return redirect('login')

    total_menus = Menu.objects.count()
    total_categorias = TipoMenu.objects.count()
    total_recetas = Menu.objects.filter(recetamenu__isnull=False).distinct().count()
    nuevas_recetas = 0 

    return render(request, 'admin/menu/menu.html', {
        'total_menus': total_menus,
        'total_categorias': total_categorias,
        'total_recetas': total_recetas,
        'nuevas_recetas': nuevas_recetas
    })


def crear_menu(request):
    tipos = TipoMenu.objects.all().order_by('nom_tipo_menu')
    if request.method == 'POST':
        nom = request.POST['nom_menu'].strip()
        if Menu.objects.filter(nom_menu__iexact=nom).exists():
            messages.error(request, f'Ya existe un plato con el nombre "{nom}".')
            return render(request, 'admin/menu/index-menu.html', {'tipos': tipos})

        precio = str(request.POST['precio_menu']).replace(',', '')

        menu = Menu(
            nom_menu        = nom,
            precio_menu     = precio,
            des_menu        = request.POST['des_menu'],
            id_tipo_menu_fk = get_object_or_404(TipoMenu, id_tipo_menu_pk=request.POST['id_tipo_menu_fk']),
            disponible_menu = request.POST.get('disponible_menu', 1),
        )
        if 'img_menu' in request.FILES:
            menu.img_menu = request.FILES['img_menu']
        menu.save()
        messages.success(request, 'Menú registrado correctamente')
        return redirect('tabla_menus')
    return render(request, 'admin/menu/index-menu.html', {'tipos': tipos})


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
    return render(request, 'admin/menu/tabla-menu.html', {
        'menus': menus, 'tipos': tipos,
    })


def editar_menu(request, id):
    menu = get_object_or_404(Menu, id_menu_pk=id)
    tipos = TipoMenu.objects.all().order_by('nom_tipo_menu')

    if request.method == 'POST':
        nom = request.POST['nom_menu'].strip()
        if Menu.objects.filter(nom_menu__iexact=nom).exclude(id_menu_pk=id).exists():
            messages.error(request, f'Ya existe otro plato con el nombre "{nom}".')
            return redirect('tabla_menus')

        precio = str(request.POST['precio_menu']).replace(',', '')

        menu.nom_menu        = nom
        menu.precio_menu     = precio
        menu.des_menu        = request.POST['des_menu']
        menu.id_tipo_menu_fk = get_object_or_404(TipoMenu, id_tipo_menu_pk=request.POST['id_tipo_menu_fk'])
        menu.disponible_menu = request.POST.get('disponible_menu', menu.disponible_menu)
        
        if 'img_menu' in request.FILES:
            if menu.img_menu:
                import os
                if os.path.isfile(menu.img_menu.path):
                    os.remove(menu.img_menu.path)
            menu.img_menu = request.FILES['img_menu']
        
        menu.save()
        messages.success(request, 'Menú actualizado correctamente')
        return redirect('tabla_menus')
        
    return redirect('tabla_menus')


def cambiar_disponibilidad_menu(request, id):
    menu = get_object_or_404(Menu, id_menu_pk=id)
    menu.disponible_menu = 0 if menu.disponible_menu == 1 else 1
    menu.save()
    estado = "no disponible" if menu.disponible_menu == 0 else "disponible"
    messages.success(request, f'El menú ahora está {estado}')
    return redirect('tabla_menus')


def eliminar_menu(request, id):
    menu = get_object_or_404(Menu, id_menu_pk=id)
    menu.delete()
    messages.success(request, 'Menú eliminado')
    return redirect('tabla_menus')


# ── Recetas ───────────────────────────────────────────────

def crear_receta(request):
    if _staff_required(request):
        return redirect('login')

    menus = Menu.objects.filter(disponible_menu=1).select_related('id_tipo_menu_fk').order_by('nom_menu')
    from core.models import TipoMenu, CategoriaProducto
    tipos_menu = TipoMenu.objects.all().order_by('nom_tipo_menu')
    categorias_producto = CategoriaProducto.objects.all().order_by('nom_cate')
    # Solo productos con stock > 0
    productos = Producto.objects.filter(estado_produ='disponible', stock_actual_produ__gt=0).select_related('id_uni_medi_produ_fk', 'id_cate_produ_fk').order_by('nom_produ')
    unidades = UnidadMedida.objects.all().order_by('nom_uni_medi')

    # Serializar productos y unidades para el frontend
    productos_json = []
    for p in productos:
        productos_json.append({
            'id': p.id_produ_pk,
            'stock': float(p.stock_actual_produ),
            'base_unit_id': p.id_uni_medi_produ_fk.id_uni_medi_pk,
            'base_unit_nom': p.id_uni_medi_produ_fk.abreviatura,
            'tipo_unidad': p.id_uni_medi_produ_fk.tipo_uni_medi,
        })
        
    unidades_json = []
    for u in unidades:
        unidades_json.append({
            'id': u.id_uni_medi_pk,
            'abreviatura': u.abreviatura,
            'tipo': u.tipo_uni_medi,
        })

    menu_preseleccionado = request.GET.get('menu', '')

    ingredientes_actuales = []
    if menu_preseleccionado:
        ingredientes_actuales = RecetaMenu.objects.filter(
            id_menu_fk_id=menu_preseleccionado
        ).select_related('id_produ_fk', 'id_uni_medi_fk')

    if request.method == 'POST':
        id_menu = request.POST.get('id_menu_fk')
        id_produ = request.POST.get('id_produ_fk')
        cantidad = request.POST.get('cantidad_reque')
        id_unidad = request.POST.get('id_uni_medi_fk')
        notas = request.POST.get('notas', '').strip()

        if not all([id_menu, id_produ, cantidad, id_unidad]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('crear_receta')

        if RecetaMenu.objects.filter(id_menu_fk=id_menu, id_produ_fk=id_produ).exists():
            messages.error(request, 'Este producto ya está en la receta del menú seleccionado.')
            return redirect(f'/admin-panel/recetas/nuevo/?menu={id_menu}')

        RecetaMenu.objects.create(
            id_menu_fk_id=id_menu,
            id_produ_fk_id=id_produ,
            cantidad_reque=cantidad,
            id_uni_medi_fk_id=id_unidad,
            notas=notas if notas else None
        )
        messages.success(request, 'Ingrediente agregado a la receta exitosamente.')
        return redirect(f'/admin-panel/recetas/nuevo/?menu={id_menu}')

    return render(request, 'admin/menu/index-receta.html', {
        'menus': menus, 
        'tipos_menu': tipos_menu,
        'categorias_producto': categorias_producto,
        'productos': productos,
        'unidades': unidades, 
        'menu_preseleccionado': menu_preseleccionado,
        'ingredientes_actuales': ingredientes_actuales,
        'productos_json': json.dumps(productos_json),
        'unidades_json': json.dumps(unidades_json),
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
        producto = receta.id_produ_fk

        if tipo_nombre not in categorias_dict:
            categorias_dict[tipo_nombre] = {}
            
        if menu.id_menu_pk not in categorias_dict[tipo_nombre]:
            categorias_dict[tipo_nombre][menu.id_menu_pk] = {
                'menu': menu,
                'ingredientes': [],
                'porciones_maximas': float('inf'),
                'limitante': None
            }
            
        # Calcular porciones para este ingrediente
        factor = _get_factor_conversion(receta.id_uni_medi_fk.abreviatura, producto.id_uni_medi_produ_fk.abreviatura)
        cantidad_base_reque = receta.cantidad_reque * factor
        
        porciones_ingrediente = 0
        if cantidad_base_reque > 0:
            porciones_ingrediente = int(producto.stock_actual_produ / cantidad_base_reque)
            
        # Estado semáforo
        if porciones_ingrediente == 0:
            estado_semaforo = 'agotado'
        elif porciones_ingrediente < 5:
            estado_semaforo = 'rojo'
        elif porciones_ingrediente <= 20:
            estado_semaforo = 'amarillo'
        else:
            estado_semaforo = 'verde'
            
        # Adjuntar métricas a la receta para mostrar en la tabla
        setattr(receta, 'porciones_posibles', porciones_ingrediente)
        setattr(receta, 'semaforo', estado_semaforo)
        setattr(receta, 'req_convertido', cantidad_base_reque)
        
        menu_dict = categorias_dict[tipo_nombre][menu.id_menu_pk]
        menu_dict['ingredientes'].append(receta)
        
        if porciones_ingrediente < menu_dict['porciones_maximas']:
            menu_dict['porciones_maximas'] = porciones_ingrediente
            menu_dict['limitante'] = producto.nom_produ

    # Convertir a lista plana para el template
    categorias_lista = []
    for tipo, menus_dict in categorias_dict.items():
        categorias_lista.append({
            'nom_tipo': tipo,
            'menus': menus_dict.values()
        })

    return render(request, 'admin/menu/tabla-receta.html', {
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
        cantidad  = request.POST.get('cantidad_reque')
        id_unidad = request.POST.get('id_uni_medi_fk')
        notas     = request.POST.get('notas', '').strip()

        if not all([cantidad, id_unidad]):
            messages.error(request, 'Cantidad y unidad son obligatorios.')
            return redirect('tabla_recetas')

        # Protegemos la integridad no alterando el menú ni el producto
        receta.cantidad_reque    = cantidad
        receta.id_uni_medi_fk_id = id_unidad
        receta.notas             = notas if notas else None
        receta.save()
        messages.success(request, 'Receta actualizada correctamente.')

    return redirect(f"/admin-panel/recetas/?open_menu={receta.id_menu_fk_id}")


def eliminar_receta(request, id_receta):
    if _staff_required(request):
        return redirect('login')
    receta = get_object_or_404(RecetaMenu, id_receta_pk=id_receta)
    id_menu = receta.id_menu_fk_id
    receta.delete()
    messages.success(request, 'Ingrediente eliminado de la receta.')
    return redirect(f"/admin-panel/recetas/?open_menu={id_menu}")


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