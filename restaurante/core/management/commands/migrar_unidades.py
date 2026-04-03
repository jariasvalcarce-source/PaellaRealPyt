import os
from django.core.management.base import BaseCommand
from core.models import Producto, MovimientoProducto, UnidadMedida
from decimal import Decimal

class Command(BaseCommand):
    help = 'Convierte el inventario de la base de datos de gramos a kilogramos de forma segura.'

    def handle(self, *args, **kwargs):
        # Asegurar que existe una unidad de medida para kilogramos
        kg_unit, _ = UnidadMedida.objects.get_or_create(
            abreviatura__iexact='kg',
            defaults={'nom_uni_medi': 'Kilogramos', 'abreviatura': 'kg', 'tipo_uni_medi': 'Masa'}
        )
        
        # Filtramos unidades que podrían ser gramos (g, gr, gramos)
        g_units = UnidadMedida.objects.filter(abreviatura__in=['g', 'gr', 'gramos'])
        
        if not g_units.exists():
            self.stdout.write(self.style.WARNING("No se encontró una unidad de gramos (abreviatura g). Verificando productos con stock de gramos introducidos erróneamente en kg..."))
            # Heurística temporal: si el stock es mayor o igual a 1000, asume que está en gramos
            productos = Producto.objects.filter(stock_actual_produ__gte=1000)
        else:
            self.stdout.write(self.style.SUCCESS("Se encontraron unidades de medida de Gramos."))
            productos = Producto.objects.filter(id_uni_medi_produ_fk__in=g_units)
            
        productos_migrados = 0
            
        for p in productos:
            old_stock = p.stock_actual_produ
            
            # Solo migramos si tiene sentido (números grandes que implican gramos)
            if p.stock_actual_produ >= 50:
                p.stock_actual_produ = round(p.stock_actual_produ / Decimal('1000'), 3)
                p.stock_minimo_produ = round(p.stock_minimo_produ / Decimal('1000'), 3)
                
                # Le asignamos la unidad base 'kg' estrictamente
                p.id_uni_medi_produ_fk = kg_unit
                
                p.save()
                
                # Convertir también todos sus movimientos históricos
                movimientos = MovimientoProducto.objects.filter(id_produ_movi_fk=p)
                for m in movimientos:
                    m.cant_movi = round(m.cant_movi / Decimal('1000'), 3)
                    m.stock_anterior = round(m.stock_anterior / Decimal('1000'), 3)
                    m.stock_posterior = round(m.stock_posterior / Decimal('1000'), 3)
                    m.save()
                    
                productos_migrados += 1
                self.stdout.write(self.style.SUCCESS(f"Migrado '{p.nom_produ}': {old_stock} g -> {p.stock_actual_produ} kg"))

        self.stdout.write(self.style.SUCCESS(f"Se terminaron de migrar {productos_migrados} productos y sus movimientos asociados."))
