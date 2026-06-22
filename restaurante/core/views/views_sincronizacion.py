from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from ..models import Menu, Cliente, Favorito, CarritoItem, UsuarioAuth
import json

def get_cliente_global(request):
    if 'usuario_id' in request.session:
        try:
            usuario = UsuarioAuth.objects.get(id_auth_pk=request.session['usuario_id'])
            return Cliente.objects.get(id_auth_fk=usuario)
        except (UsuarioAuth.DoesNotExist, Cliente.DoesNotExist):
            return None
    return None

@require_POST
def toggle_favorito(request, menu_id):
    cliente = get_cliente_global(request)
    if not cliente:
        return JsonResponse({'status': 'error', 'message': 'Debes iniciar sesión.'}, status=401)
    
    menu = get_object_or_404(Menu, pk=menu_id)
    favorito, created = Favorito.objects.get_or_create(id_cliente_fk=cliente, id_menu_fk=menu)
    
    if not created:
        favorito.delete()
        accion = 'removido'
    else:
        accion = 'agregado'
        
    return badge_sincronizacion(request)

@require_POST
def agregar_carrito(request, menu_id):
    cliente = get_cliente_global(request)
    if not cliente:
        return JsonResponse({'status': 'error', 'message': 'Debes iniciar sesión.'}, status=401)
    
    try:
        data = json.loads(request.body)
        cantidad = int(data.get('cantidad', 1))
    except:
        cantidad = 1
        
    menu = get_object_or_404(Menu, pk=menu_id)

    if not menu.disponible_menu:
        return JsonResponse({
            'status': 'error', 
            'message': 'Actualmente no está disponible.'
        }, status=400)

    # Validar stock antes de agregar
    from core.models import RecetaMenu
    from core.utils import convertir_a_unidad_base
    from decimal import Decimal

    recetas = RecetaMenu.objects.select_related(
        'id_produ_fk', 'id_uni_medi_fk',
        'id_produ_fk__id_uni_medi_produ_fk'
    ).filter(id_menu_fk=menu)

    # Calcular cantidad futura en el carrito para verificar stock total
    try:
        item_existente = CarritoItem.objects.get(id_cliente_fk=cliente, id_menu_fk=menu)
        cantidad_futura = item_existente.cantidad + cantidad
    except CarritoItem.DoesNotExist:
        cantidad_futura = cantidad

    if recetas.exists():
        for receta in recetas:
            prod = receta.id_produ_fk
            stock = prod.stock_actual_produ
            try:
                requerido = convertir_a_unidad_base(
                    receta.cantidad_reque,
                    receta.id_uni_medi_fk,
                    prod.id_uni_medi_produ_fk
                ) * Decimal(str(cantidad_futura))
            except ValueError:
                requerido = receta.cantidad_reque * Decimal(str(cantidad_futura))

            if stock < requerido:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Actualmente no está disponible por falta de stock.'
                }, status=400)

    item, created = CarritoItem.objects.get_or_create(
        id_cliente_fk=cliente, 
        id_menu_fk=menu,
        defaults={'cantidad': cantidad}
    )
    
    if not created:
        item.cantidad += cantidad
        item.save()
        
    return badge_sincronizacion(request)

@require_POST
def quitar_carrito(request, menu_id):
    cliente = get_cliente_global(request)
    if not cliente:
        return JsonResponse({'status': 'error', 'message': 'Debes iniciar sesión.'}, status=401)
    
    CarritoItem.objects.filter(id_cliente_fk=cliente, id_menu_fk_id=menu_id).delete()
    return badge_sincronizacion(request)

def badge_sincronizacion(request):
    cliente = get_cliente_global(request)
    total_favoritos = 0
    total_carrito = 0
    carrito_dict = {}
    favoritos_list = []

    if cliente:
        fav_items = Favorito.objects.filter(id_cliente_fk=cliente)
        total_favoritos = fav_items.count()
        favoritos_list = [f.id_menu_fk_id for f in fav_items]

        cart_items = CarritoItem.objects.filter(id_cliente_fk=cliente)
        total_carrito = sum(item.cantidad for item in cart_items)
        for item in cart_items:
            carrito_dict[str(item.id_menu_fk_id)] = {
                'id': str(item.id_menu_fk_id),
                'nombre': item.id_menu_fk.nom_menu,
                'precio': float(item.id_menu_fk.precio_menu),
                'cantidad': item.cantidad,
                'img': item.id_menu_fk.img_menu.url if item.id_menu_fk.img_menu else ''
            }
        
    carrito_json = json.dumps(carrito_dict)
    favoritos_json = json.dumps(favoritos_list)

    html = f"""
    <span id="badge-carrito-sidebar" class="sidebar-badge" hx-swap-oob="true" style="display: {'flex' if total_carrito > 0 else 'none'}">{total_carrito}</span>
    <span id="badge-favoritos-sidebar" class="sidebar-badge" hx-swap-oob="true" style="display: {'flex' if total_favoritos > 0 else 'none'}">{total_favoritos}</span>
    <script>
        try {{
            if (window.PAELLA_CARRITO_KEY) {{
                localStorage.setItem(window.PAELLA_CARRITO_KEY, '{carrito_json}');
            }}
            if (window.PAELLA_FAVORITOS_KEY) {{
                localStorage.setItem(window.PAELLA_FAVORITOS_KEY, '{favoritos_json}');
            }}
            if (typeof renderCarrito === "function") renderCarrito();
        }} catch(e) {{}}
    </script>
    """
    response = HttpResponse(html)
    response['HX-Trigger'] = 'syncComplete'
    return response
