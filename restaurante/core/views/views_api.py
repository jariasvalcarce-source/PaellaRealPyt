# views_api.py
import csv
import io
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from ..models import Menu, RecetaMenu, Producto, Proveedor, UnidadMedida, CategoriaProducto, Pedido, DetallePedidoMenu, Cliente, TipoMenu, Empleado


def verificar_stock_menu(request, menu_id):
    """GET · Verifica stock de ingredientes de un menú."""
    try:
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
            stock = prod.stock_actual_produ
            if stock < receta.cantidad_reque:
                bajos.append({
                    'ingrediente':  prod.nom_produ,
                    'stock_actual': float(stock),
                    'requerido':    float(receta.cantidad_reque),
                    'unidad':       receta.id_uni_medi_fk.abreviatura,
                })

        if bajos:
            nombres = ', '.join(i['ingrediente'] for i in bajos[:3])
            return JsonResponse({
                'disponible': True, 'tiene_receta': True,
                'advertencia': True, 'ingredientes_bajos': bajos,
                'mensaje': (
                    f'Stock bajo en: {nombres}. '
                    f'Tu pedido se procesará en cuanto tengamos disponibilidad.'
                ),
            })

        return JsonResponse({
            'disponible': True, 'tiene_receta': True,
            'advertencia': False, 'ingredientes_bajos': [],
            'mensaje': 'Stock suficiente.',
        })

    except Exception as e:
        return JsonResponse({
            'disponible': True, 'advertencia': False,
            'mensaje': 'No se pudo verificar el stock.', 'error': str(e),
        })


def _resolve_foreign_key(model, value):
    if value is None:
        return None
    try:
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            return model.objects.get(pk=int(value))
    except model.DoesNotExist:
        pass

    lookup_fields = {
        Proveedor: ['nom_provee', 'correo_provee'],
        UnidadMedida: ['nom_uni_medi', 'abreviatura'],
        CategoriaProducto: ['nom_cate'],
    }.get(model, [])

    for field in lookup_fields:
        kwargs = {f'{field}__iexact': value}
        obj = model.objects.filter(**kwargs).first()
        if obj:
            return obj

    raise ValueError(f'No se encontró {model.__name__} para valor: {value}')


def _parse_producto_item(item):
    required = [
        'nom_produ', 'stock_actual_produ', 'stock_minimo_produ',
        'fecha_venci_produ', 'precio_uni_produ', 'des_produ',
        'estado_produ', 'id_provee_produ_fk', 'id_uni_medi_produ_fk',
        'id_cate_produ_fk'
    ]
    missing = [field for field in required if field not in item or item[field] in [None, '']]
    if missing:
        raise ValueError(f'Faltan campos obligatorios: {", ".join(missing)}')

    proveedor = _resolve_foreign_key(Proveedor, item['id_provee_produ_fk'])
    unidad = _resolve_foreign_key(UnidadMedida, item['id_uni_medi_produ_fk'])
    categoria = _resolve_foreign_key(CategoriaProducto, item['id_cate_produ_fk'])

    return {
        'nom_produ': item['nom_produ'],
        'stock_actual_produ': item['stock_actual_produ'],
        'stock_minimo_produ': item['stock_minimo_produ'],
        'fecha_venci_produ': item['fecha_venci_produ'],
        'precio_uni_produ': item['precio_uni_produ'],
        'des_produ': item['des_produ'],
        'estado_produ': item['estado_produ'],
        'id_provee_produ_fk': proveedor,
        'id_uni_medi_produ_fk': unidad,
        'id_cate_produ_fk': categoria,
    }


@csrf_exempt
def listar_productos_api(request):
    if request.method != 'GET':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)

    productos = Producto.objects.select_related(
        'id_provee_produ_fk', 'id_uni_medi_produ_fk', 'id_cate_produ_fk'
    ).all()

    data = [
        {
            'id': p.id_produ_pk,
            'nombre': p.nom_produ,
            'stock_actual': float(p.stock_actual_produ),
            'stock_minimo': float(p.stock_minimo_produ),
            'fecha_vencimiento': p.fecha_venci_produ.isoformat(),
            'precio_unitario': float(p.precio_uni_produ),
            'descripcion': p.des_produ,
            'estado': p.estado_produ,
            'proveedor': p.id_provee_produ_fk.nom_provee,
            'unidad_medida': p.id_uni_medi_produ_fk.abreviatura,
            'categoria': p.id_cate_produ_fk.nom_cate,
        }
        for p in productos
    ]

    return JsonResponse({'ok': True, 'productos': data})


@csrf_exempt
def bulk_upload_productos_api(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body.decode('utf-8'))
            items = payload if isinstance(payload, list) else payload.get('productos', [])
        elif 'multipart/form-data' in request.content_type and request.FILES.get('file'):
            file = request.FILES['file']
            csv_file = io.TextIOWrapper(file.file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
            items = [row for row in reader]
        else:
            return JsonResponse({'ok': False, 'error': 'Contenido no válido. Usa JSON o envía un archivo CSV.'}, status=400)

        if not isinstance(items, list) or not items:
            return JsonResponse({'ok': False, 'error': 'Debe enviar una lista de productos.'}, status=400)

        resultados = []
        for item in items:
            try:
                parsed = _parse_producto_item(item)
                producto = Producto.objects.filter(nom_produ__iexact=parsed['nom_produ']).first()
                if producto:
                    for key, value in parsed.items():
                        setattr(producto, key, value)
                    producto.save()
                    resultados.append({'producto': producto.nom_produ, 'accion': 'actualizado'})
                else:
                    producto = Producto.objects.create(**parsed)
                    resultados.append({'producto': producto.nom_produ, 'accion': 'creado'})
            except Exception as item_err:
                resultados.append({'producto': item.get('nom_produ', 'sin_nombre'), 'error': str(item_err)})

        return JsonResponse({'ok': True, 'resultados': resultados})
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'JSON inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@csrf_exempt
def listar_menus_api(request):
    if request.method != 'GET':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)

    menus = Menu.objects.select_related('id_tipo_menu_fk').filter(disponible_menu=True).all()

    data = [
        {
            'id': m.id_menu_pk,
            'nombre': m.nom_menu,
            'precio': float(m.precio_menu),
            'descripcion': m.des_menu,
            'tipo': m.id_tipo_menu_fk.nom_tipo_menu,
            'disponible': m.disponible_menu,
        }
        for m in menus
    ]

    return JsonResponse({'ok': True, 'menus': data})


@csrf_exempt
def bulk_upload_menus_api(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body.decode('utf-8'))
            items = payload if isinstance(payload, list) else payload.get('menus', [])
        elif 'multipart/form-data' in request.content_type and request.FILES.get('file'):
            file = request.FILES['file']
            csv_file = io.TextIOWrapper(file.file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
            items = [row for row in reader]
        else:
            return JsonResponse({'ok': False, 'error': 'Contenido no válido. Usa JSON o envía un archivo CSV.'}, status=400)

        if not isinstance(items, list) or not items:
            return JsonResponse({'ok': False, 'error': 'Debe enviar una lista de menús.'}, status=400)

        resultados = []
        for item in items:
            try:
                required = ['nom_menu', 'precio_menu', 'des_menu', 'id_tipo_menu_fk']
                missing = [field for field in required if field not in item or item[field] in [None, '']]
                if missing:
                    raise ValueError(f'Faltan campos obligatorios: {", ".join(missing)}')

                tipo_menu = _resolve_foreign_key(TipoMenu, item['id_tipo_menu_fk'])

                menu_data = {
                    'nom_menu': item['nom_menu'],
                    'precio_menu': item['precio_menu'],
                    'des_menu': item['des_menu'],
                    'id_tipo_menu_fk': tipo_menu,
                    'disponible_menu': item.get('disponible_menu', True),
                }

                menu = Menu.objects.filter(nom_menu__iexact=menu_data['nom_menu']).first()
                if menu:
                    for key, value in menu_data.items():
                        setattr(menu, key, value)
                    menu.save()
                    resultados.append({'menu': menu.nom_menu, 'accion': 'actualizado'})
                else:
                    menu = Menu.objects.create(**menu_data)
                    resultados.append({'menu': menu.nom_menu, 'accion': 'creado'})
            except Exception as item_err:
                resultados.append({'menu': item.get('nom_menu', 'sin_nombre'), 'error': str(item_err)})

        return JsonResponse({'ok': True, 'resultados': resultados})
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'JSON inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@csrf_exempt
def listar_pedidos_api(request):
    if request.method != 'GET':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)

    pedidos = Pedido.objects.select_related('id_clien_pedido_fk', 'id_emple_pedido_fk').all()

    data = [
        {
            'id': p.id_pedido_pk,
            'fecha': p.fecha_pedido.isoformat(),
            'estado': p.estado_pedido,
            'tipo': p.tipo_pedido,
            'total': float(p.total_pedido),
            'cliente': p.id_clien_pedido_fk.nom_clien,
            'empleado': p.id_emple_pedido_fk.nom_emple if p.id_emple_pedido_fk else None,
        }
        for p in pedidos
    ]

    return JsonResponse({'ok': True, 'pedidos': data})


@csrf_exempt
def bulk_upload_pedidos_api(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)

    try:
        if request.content_type == 'application/json':
            payload = json.loads(request.body.decode('utf-8'))
            items = payload if isinstance(payload, list) else payload.get('pedidos', [])
        elif 'multipart/form-data' in request.content_type and request.FILES.get('file'):
            file = request.FILES['file']
            csv_file = io.TextIOWrapper(file.file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
            items = [row for row in reader]
        else:
            return JsonResponse({'ok': False, 'error': 'Contenido no válido. Usa JSON o envía un archivo CSV.'}, status=400)

        if not isinstance(items, list) or not items:
            return JsonResponse({'ok': False, 'error': 'Debe enviar una lista de pedidos.'}, status=400)

        resultados = []
        for item in items:
            try:
                required = ['estado_pedido', 'tipo_pedido', 'total_pedido', 'id_clien_pedido_fk']
                missing = [field for field in required if field not in item or item[field] in [None, '']]
                if missing:
                    raise ValueError(f'Faltan campos obligatorios: {", ".join(missing)}')

                cliente = _resolve_foreign_key(Cliente, item['id_clien_pedido_fk'])
                empleado = _resolve_foreign_key(Empleado, item.get('id_emple_pedido_fk')) if item.get('id_emple_pedido_fk') else None

                pedido_data = {
                    'estado_pedido': item['estado_pedido'],
                    'tipo_pedido': item['tipo_pedido'],
                    'total_pedido': item['total_pedido'],
                    'notas_pedido': item.get('notas_pedido', ''),
                    'id_clien_pedido_fk': cliente,
                    'id_emple_pedido_fk': empleado,
                }

                pedido = Pedido.objects.create(**pedido_data)
                resultados.append({'pedido': pedido.id_pedido_pk, 'accion': 'creado'})
            except Exception as item_err:
                resultados.append({'pedido': item.get('id_pedido_pk', 'sin_id'), 'error': str(item_err)})

        return JsonResponse({'ok': True, 'resultados': resultados})
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'JSON inválido.'}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
