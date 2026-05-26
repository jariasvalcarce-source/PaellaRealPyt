import os
import django
import sys
from datetime import date

def run():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurante.settings')
    django.setup()
    
    from core.models import Rol, UsuarioAuth, Empleado
    
    # 1. Create default roles
    print("Seeding roles...")
    for r in ['admin', 'empleado', 'cliente']:
        rol, created = Rol.objects.get_or_create(name=r)
        if created:
            print(f"Created role: {r}")
            
    # 2. Create default admin auth
    admin_rol = Rol.objects.get(name='admin')
    admin_auth, created = UsuarioAuth.objects.get_or_create(
        nombre_usuario='admin',
        defaults={'rol': admin_rol, 'activo': True}
    )
    if created:
        admin_auth.set_password('admin123') # Default password, user can change in profile
        admin_auth.save()
        print("Created default admin auth account (username: admin, password: admin123)")
    else:
        print("Admin auth account already exists.")
        
    # 3. Create default admin employee complying with the new database schema
    if not Empleado.objects.filter(id_auth_fk=admin_auth).exists():
        Empleado.objects.create(
            nom_emple='Admin',
            apellido_emple='Sistema',
            fecha_naci_emple=date(2000,1,1),
            tel_emple='3000000000',
            correo_emple='admin@paellareal.com',
            direc_emple='Sede Principal',
            estado_emple='activo',
            id_auth_fk=admin_auth,
            foto_empleado='default.png',
            tipo_doc='Cédula de Ciudadanía',
            num_doc='1234567890',
            fecha_ingreso=date(2026,1,1),
            tipo_contrato='Término Indefinido',
            salario_empleado=2000000.00
        )
        print("Created default admin employee account matching schema!")
    else:
        print("Admin employee account already exists.")

if __name__ == '__main__':
    run()
