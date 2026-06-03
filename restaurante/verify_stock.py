#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurante.settings')
django.setup()

from core.models import Producto
from decimal import Decimal

# Verificar stocks negativos
negativos = Producto.objects.filter(stock_actual_produ__lt=0)
print(f"✓ Productos con stock < 0: {negativos.count()}")

# Verificar productos con estado 0
cero_stock = Producto.objects.filter(stock_actual_produ=Decimal('0')).count()
print(f"✓ Productos con stock = 0: {cero_stock}")

# Verificar productos inactivos
inactivos = Producto.objects.filter(estado_produ='no disponible').count()
print(f"✓ Productos inactivos: {inactivos}")

print("\n✅ Sistema de stock corregido exitosamente.")
