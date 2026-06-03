from django.core.management.base import BaseCommand
from core.models import Producto
from decimal import Decimal


class Command(BaseCommand):
    help = 'Fija todos los stocks negativos a 0 y marca productos como no disponibles'

    def handle(self, *args, **options):
        productos_negativos = Producto.objects.filter(stock_actual_produ__lt=0)
        count = productos_negativos.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('✓ No hay productos con stock negativo.'))
            return

        self.stdout.write(self.style.WARNING(f'Encontrados {count} productos con stock negativo.'))

        for producto in productos_negativos:
            stock_anterior = producto.stock_actual_produ
            producto.stock_actual_produ = Decimal('0')
            producto.estado_produ = 'no disponible'
            producto.save()
            self.stdout.write(
                f'  {producto.nom_produ}: {stock_anterior} kg → 0 kg (inactivo)'
            )

        self.stdout.write(
            self.style.SUCCESS(f'✓ {count} productos corregidos exitosamente.')
        )
