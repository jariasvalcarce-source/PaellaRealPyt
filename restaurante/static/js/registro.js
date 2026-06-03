document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('formulario-registro');
    const fechaNacimientoInput = document.getElementById('fecha-nacimiento');
    const mensajeEdad = document.getElementById('mensaje');
    const passwordInput = document.getElementById('password');
    const passwordConfirmInput = document.getElementById('password_confirmation');
    const usernameInput = document.getElementById('nombre_usuario');
    const emailInput = document.getElementById('email');
    const nombreInput = document.getElementById('nom_clien');
    const apellidoInput = document.getElementById('apellido_clien');
    const telefonoInput = document.getElementById('tel_cliente');
    const allowedDomains = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com', 'live.com', 'msn.com'];

    function setMsg(id, text, ok) {
        const node = document.getElementById(id);
        if (!node) return;
        node.textContent = text || '';
        node.classList.toggle('valid', !!ok && !text);
        node.classList.toggle('invalid', !!text);
    }

    // ==========================================
    // 1. VALIDACIÓN DE EDAD (>= 17 AÑOS)
    // ==========================================
    function calcularEdad(fechaString) {
        if (!fechaString) return 0;
        const hoy = new Date();
        const fechaNac = new Date(fechaString);
        let edad = hoy.getFullYear() - fechaNac.getFullYear();
        const mes = hoy.getMonth() - fechaNac.getMonth();
        if (mes < 0 || (mes === 0 && hoy.getDate() < fechaNac.getDate())) {
            edad--;
        }
        return edad;
    }

    function validarFechaNacimiento() {
        if (!fechaNacimientoInput) return true;
        const fechaStr = fechaNacimientoInput.value;
        if (!fechaStr) {
            mensajeEdad.textContent = '';
            setMsg('msg-fecha_naci_cliente', '', false);
            fechaNacimientoInput.setCustomValidity('');
            return false;
        }
        const edad = calcularEdad(fechaStr);
        if (edad < 15) {
            mensajeEdad.textContent = 'Debes tener al menos 15 años para registrarte.';
            mensajeEdad.style.color = '#b91c1c';
            fechaNacimientoInput.setCustomValidity('Debes tener al menos 15 años.');
            setMsg('msg-fecha_naci_cliente', 'Debes tener al menos 15 años.', false);
            return false;
        }
        mensajeEdad.textContent = `Tienes ${edad} años. Edad apta para el registro.`;
        mensajeEdad.style.color = '#047857';
        fechaNacimientoInput.setCustomValidity('');
        setMsg('msg-fecha_naci_cliente', '', true);
        return true;
    }

    if (fechaNacimientoInput) {
        fechaNacimientoInput.addEventListener('change', validarFechaNacimiento);
    }

    // ==========================================
    // 2. COINCIDENCIA DE CONTRASEÑAS
    // ==========================================
    function validarContrasenas() {
        if (!passwordInput || !passwordConfirmInput) return true;
        const p1 = passwordInput.value.trim();
        const p2 = passwordConfirmInput.value.trim();
        let ok = true;
        let msg = '';
        if (p1 && p1.length < 8) { ok = false; msg = 'La contraseña debe tener al menos 8 caracteres.'; }
        if (p2 && p1 !== p2) { ok = false; msg = 'Las contraseñas no coinciden.'; }
        passwordInput.setCustomValidity(ok ? '' : msg);
        passwordConfirmInput.setCustomValidity(ok ? '' : msg);
        setMsg('msg-password', p1 && p1.length < 8 ? 'La contraseña debe tener al menos 8 caracteres.' : '', ok && !msg);
        setMsg('msg-password_confirmation', p2 && p1 !== p2 ? 'Las contraseñas no coinciden.' : '', p2 ? p1 === p2 : false);
        return ok;
    }

    if (passwordInput && passwordConfirmInput) {
        passwordInput.addEventListener('input', validarContrasenas);
        passwordConfirmInput.addEventListener('input', validarContrasenas);
    }

    // ==========================================
    // 3. FORMATO DE NOMBRE DE USUARIO
    // ==========================================
    function validarNombreUsuario() {
        if (!usernameInput) return true;
        const val = usernameInput.value.trim();
        const tieneEspacios = /\s/.test(val);
        const tieneMayuscula = /[A-Z]/.test(val);
        const tieneNumero = /\d/.test(val);
        const largoCorrecto = val.length >= 4 && val.length <= 20;
        let msg = '';
        if (tieneEspacios) msg = 'No puede contener espacios.';
        else if (!tieneMayuscula) msg = 'Debe tener al menos una letra mayúscula.';
        else if (!tieneNumero) msg = 'Debe incluir al menos un número.';
        else if (!largoCorrecto) msg = 'Debe tener entre 4 y 20 caracteres.';
        usernameInput.setCustomValidity(msg);
        setMsg('msg-nombre_usuario', msg, !msg);
        return !msg;
    }

    if (usernameInput) {
        usernameInput.addEventListener('input', function () {
            this.value = this.value.replace(/\s/g, '');
            validarNombreUsuario();
        });
    }

    function validarEmail() {
        if (!emailInput) return true;
        const val = emailInput.value.trim().toLowerCase();
        const regex = /^[^\s@]+@[^\s@]+\.com$/i;
        const dominio = val.split('@')[1] || '';
        const permitido = allowedDomains.includes(dominio);
        let msg = '';
        if (!val) msg = 'El correo es obligatorio.';
        else if (!regex.test(val)) msg = 'Debe terminar en .com y tener un formato válido.';
        else if (!permitido) msg = 'Use un correo de Gmail, Hotmail, Outlook, Yahoo, Live o MSN.';
        emailInput.setCustomValidity(msg);
        setMsg('msg-email', msg, !msg);
        return !msg;
    }

    if (emailInput) {
        emailInput.addEventListener('input', validarEmail);
    }

    function validarTextoSoloLetras(input, msgId) {
        if (!input) return true;
        const val = input.value;
        const soloLetras = /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/.test(val);
        const tieneNumero = /\d/.test(val);
        let msg = '';
        if (!val.trim()) msg = 'Este campo es obligatorio.';
        else if (tieneNumero) msg = 'No se permiten números.';
        else if (!soloLetras) msg = 'Solo se permiten letras y espacios.';
        input.setCustomValidity(msg);
        setMsg(msgId, msg, !msg);
        return !msg;
    }

    if (nombreInput) {
        nombreInput.addEventListener('input', function () {
            this.value = this.value.replace(/[0-9]/g, '');
            validarTextoSoloLetras(this, 'msg-nom_clien');
        });
    }

    if (apellidoInput) {
        apellidoInput.addEventListener('input', function () {
            this.value = this.value.replace(/[0-9]/g, '');
            validarTextoSoloLetras(this, 'msg-apellido_clien');
        });
    }

    function validarTelefono() {
        if (!telefonoInput) return true;
        const val = telefonoInput.value.replace(/\D/g, '');
        telefonoInput.value = val;
        let msg = '';
        if (!val) msg = 'El teléfono es obligatorio.';
        else if (!/^\d{10}$/.test(val)) msg = 'Debe tener exactamente 10 dígitos.';
        telefonoInput.setCustomValidity(msg);
        setMsg('msg-tel_cliente', msg, !msg);
        return !msg;
    }

    if (telefonoInput) {
        telefonoInput.addEventListener('input', validarTelefono);
    }

    document.querySelectorAll('.password-toggle').forEach((btn) => {
        btn.addEventListener('click', () => {
            const target = document.getElementById(btn.dataset.target);
            if (!target) return;
            const isPassword = target.type === 'password';
            target.type = isPassword ? 'text' : 'password';
            btn.querySelector('i').className = isPassword ? 'bx bx-hide' : 'bx bx-show';
        });
    });

    if (form) {
        form.addEventListener('submit', function (event) {
            const okUser = validarNombreUsuario();
            const okEmail = validarEmail();
            const okPass = validarContrasenas();
            const okNames = validarTextoSoloLetras(nombreInput, 'msg-nom_clien');
            const okApellidos = validarTextoSoloLetras(apellidoInput, 'msg-apellido_clien');
            const okEdad = validarFechaNacimiento();
            const okTel = validarTelefono();
            const allOk = okUser && okEmail && okPass && okNames && okApellidos && okEdad && okTel;
            if (!allOk) {
                event.preventDefault();
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) firstInvalid.focus();
                return;
            }
            event.preventDefault();
            Swal.fire({
                title: '¿Estás seguro?',
                text: 'Se creará tu cuenta con estos datos.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Sí, registrarme',
                cancelButtonText: 'Cancelar',
                reverseButtons: true,
            }).then((result) => {
                if (result.isConfirmed) form.submit();
            });
        });
    }

    if (document.body.dataset.registroExitoso === 'true') {
        Swal.fire({
            title: '¡Registro creado correctamente!',
            text: 'Tu cuenta quedó registrada en La Paella Real.',
            icon: 'success',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        });
    }

    // ==========================================
    // 4. ANIMACIÓN VISUAL EN LOS PASOS (STEPS)
    // ==========================================
    // El formulario tiene tres grupos-campos. Al enfocarse en ellos,
    // actualizamos de forma interactiva el progreso visual en la cabecera.
    const camposGrupos = document.querySelectorAll('.grupo-campos');
    const steps = document.querySelectorAll('.progress-bar .step');

    camposGrupos.forEach((grupo, index) => {
        grupo.addEventListener('focusin', function() {
            // Desactivar pasos posteriores
            steps.forEach((step, sIndex) => {
                if (sIndex <= index) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                    step.classList.remove('completado');
                }
                
                if (sIndex < index) {
                    step.classList.remove('active');
                    step.classList.add('completado');
                }
            });
        });
    });
});
