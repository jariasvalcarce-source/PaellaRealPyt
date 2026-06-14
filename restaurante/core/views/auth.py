# auth.py
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from core.models import UsuarioAuth, Cliente, Rol
from datetime import datetime
import re


def inicio(request):
    return render(request, 'inicio.html')


def login_view(request):
    if request.method == 'POST':
        usuario  = request.POST.get('email', request.POST.get('usuario', '')).strip()
        password = request.POST.get('password')
        try:
            user = UsuarioAuth.objects.select_related('rol').get(
                Q(nombre_usuario=usuario) | Q(correo=usuario) | Q(cliente__correo_clien=usuario)
            )
            
            if not user.activo:
                messages.error(request, 'Usted ha sido desactivado. Contáctese con nosotros.')
                return render(request, 'login.html', {'datos': request.POST})

            if user.check_password(password):
                request.session['usuario_id'] = user.id_auth_pk
                request.session['usuario']    = user.nombre_usuario
                request.session['rol']        = user.rol.name
                
                if password.startswith('Prov-'):
                    request.session['cambio_pw_pendiente'] = True

                destinos = {
                    'admin':    'dashboard_admin',
                    'empleado': 'dashboard_empleado',
                    'cliente':  'inicio_usuarios',
                }
                redirect_url = reverse(destinos[user.rol.name])
                return render(request, 'login.html', {
                    'datos': request.POST,
                    'login_success': True,
                    'redirect_url': redirect_url,
                })

            messages.error(request, 'Contraseña incorrecta. Por favor verifica tu contraseña.')
            return render(request, 'login.html', {'datos': request.POST})
        except UsuarioAuth.DoesNotExist:
            messages.error(request, 'Usuario no encontrado. Verifica tu usuario o correo.')
            return render(request, 'login.html', {'datos': request.POST})
    return render(request, 'login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


def registro_view(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('nombre_usuario', '').strip()
        email     = request.POST.get('email', request.POST.get('correo_clien', '')).strip().lower()
        password  = request.POST.get('password', '')
        password2 = request.POST.get('password_confirmation', '')
        fecha_nac_str = request.POST.get('fecha_naci_cliente', '')
        nom_clien = request.POST.get('nom_clien', '').strip()
        apellido_clien = request.POST.get('apellido_clien', '').strip()
        tel_cliente = request.POST.get('tel_cliente', '').strip()
        ALLOWED_EMAIL_DOMAINS = {'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com', 'live.com', 'msn.com'}

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'registro.html', {'datos': request.POST})

        if fecha_nac_str:
            fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
            hoy = datetime.now().date()
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            if edad < 15:
                messages.error(request, 'Debes tener al menos 15 años para registrarte en La Paella Real.')
                return render(request, 'registro.html', {'datos': request.POST})

        if not re.fullmatch(r'(?=.*[A-Z])(?=.*\d)[A-Za-z\d_]{4,20}', nombre_usuario):
            messages.error(request, 'El nombre de usuario debe tener 4 a 20 caracteres, al menos una mayúscula, al menos un número y sin espacios.')
            return render(request, 'registro.html', {'datos': request.POST})

        if not re.fullmatch(r'^[^\s@]+@[^\s@]+\.com$', email) or (email.split('@')[1] if '@' in email else '').lower() not in ALLOWED_EMAIL_DOMAINS:
            messages.error(request, 'El correo debe tener formato válido, terminar en .com y usar Gmail, Hotmail, Outlook, Yahoo, Live o MSN.')
            return render(request, 'registro.html', {'datos': request.POST})

        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'registro.html', {'datos': request.POST})

        if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+', nom_clien):
            messages.error(request, 'Los nombres solo pueden contener letras y espacios.')
            return render(request, 'registro.html', {'datos': request.POST})

        if not re.fullmatch(r'[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+', apellido_clien):
            messages.error(request, 'Los apellidos solo pueden contener letras y espacios.')
            return render(request, 'registro.html', {'datos': request.POST})

        if not re.fullmatch(r'\d{10}', tel_cliente):
            messages.error(request, 'El teléfono debe tener exactamente 10 dígitos.')
            return render(request, 'registro.html', {'datos': request.POST})

        if UsuarioAuth.objects.filter(nombre_usuario=nombre_usuario).exists():
            messages.error(request, 'Ese nombre de usuario ya está en uso. Por favor, elige otro.')
            return render(request, 'registro.html', {'datos': request.POST})

        if UsuarioAuth.objects.filter(correo=email).exists() or Cliente.objects.filter(correo_clien=email).exists():
            messages.error(request, 'Ya existe una cuenta con ese email')
            return render(request, 'registro.html', {'datos': request.POST})

        try:
            rol_cliente = Rol.objects.get(name='cliente')
        except Rol.DoesNotExist:
            messages.error(request, 'Error de configuración: roles no creados')
            return render(request, 'registro.html')

        usuario = UsuarioAuth(
            nombre_usuario=nombre_usuario, 
            correo=email,
            activo=True, 
            rol=rol_cliente
        )
        usuario.set_password(password)
        usuario.save()

        Cliente.objects.create(
            nom_clien          = request.POST.get('nom_clien', '').strip(),
            apellido_clien     = request.POST.get('apellido_clien', '').strip(),
            fecha_naci_cliente = request.POST.get('fecha_naci_cliente', ''),
            tel_cliente        = request.POST.get('tel_cliente', '').strip(),
            correo_clien       = email,
            direc_clien        = request.POST.get('direc_clien', '').strip(),
            estado_clien       = 'activo',
            id_auth_fk         = usuario,
        )

        # No iniciamos sesión automáticamente, dejamos que el usuario haga login
        return render(request, 'registro.html', {'registro_exitoso': True})

    return render(request, 'registro.html')