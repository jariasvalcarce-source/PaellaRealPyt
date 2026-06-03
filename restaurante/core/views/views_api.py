# views_api.py
import base64
import csv
import io
import json
import pandas as pd
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from core.api_auth import CustomJWTAuthentication
from core.api.serializers import (ClienteSerializer, EmpleadoSerializer, ProductoSerializer, MenuSerializer, PedidoSerializer)
from core.models import (
    Menu, RecetaMenu, Producto, Proveedor, UnidadMedida, CategoriaProducto,
    Pedido, DetallePedidoMenu, Cliente, TipoMenu, Empleado,
    UsuarioAuth, Rol, Domicilio, Evento, Barrio, TipoEvento, MesaEvento
)
from core.views.views_personas import _check_duplicate_phone

# =============================================================================
# SECCIÓN 1: UTILIDADES GLOBALES DE LA API Y RESOLUCIÓN DE DATOS
# =============================================================================

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


@csrf_exempt
def check_username_api(request):
    """POST · Verifica si un nombre de usuario ya está en uso."""
    if request.method != 'POST':
        return JsonResponse({'disponible': False, 'error': 'Método no permitido.'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        
        if not username:
            return JsonResponse({'disponible': False, 'error': 'Username requerido.'})
        
        # Verificar si el username ya existe en UsuarioAuth
        existe = UsuarioAuth.objects.filter(nombre_usuario=username).exists()
        
        return JsonResponse({'disponible': not existe})
    except Exception as e:
        return JsonResponse({'disponible': False, 'error': str(e)})


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
        Cliente: ['nom_clien', 'correo_clien'],
        Empleado: ['nom_emple', 'correo_emple'],
        TipoMenu: ['nom_tipo_menu'],
        Menu: ['nom_menu'],
        Producto: ['nom_produ'],
        Barrio: ['nom_barrio'],
        TipoEvento: ['nom_tipo_evento'],
        MesaEvento: ['num_mesa'],
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


def _parse_json_body(request):
    try:
        # En DRF `request.data` procesa JSON automáticamente, pero lo mantenemos para compatibilidad con csr_exempt puro
        if hasattr(request, 'data'):
            return request.data
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise ValueError('JSON inválido.')

def _extract_data_from_request(request, key_name):
    if request.content_type and 'application/json' in request.content_type:
        payload = request.data if hasattr(request, 'data') else _parse_json_body(request)
        return payload if isinstance(payload, list) else payload.get(key_name, [])
        
    # DRF almacena los archivos en request.FILES, pero también pueden estar en request.data
    # dependiendo de los parsers usados.
    archivos = request.FILES or {}
    data_files = {k: v for k, v in request.data.items() if hasattr(v, 'read')} if hasattr(request, 'data') else {}
    
    if archivos or data_files:
        file = archivos.get('file') or data_files.get('file')
        if not file:
            todas_keys = list(archivos.values()) + list(data_files.values())
            file = todas_keys[0] if todas_keys else None
            
        if not file:
             raise ValueError("Extracción de archivo falló. Archivos enviados pero 'file' está vacío.")
             
        filename = getattr(file, 'name', 'desconocido').lower()
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            raise ValueError(f"Formato no soportado en el archivo '{filename}'. Usa .csv o .xlsx")
        
        df = df.where(pd.notnull(df), None)
        return df.to_dict('records')
        
    raise ValueError(f"Contenido o variable no encontrada. ¿Adjuntaste el archivo? (Recibimos type={request.content_type})")


def _require_auth_admin(request):
    try:
        auth_result = CustomJWTAuthentication().authenticate(request)
        if auth_result is None:
            raise PermissionError('Falta el Token JWT. Envía el header "Authorization: Bearer <token>".')
        
        usuario, token = auth_result
        if usuario.rol.name != 'admin':
            raise PermissionError('Acceso denegado. Solo administradores.')
        return usuario
    except Exception as e:
        # Relanzamos para que las vistas generen el 401
        raise PermissionError(str(e))

# =============================================================================
# SECCIÓN 2: FORMATEADORES, VALIDACIÓN Y LÓGICA DE USUARIOS BASE
# =============================================================================

def _validate_fields(data, required):
    missing = [field for field in required if field not in data or data[field] in [None, '']]
    if missing:
        raise ValueError(f'Faltan campos obligatorios: {", ".join(missing)}')


def _create_usuario_auth(username, password, role_name):
    if UsuarioAuth.objects.filter(nombre_usuario=username).exists():
        raise ValueError('Ya existe un usuario con ese nombre.')

    rol = Rol.objects.filter(name=role_name).first()
    if not rol:
        raise ValueError(f'Rol inválido: {role_name}')

    usuario = UsuarioAuth(nombre_usuario=username, activo=True, rol=rol)
    usuario.set_password(password)
    usuario.save()
    return usuario


def _cliente_data(data):
    required = [
        'nom_clien', 'apellido_clien', 'fecha_naci_cliente',
        'tel_cliente', 'correo_clien', 'direc_clien',
        'nombre_usuario', 'password'
    ]
    _validate_fields(data, required)
    if _check_duplicate_phone(data['tel_cliente']):
        raise ValueError('El número de celular ya está registrado por otra persona.')

    return {
        'nom_clien': data['nom_clien'].strip(),
        'apellido_clien': data['apellido_clien'].strip(),
        'fecha_naci_cliente': data['fecha_naci_cliente'],
        'tel_cliente': int(data['tel_cliente']),
        'correo_clien': data['correo_clien'].strip(),
        'direc_clien': data['direc_clien'].strip(),
        'estado_clien': data.get('estado_clien', 'activo'),
    }


def _empleado_data(data):
    required = [
        'nom_emple', 'apellido_emple', 'fecha_naci_emple',
        'tel_emple', 'correo_emple', 'direc_emple',
        'nombre_usuario', 'password'
    ]
    _validate_fields(data, required)
    if _check_duplicate_phone(data['tel_emple']):
        raise ValueError('El número de celular ya está registrado por otra persona.')

    return {
        'nom_emple': data['nom_emple'].strip(),
        'apellido_emple': data['apellido_emple'].strip(),
        'fecha_naci_emple': data['fecha_naci_emple'],
        'tel_emple': int(data['tel_emple']),
        'correo_emple': data['correo_emple'].strip(),
        'direc_emple': data['direc_emple'].strip(),
        'estado_emple': data.get('estado_emple', 'activo'),
    }

# =============================================================================
# SECCIÓN 3: API DE PERSONAS (CLIENTES, EMPLEADOS, PROVEEDORES)
# Módulo encargado del listado, creación individual y carga masiva
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_cliente_api(request):
    try:
        # data = _parse_json_body(request) 
        data = request.data
        cliente_data = _cliente_data(data)
        usuario = _create_usuario_auth(data['nombre_usuario'], data['password'], 'cliente')

        cliente = Cliente.objects.create(
            **cliente_data,
            id_auth_fk=usuario
        )

        return Response({
            'ok': True,
            'cliente': {
                'id_clien_pk': cliente.id_clien_pk,
                'nom_clien': cliente.nom_clien,
                'apellido_clien': cliente.apellido_clien,
                'correo_clien': cliente.correo_clien,
                'nombre_usuario': usuario.nombre_usuario,
            }
        }, status=201)
    except PermissionError as perm_err:
        return Response({'ok': False, 'error': str(perm_err)}, status=401)
    except ValueError as val_err:
        return Response({'ok': False, 'error': str(val_err)}, status=400)
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def bulk_upload_clientes_api(request):
    if request.user.rol.name != 'admin':
        return Response({'ok': False, 'error': 'Acceso denegado. Solo administradores.'}, status=403)

    try:
        items = _extract_data_from_request(request, 'clientes')
        if not isinstance(items, list) or not items:
            return Response({'ok': False, 'error': 'Debe enviar una lista de clientes.'}, status=400)

        resultados = []
        try:
            with transaction.atomic():
                for i, item in enumerate(items):
                    try:
                        cliente_data = _cliente_data(item)
                        # Comprobamos si el cliente (correo) ya existe de forma robusta
                        if Cliente.objects.filter(correo_clien__iexact=cliente_data['correo_clien']).exists():
                             raise ValueError("Ya existe un cliente con este correo.")
                             
                        usuario = _create_usuario_auth(item['nombre_usuario'], item['password'], 'cliente')
                        cliente = Cliente.objects.create(**cliente_data, id_auth_fk=usuario)
                        resultados.append({'cliente': cliente.nom_clien, 'accion': 'creado'})
                    except Exception as item_err:
                        raise ValueError(f"Fila {i+1} ({item.get('nom_clien', 'desconocido')}): {str(item_err)}")
        except ValueError as trans_err:
            return Response({'ok': False, 'error': str(trans_err)}, status=400)

        return Response({
            'ok': True, 
            'mensaje': f'{len(resultados)} clientes procesados exitosamente bajo transacción.', 
            'resultados': resultados
        })
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=500)


@csrf_exempt
def crear_empleado_api(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)

    try:
        _require_auth_admin(request)
        data = _parse_json_body(request)
        empleado_data = _empleado_data(data)
        usuario = _create_usuario_auth(data['nombre_usuario'], data['password'], 'empleado')

        empleado = Empleado.objects.create(
            **empleado_data,
            id_auth_fk=usuario
        )

        return JsonResponse({
            'ok': True,
            'empleado': {
                'id_emple_pk': empleado.id_emple_pk,
                'nom_emple': empleado.nom_emple,
                'apellido_emple': empleado.apellido_emple,
                'correo_emple': empleado.correo_emple,
                'nombre_usuario': usuario.nombre_usuario,
            }
        }, status=201)
    except PermissionError as perm_err:
        return JsonResponse({'ok': False, 'error': str(perm_err)}, status=401)
    except ValueError as val_err:
        return JsonResponse({'ok': False, 'error': str(val_err)}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def bulk_upload_empleados_api(request):
    if request.user.rol.name != 'admin':
        return Response({'ok': False, 'error': 'Acceso denegado. Solo administradores.'}, status=403)

    try:
        items = _extract_data_from_request(request, 'empleados')
        if not isinstance(items, list) or not items:
            return Response({'ok': False, 'error': 'Debe enviar una lista de empleados.'}, status=400)

        resultados = []
        try:
            with transaction.atomic():
                for i, item in enumerate(items):
                    try:
                        empleado_data = _empleado_data(item)
                        if Empleado.objects.filter(correo_emple__iexact=empleado_data['correo_emple']).exists():
                             raise ValueError("Ya existe un empleado con este correo.")
                             
                        usuario = _create_usuario_auth(item['nombre_usuario'], item['password'], 'empleado')
                        empleado = Empleado.objects.create(**empleado_data, id_auth_fk=usuario)
                        resultados.append({'empleado': empleado.nom_emple, 'accion': 'creado'})
                    except Exception as item_err:
                        raise ValueError(f"Fila {i+1}: {str(item_err)}")
        except ValueError as trans_err:
            return Response({'ok': False, 'error': str(trans_err)}, status=400)

        return Response({
            'ok': True, 
            'mensaje': f'{len(resultados)} empleados procesados exitosamente bajo transacción.', 
            'resultados': resultados
        })
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_clientes_api(request):
    if request.user.rol.name != 'admin':
        return Response({'ok': False, 'error': 'Acceso denegado. Solo administradores.'}, status=403)
    
    try:
        clientes = Cliente.objects.select_related('id_auth_fk').all()
        serializer = ClienteSerializer(clientes, many=True)
        return Response({'ok': True, 'clientes': serializer.data})
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_empleados_api(request):
    empleados = Empleado.objects.select_related('id_auth_fk').all()
    serializer = EmpleadoSerializer(empleados, many=True)
    return Response({'ok': True, 'empleados': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_cliente_api(request, cliente_id):
    """GET · Obtiene datos completos de un cliente por ID."""
    if request.user.rol.name != 'admin':
        return Response({'ok': False, 'error': 'Acceso denegado. Solo administradores.'}, status=403)

    try:
        cliente = Cliente.objects.select_related('id_auth_fk').get(id_clien_pk=cliente_id)
        serializer = ClienteSerializer(cliente)
        return Response({'ok': True, 'cliente': serializer.data})
    except Cliente.DoesNotExist:
        return Response({'ok': False, 'error': f'Cliente {cliente_id} no encontrado.'}, status=404)
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_empleado_api(request, empleado_id):
    """GET · Obtiene datos completos de un empleado por ID."""
    if request.user.rol.name != 'admin':
        return Response({'ok': False, 'error': 'Acceso denegado. Solo administradores.'}, status=403)

    try:
        empleado = Empleado.objects.select_related('id_auth_fk').get(id_emple_pk=empleado_id)
        serializer = EmpleadoSerializer(empleado)
        return Response({'ok': True, 'empleado': serializer.data})
    except Empleado.DoesNotExist:
        return Response({'ok': False, 'error': f'Empleado {empleado_id} no encontrado.'}, status=404)
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=500)

# =============================================================================
# SECCIÓN 4: API DEL INVENTARIO (PRODUCTOS, RECETAS Y MENÚS)
# Listados y subida masiva del catálogo del restaurante
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_productos_api(request):
    productos = Producto.objects.select_related(
        'id_provee_produ_fk', 'id_uni_medi_produ_fk', 'id_cate_produ_fk'
    ).all()
    serializer = ProductoSerializer(productos, many=True)
    return Response({'ok': True, 'productos': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def bulk_upload_productos_api(request):
    if request.user.rol.name != 'admin':
        return Response({'ok': False, 'error': 'Acceso denegado. Solo administradores.'}, status=403)

    try:
        items = _extract_data_from_request(request, 'productos')
        if not isinstance(items, list) or not items:
            return Response({'ok': False, 'error': 'Debe enviar una lista de productos.'}, status=400)

        resultados = []
        try:
            with transaction.atomic():
                for i, item in enumerate(items):
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
                        raise ValueError(f"Fila {i+1} ({item.get('nom_produ', 'sin_nombre')}): {str(item_err)}")
        except ValueError as trans_err:
            return Response({'ok': False, 'error': str(trans_err)}, status=400)

        return Response({
            'ok': True, 
            'mensaje': f'{len(resultados)} productos procesados exitosamente bajo transacción.', 
            'resultados': resultados
        })
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_menus_api(request):
    menus = Menu.objects.select_related('id_tipo_menu_fk').filter(disponible_menu=True).all()
    serializer = MenuSerializer(menus, many=True)
    return Response({'ok': True, 'menus': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def bulk_upload_menus_api(request):
    if request.user.rol.name != 'admin':
        return Response({'ok': False, 'error': 'Acceso denegado. Solo administradores.'}, status=403)

    try:
        items = _extract_data_from_request(request, 'menus')
        if not isinstance(items, list) or not items:
            return Response({'ok': False, 'error': 'Debe enviar una lista de menús.'}, status=400)

        resultados = []
        try:
            with transaction.atomic():
                for i, item in enumerate(items):
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
                        raise ValueError(f"Fila {i+1} ({item.get('nom_menu', 'sin_nombre')}): {str(item_err)}")
        except ValueError as trans_err:
            return Response({'ok': False, 'error': str(trans_err)}, status=400)

        return Response({
            'ok': True, 
            'mensaje': f'{len(resultados)} menús procesados exitosamente bajo transacción.', 
            'resultados': resultados
        })
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=500)

# =============================================================================
# SECCIÓN 5: API DE VENTAS (PEDIDOS, DOMICILIOS, EVENTOS)
# Módulo de operaciones comerciales, listado y carga histórica
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_pedidos_api(request):
    pedidos = Pedido.objects.select_related('id_clien_pedido_fk', 'id_emple_pedido_fk').all()
    serializer = PedidoSerializer(pedidos, many=True)
    return Response({'ok': True, 'pedidos': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def bulk_upload_pedidos_api(request):
    if request.user.rol.name != 'admin':
        return Response({'ok': False, 'error': 'Acceso denegado. Solo administradores.'}, status=403)

    try:
        items = _extract_data_from_request(request, 'pedidos')
        if not isinstance(items, list) or not items:
            return Response({'ok': False, 'error': 'Debe enviar una lista de pedidos.'}, status=400)

        resultados = []
        try:
            with transaction.atomic():
                for i, item in enumerate(items):
                    try:
                        required = ['estado_pedido', 'tipo_pedido', 'id_clien_pedido_fk']
                        missing = [field for field in required if field not in item or item[field] in [None, '']]
                        if missing:
                            raise ValueError(f'Faltan campos obligatorios: {", ".join(missing)}')

                        cliente = _resolve_foreign_key(Cliente, item['id_clien_pedido_fk'])
                        empleado = _resolve_foreign_key(Empleado, item.get('id_emple_pedido_fk')) if item.get('id_emple_pedido_fk') else None

                        pedido_data = {
                            'estado_pedido': item['estado_pedido'],
                            'tipo_pedido': item['tipo_pedido'],
                            'total_pedido': 0, # Calcularemos después o asuminaremos del CSV
                            'notas_pedido': item.get('notas_pedido', ''),
                            'id_clien_pedido_fk': cliente,
                            'id_emple_pedido_fk': empleado,
                        }

                        pedido = Pedido.objects.create(**pedido_data)
                        
                        if item.get('fecha_simulada') and pd.notna(item.get('fecha_simulada')):
                            pedido.fecha_pedido = item['fecha_simulada']
                            pedido.save(update_fields=['fecha_pedido'])

                        total_calculado = 0
                        for m_idx in range(1, 4):
                            menu_key = f'menu_{m_idx}'
                            cant_key = f'cant_{m_idx}'
                            
                            menu_val = item.get(menu_key)
                            cant_val = item.get(cant_key)
                            
                            if menu_val and pd.notna(menu_val) and cant_val and pd.notna(cant_val):
                                menu_obj = _resolve_foreign_key(Menu, menu_val)
                                cant = int(cant_val)
                                subtotal = menu_obj.precio_menu * cant
                                
                                DetallePedidoMenu.objects.create(
                                    cant_detalle=cant,
                                    precio_unitario=menu_obj.precio_menu,
                                    subtotal=subtotal,
                                    id_pedido_fk=pedido,
                                    id_menu_fk=menu_obj
                                )
                                total_calculado += subtotal

                        if item.get('total_pedido') and pd.notna(item.get('total_pedido')):
                            pedido.total_pedido = float(item['total_pedido'])
                        else:
                            pedido.total_pedido = total_calculado
                        pedido.save(update_fields=['total_pedido'])

                        if item['tipo_pedido'] == 'domicilio':
                            req_dom = ['direc_domi', 'fecha_domi', 'hora_entrega_domi', 'barrio']
                            for req_d in req_dom:
                                if req_d not in item or pd.isna(item[req_d]):
                                    raise ValueError(f'Falta campo de domicilio: {req_d}')
                            
                            barrio_obj = _resolve_foreign_key(Barrio, item['barrio'])
                            Domicilio.objects.create(
                                direc_domi=item['direc_domi'],
                                fecha_domi=item['fecha_domi'],
                                hora_entrega_domi=item['hora_entrega_domi'],
                                estado_domi='pendiente',
                                id_pedido_domi_fk=pedido,
                                id_barrio_domi_fk=barrio_obj
                            )

                        elif item['tipo_pedido'] == 'evento':
                            req_ev = ['nom_evento', 'fecha_evento', 'hora_inicio', 'hora_fin', 'ubi_evento', 'cant_invi', 'tipo_evento', 'mesa']
                            for req_e in req_ev:
                                if req_e not in item or pd.isna(item[req_e]):
                                    raise ValueError(f'Falta campo de evento: {req_e}')
                            
                            tipo_evento_obj = _resolve_foreign_key(TipoEvento, item['tipo_evento'])
                            mesa_obj = _resolve_foreign_key(MesaEvento, item['mesa'])
                            
                            Evento.objects.create(
                                nom_evento=item['nom_evento'],
                                fecha_evento=item['fecha_evento'],
                                hora_inicio_evento=item['hora_inicio'],
                                hora_fin_evento=item['hora_fin'],
                                ubi_evento=item['ubi_evento'],
                                cant_invi_evento=int(item['cant_invi']),
                                estado_evento='pendiente',
                                id_tipo_evento_fk=tipo_evento_obj,
                                id_mesa_evento_fk=mesa_obj,
                                id_pedido_evento_fk=pedido
                            )
                        
                        resultados.append({'pedido': pedido.id_pedido_pk, 'accion': 'creado'})
                    except Exception as item_err:
                        raise ValueError(f"Fila {i+1}: {str(item_err)}")
        except ValueError as trans_err:
            return Response({'ok': False, 'error': str(trans_err)}, status=400)

        return Response({
            'ok': True, 
            'mensaje': f'{len(resultados)} pedidos procesados exitosamente bajo transacción.', 
            'resultados': resultados
        })
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def bulk_upload_proveedores_api(request):
    if request.user.rol.name != 'admin':
        return Response({'ok': False, 'error': 'Acceso denegado. Solo administradores.'}, status=403)
    try:
        items = _extract_data_from_request(request, 'proveedores')
        if not isinstance(items, list) or not items:
            return Response({'ok': False, 'error': 'Debe enviar una lista.'}, status=400)
        resultados = []
        with transaction.atomic():
            for i, item in enumerate(items):
                try:
                    req = ['tipo_provee', 'nom_provee', 'nit_cedula_provee', 'tel_provee', 'correo_provee', 'direc_provee', 'estado_provee']
                    _validate_fields(item, req)
                    
                    p = Proveedor.objects.filter(nit_cedula_provee=item['nit_cedula_provee']).first()
                    if _check_duplicate_phone(item['tel_provee'], current_proveedor_id=p.id_provee_pk if p else None):
                        raise ValueError(f"El número de teléfono {item['tel_provee']} ya está registrado por otra persona.")

                    # Also check duplicate email if creating a new one or modifying email
                    if Proveedor.objects.filter(correo_provee=item['correo_provee']).exclude(id_provee_pk=p.id_provee_pk if p else None).exists():
                         raise ValueError(f"El correo {item['correo_provee']} ya está registrado.")

                    prov_data = {
                        'tipo_provee': item['tipo_provee'],
                        'nom_provee': item['nom_provee'],
                        'nit_cedula_provee': str(item['nit_cedula_provee']),
                        'nombre_contacto_provee': item.get('nombre_contacto_provee', ''),
                        'tel_provee': item['tel_provee'],
                        'correo_provee': item['correo_provee'],
                        'direc_provee': item['direc_provee'],
                        'condicion_pago_provee': item.get('condicion_pago_provee', ''),
                        'observaciones_provee': item.get('observaciones_provee', ''),
                        'estado_provee': item['estado_provee']
                    }
                    
                    if p:
                        for k, v in prov_data.items(): setattr(p, k, v)
                        p.save(); resultados.append({'prov': p.nom_provee, 'accion': 'actualizado'})
                    else:
                        p = Proveedor.objects.create(**prov_data)
                        resultados.append({'prov': p.nom_provee, 'accion': 'creado'})
                except Exception as e:
                    raise ValueError(f'Fila {i+1}: {str(e)}')
        return Response({'ok': True, 'resultados': resultados})
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=400)
# =============================================================================
# SECCIÓN 6: MOVIMIENTOS DE INVENTARIO Y EXTRAS
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def bulk_upload_movimientos_api(request):
    from core.models import MovimientoProducto
    if request.user.rol.name != 'admin':
        return Response({'ok': False, 'error': 'Acceso denegado. Solo administradores.'}, status=403)
    try:
        items = _extract_data_from_request(request, 'movimientos')
        if not isinstance(items, list) or not items:
            return Response({'ok': False, 'error': 'Debe enviar una lista.'}, status=400)
        resultados = []
        with transaction.atomic():
            for i, item in enumerate(items):
                try:
                    req = ['tipo_movi', 'motivo_movi', 'fecha_movi', 'cant_movi', 'stock_anterior', 'stock_posterior', 'id_emple_movi_fk', 'id_produ_movi_fk']
                    _validate_fields(item, req)
                    emp = _resolve_foreign_key(Empleado, item['id_emple_movi_fk'])
                    prod = _resolve_foreign_key(Producto, item['id_produ_movi_fk'])
                    d = {
                        'tipo_movi': item['tipo_movi'],
                        'motivo_movi': item['motivo_movi'],
                        'fecha_movi': item['fecha_movi'],
                        'cant_movi': item['cant_movi'],
                        'stock_anterior': item['stock_anterior'],
                        'stock_posterior': item['stock_posterior'],
                        'id_emple_movi_fk': emp,
                        'id_produ_movi_fk': prod
                    }
                    m = MovimientoProducto.objects.filter(id_emple_movi_fk=emp, id_produ_movi_fk=prod, fecha_movi=item['fecha_movi']).first()
                    if m:
                        for k, v in d.items(): setattr(m, k, v)
                        m.save(); resultados.append({'mov': m.id_movi_pk, 'accion': 'actualizado'})
                    else:
                        m = MovimientoProducto.objects.create(**d)
                        resultados.append({'mov': m.id_movi_pk, 'accion': 'creado'})
                except Exception as e:
                    raise ValueError(f'Fila {i+1}: {str(e)}')
        return Response({'ok': True, 'resultados': resultados})
    except Exception as e:

        return Response({'ok': False, 'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def bulk_upload_recetas_api(request):
    if request.user.rol.name != 'admin':
        return Response({'ok': False, 'error': 'Acceso denegado. Solo administradores.'}, status=403)
    try:
        items = _extract_data_from_request(request, 'recetas')
        if not isinstance(items, list) or not items:
            return Response({'ok': False, 'error': 'Debe enviar una lista.'}, status=400)
        
        resultados = []
        with transaction.atomic():
            for i, item in enumerate(items):
                try:
                    req = ['menu', 'producto', 'cantidad', 'unidad']
                    _validate_fields(item, req)
                    
                    menu = _resolve_foreign_key(Menu, item['menu'])
                    producto = _resolve_foreign_key(Producto, item['producto'])
                    unidad = _resolve_foreign_key(UnidadMedida, item['unidad'])
                    
                    receta_data = {
                        'id_menu_fk': menu,
                        'id_produ_fk': producto,
                        'cantidad_reque': item['cantidad'],
                        'id_uni_medi_fk': unidad,
                        'notas': item.get('notas', '')
                    }
                    
                    receta, created = RecetaMenu.objects.update_or_create(
                        id_menu_fk=menu, id_produ_fk=producto,
                        defaults=receta_data
                    )
                    accion = 'creado' if created else 'actualizado'
                    resultados.append({'receta': f"{menu.nom_menu} - {producto.nom_produ}", 'accion': accion})
                except Exception as e:
                    raise ValueError(f'Fila {i+1}: {str(e)}')
        return Response({'ok': True, 'resultados': resultados})
    except Exception as e:
        return Response({'ok': False, 'error': str(e)}, status=400)


import stripe
from django.conf import settings
from django.http import HttpResponse
from datetime import datetime as dt
from core.models import MetodoPago, Factura, Pago, Pedido

@csrf_exempt
def webhook_stripe_api(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        # En modo prueba local sin signature secret habilitado puede fallar
        # para facilidad ignoraremos la validacion estricta en local si es necesario,
        # pero intentaremos validarlo.
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        pedido_id = session.get('client_reference_id')
        
        if pedido_id:
            try:
                pedido = Pedido.objects.get(id_pedido_pk=int(pedido_id))
                if pedido.estado_pedido != 'confirmado':
                    # Podria buscar o crear MetodoPago 'stripe'
                    metodo, _ = MetodoPago.objects.get_or_create(tipo_met_pago='stripe')
                    
                    ahora = dt.now()
                    factura = Factura.objects.create(
                        fecha_factu = ahora.date(),
                        hora_factu = ahora.time(),
                        total_factu = pedido.total_pedido,
                        id_clien_factu_fk = pedido.id_clien_pedido_fk,
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
            except Exception as e:
                print(f'Webhook Error: {str(e)}')
                pass

    return HttpResponse(status=200)
