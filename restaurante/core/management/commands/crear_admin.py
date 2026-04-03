from django.core.management.base import BaseCommand
from core.models import UsuarioAuth, Rol

class Command(BaseCommand):
    help = 'Crea el usuario administrador predeterminado'

    def handle(self, *args, **kwargs):
        rol_admin, _ = Rol.objects.get_or_create(name='admin')

        if UsuarioAuth.objects.filter(nombre_usuario='admin').exists():
            self.stdout.write('El admin ya existe.')
            return

        admin = UsuarioAuth(
            nombre_usuario='admin',
            rol=rol_admin,
            activo=True
        )
        admin.set_password('Admin2024*')
        admin.save()

        self.stdout.write(self.style.SUCCESS(
            'Admin creado exitosamente — usuario: admin  contraseña: Admin2024*'
        ))