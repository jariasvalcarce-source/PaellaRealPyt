# utils.py
from decimal import Decimal

def convertir_a_unidad_base(cantidad, unidad_origen, unidad_destino):
    """
    Convierte cantidad a la unidad base del producto usando los nombres exactos de la BD.
    
    Unidades posibles en BD:
    - kilogramo (kg)
    - gramo (g)
    - litro (L)
    - mililitro (ml)
    - unidad (und)
    """
    if not unidad_origen or not unidad_destino:
        return Decimal(str(cantidad))
        
    origen = unidad_origen.nom_uni_medi.lower().strip()
    destino = unidad_destino.nom_uni_medi.lower().strip()
    
    if origen == destino:
        return Decimal(str(cantidad))
        
    conversiones = {
        ('gramo', 'kilogramo'): Decimal('0.001'),
        ('kilogramo', 'gramo'): Decimal('1000'),
        ('mililitro', 'litro'): Decimal('0.001'),
        ('litro', 'mililitro'): Decimal('1000'),
    }
    
    clave = (origen, destino)
    factor = conversiones.get(clave)
    
    if factor is None:
        raise ValueError(f"Conversión no soportada de {origen} a {destino}.")
        
    return Decimal(str(cantidad)) * factor
