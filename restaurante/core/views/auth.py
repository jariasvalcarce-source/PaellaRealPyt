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

        if not re.fullmatch(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            messages.error(request, 'Por favor, ingresa un correo electrónico válido.')
            return render(request, 'registro.html', {'datos': request.POST})

        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un carácter especial.')
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

import resend
from django.core import signing
from django.conf import settings
from django.http import HttpResponse

def solicitar_recuperacion(request):
    if request.method == 'POST':
        usuario_input = request.POST.get('email_o_usuario', '').strip()
        try:
            # Buscar por nombre de usuario, correo en auth o correo en cliente
            user = UsuarioAuth.objects.select_related('cliente').get(
                Q(nombre_usuario=usuario_input) | Q(correo=usuario_input) | Q(cliente__correo_clien=usuario_input)
            )
            
            # Si el usuario_auth no tiene correo directamente, intentamos usar el del cliente
            correo_destino = user.correo
            if not correo_destino and hasattr(user, 'cliente') and user.cliente.correo_clien:
                correo_destino = user.cliente.correo_clien
                
            if not correo_destino:
                messages.error(request, 'No hay un correo electrónico asociado a esta cuenta.')
                return render(request, 'olvide_password.html')
                
            # Generar token seguro válido por 1 hora
            token = signing.dumps({'user_id': user.id_auth_pk})
            
            # URL de restablecimiento (usamos request.build_absolute_uri para incluir dominio/puerto)
            reset_url = request.build_absolute_uri(reverse('restablecer_contrasena', args=[token]))
            
            # Enviar con Django SMTP
            from django.core.mail import send_mail
            
            html_content = f"""
            <h2>Recuperación de contraseña de La Paella Real</h2>
            <p>Hola {user.nombre_usuario},</p>
            <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para crear una nueva (este enlace expira en 1 hora):</p>
            <p><a href="{reset_url}" style="background-color: #8b0000; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Restablecer Contraseña</a></p>
            <p>Si no solicitaste esto, ignora este correo.</p>
            """
            
            send_mail(
                subject='Restablece tu contraseña - La Paella Real',
                message=f'Restablece tu contraseña aquí: {reset_url}', # Plain text fallback
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[correo_destino],
                fail_silently=False,
                html_message=html_content
            )
            
            return render(request, 'olvide_password.html', {'email_enviado': True})
            
        except UsuarioAuth.DoesNotExist:
            # Por seguridad, no decimos si el correo existe o no, pero mostraremos éxito simulado
            # o podemos ser explícitos para mejorar UX en este caso
            messages.error(request, 'No encontramos ninguna cuenta con esos datos.')
        except Exception as e:
            messages.error(request, f'Hubo un problema al enviar el correo: {str(e)}')
            
    return render(request, 'olvide_password.html')

def restablecer_contrasena(request, token):
    try:
        data = signing.loads(token, max_age=3600) # 1 hora de validez
        user_id = data['user_id']
        user = UsuarioAuth.objects.get(id_auth_pk=user_id)
    except signing.SignatureExpired:
        messages.error(request, 'El enlace de recuperación ha expirado. Por favor solicita uno nuevo.')
        return redirect('solicitar_recuperacion')
    except (signing.BadSignature, UsuarioAuth.DoesNotExist):
        messages.error(request, 'El enlace de recuperación es inválido.')
        return redirect('solicitar_recuperacion')

    if request.method == 'POST':
        password = request.POST.get('password', '')
        password_confirmation = request.POST.get('password_confirmation', '')

        if password != password_confirmation:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'restablecer_password.html', {'token': token})

        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un carácter especial.')
            return render(request, 'restablecer_password.html', {'token': token})

        # Actualizar contraseña
        user.set_password(password)
        user.save()
        
        messages.success(request, 'Tu contraseña ha sido restablecida exitosamente. ¡Ya puedes iniciar sesión!')
        return redirect('login')

    return render(request, 'restablecer_password.html', {'token': token})