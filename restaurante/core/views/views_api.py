# views_api.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ..models import Menu, RecetaMenu


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