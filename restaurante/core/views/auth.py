# auth.py
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import UsuarioAuth, Cliente, Rol
from datetime import datetime


def inicio(request):
    return render(request, 'inicio.html')


def login_view(request):
    if request.method == 'POST':
        usuario  = request.POST.get('usuario', '').strip()
        password = request.POST.get('password')
        try:
            user = UsuarioAuth.objects.select_related('rol').get(nombre_usuario=usuario)
            
            if not user.activo:
                messages.error(request, 'Su cuenta ha sido desactivada. Por favor, contacte al administrador.')
                return render(request, 'login.html')

            if user.check_password(password):
                request.session['usuario_id'] = user.id_auth_pk
                request.session['usuario']    = user.nombre_usuario
                request.session['rol']        = user.rol.name
                
                if password.startswith('Prov-'):
                    request.session['cambio_pw_pendiente'] = True

                destinos = {
                    'admin':    'dashboard_admin',
                    'empleado': 'dashboard_admin',
                    'cliente':  'inicio_usuarios',
                }
                return redirect(destinos[user.rol.name])
            messages.error(request, 'Contraseña incorrecta')
        except UsuarioAuth.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


def registro_view(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('nombre_usuario', '').strip()
        email     = request.POST.get('email', '').strip()
        password  = request.POST.get('password', '')
        password2 = request.POST.get('password_confirmation', '')
        fecha_nac_str = request.POST.get('fecha_naci_cliente', '')

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'registro.html', {'datos': request.POST})

        if fecha_nac_str:
            fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
            hoy = datetime.now().date()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            if edad < 17:
                messages.error(request, 'Debes tener al menos 17 años para registrarte en La Paella Real.')
                return render(request, 'registro.html', {'datos': request.POST})

        if not nombre_usuario or ' ' in nombre_usuario or len(nombre_usuario) > 20 or not any(c.isupper() for c in nombre_usuario):
            messages.error(request, 'El nombre de usuario no puede tener espacios, máximo 20 caracteres y debe tener al menos una letra mayúscula.')
            return render(request, 'registro.html', {'datos': request.POST})

        if UsuarioAuth.objects.filter(nombre_usuario=nombre_usuario).exists():
            messages.error(request, 'Ese nombre de usuario ya está en uso. Por favor, elige otro.')
            return render(request, 'registro.html', {'datos': request.POST})

        if UsuarioAuth.objects.filter(cliente__correo_clien=email).exists():
            messages.error(request, 'Ya existe una cuenta con ese email')
            return render(request, 'registro.html', {'datos': request.POST})

        try:
            rol_cliente = Rol.objects.get(name='cliente')
        except Rol.DoesNotExist:
            messages.error(request, 'Error de configuración: roles no creados')
            return render(request, 'registro.html')

        usuario = UsuarioAuth(nombre_usuario=nombre_usuario, activo=True, rol=rol_cliente)
        usuario.set_password(password)
        usuario.save()

        Cliente.objects.create(
            nom_clien          = request.POST.get('nom_clien', '').strip(),
            apellido_clien     = request.POST.get('apellido_clien', '').strip(),
            fecha_naci_cliente = request.POST.get('fecha_naci_cliente', ''),
            tel_cliente        = request.POST.get('tel_cliente', '').strip(),
            correo_clien       = request.POST.get('correo_clien', '').strip(),
            direc_clien        = request.POST.get('direc_clien', '').strip(),
            estado_clien       = 'activo',
            id_auth_fk         = usuario,
        )

        # No iniciamos sesión automáticamente, dejamos que el usuario haga login
        return render(request, 'registro.html', {'registro_exitoso': True})

    return render(request, 'registro.html')