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
        
    orig = unidad_origen.abreviatura.upper()
    base = unidad_destino.abreviatura.upper()
    
    if orig == base:
        return Decimal(str(cantidad))
        
    # Peso
    if orig == 'KG' and base in ('G', 'GR'): return Decimal(str(cantidad)) * Decimal('1000.0')
    if orig == 'LB' and base in ('G', 'GR'): return Decimal(str(cantidad)) * Decimal('453.59')
    if orig in ('G', 'GR') and base == 'KG': return Decimal(str(cantidad)) * Decimal('0.001')
    
    # Volumen
    if orig == 'L' and base == 'ML': return Decimal(str(cantidad)) * Decimal('1000.0')
    if orig == 'ML' and base == 'L': return Decimal(str(cantidad)) * Decimal('0.001')
    if orig == 'OZ' and base == 'ML': return Decimal(str(cantidad)) * Decimal('29.57')
    
    # Unidades
    if 'DOCENA' in orig and 'UN' in base: return Decimal(str(cantidad)) * Decimal('12.0')
    if 'CUBETA' in orig and 'UN' in base: return Decimal(str(cantidad)) * Decimal('30.0')
    
    # Fallback to names if abbreviation fails
    origen_nom = unidad_origen.nom_uni_medi.lower().strip()
    destino_nom = unidad_destino.nom_uni_medi.lower().strip()
    
    if origen_nom == destino_nom:
        return Decimal(str(cantidad))
        
    conversiones = {
        ('gramo', 'kilogramo'): Decimal('0.001'),
        ('gramos', 'kilogramo'): Decimal('0.001'),
        ('gramos', 'kilogramos'): Decimal('0.001'),
        ('gramo', 'kilogramos'): Decimal('0.001'),
        ('kilogramo', 'gramo'): Decimal('1000'),
        ('kilogramos', 'gramo'): Decimal('1000'),
        ('kilogramos', 'gramos'): Decimal('1000'),
        ('kilogramo', 'gramos'): Decimal('1000'),
        ('mililitro', 'litro'): Decimal('0.001'),
        ('mililitros', 'litros'): Decimal('0.001'),
        ('litro', 'mililitro'): Decimal('1000'),
        ('litros', 'mililitros'): Decimal('1000'),
    }
    
    clave = (origen_nom, destino_nom)
    factor = conversiones.get(clave)
    
    if factor is not None:
        return Decimal(str(cantidad)) * factor
        
    raise ValueError(f"Conversión no soportada de {orig} a {base} o de {origen_nom} a {destino_nom}.")
