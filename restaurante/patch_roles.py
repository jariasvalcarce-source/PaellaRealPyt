import os
import re

def patch_file(filepath, signatures):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    out_lines = []
    for line in lines:
        out_lines.append(line)
        for sig in signatures:
            if line.strip().startswith(sig):
                indent = len(line) - len(line.lstrip())
                prefix = ' ' * (indent + 4)
                out_lines.append(prefix + 'if request.session.get("rol") != "admin":\n')
                out_lines.append(prefix + '    from django.shortcuts import redirect\n')
                out_lines.append(prefix + '    from django.contrib import messages\n')
                out_lines.append(prefix + '    messages.error(request, "Acceso denegado. Permisos insuficientes.")\n')
                out_lines.append(prefix + '    return redirect("dashboard_admin")\n')
                break

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

patch_file('core/views/views_personas.py', [
    'def tabla_empleados(',
    'def crear_empleado(',
    'def editar_empleado(',
    'def cambiar_estado_empleado(',
    'def tabla_proveedores(',
    'def crear_proveedor(',
    'def editar_proveedor(',
    'def cambiar_estado_proveedor('
])

with open('core/views/views_reportes.py', 'r', encoding='utf-8') as f:
    rcontent = f.read()

rcontent = rcontent.replace(
    "if request.session.get('rol') not in ['admin', 'empleado']:",
    "if request.session.get('rol') != 'admin':"
)

with open('core/views/views_reportes.py', 'w', encoding='utf-8') as f:
    f.write(rcontent)

print('PATCH_OK')
