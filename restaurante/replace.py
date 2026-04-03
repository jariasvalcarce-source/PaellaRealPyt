import sys
import os
import re

files = [
    r'c:\Software\proyecto-python\restaurante\templates\admin\personas\personas.html',
    r'c:\Software\proyecto-python\restaurante\templates\admin\inventario\inventario.html',
    r'c:\Software\proyecto-python\restaurante\templates\admin\pedido\pedido.html',
    r'c:\Software\proyecto-python\restaurante\templates\admin\factura\factura.html',
    r'c:\Software\proyecto-python\restaurante\templates\admin\personas\index-empleado.html',
    r'c:\Software\proyecto-python\restaurante\templates\admin\personas\index-cliente.html',
    r'c:\Software\proyecto-python\restaurante\templates\admin\inventario\index-receta.html',
    r'c:\Software\proyecto-python\restaurante\templates\admin\inventario\index-proveedor.html',
    r'c:\Software\proyecto-python\restaurante\templates\admin\inventario\index-producto.html',
    r'c:\Software\proyecto-python\restaurante\templates\admin\inventario\index-movimiento-producto.html',
    r'c:\Software\proyecto-python\restaurante\templates\admin\inventario\index-menu.html',
]

pattern = re.compile(r'<section class="sidebar-derecha">.*?</section>', re.DOTALL)

for path in files:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = pattern.sub(r'{% include "admin/includes/sidebar_derecha.html" %}', content)
        
        if content != new_content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Replaced in {path}')
        else:
            print(f'No match in {path}')
    else:
        print(f'Not found: {path}')
