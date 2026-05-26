document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('formulario-registro');
    const fechaNacimientoInput = document.getElementById('fecha-nacimiento');
    const mensajeEdad = document.getElementById('mensaje');
    const passwordInput = document.querySelector('input[name="password"]');
    const passwordConfirmInput = document.querySelector('input[name="password_confirmation"]');
    const usernameInput = document.querySelector('input[name="nombre_usuario"]');

    // ==========================================
    // 1. VALIDACIÓN DE EDAD (>= 17 AÑOS)
    // ==========================================
    function calcularEdad(fechaString) {
        if (!fechaString) return 0;
        const hoy = new Date();
        const fechaNac = new Date(fechaString);
        
        // Ajuste por zona horaria local para evitar descalces de 1 día
        const utcHoy = Date.UTC(hoy.getFullYear(), hoy.getMonth(), hoy.getDate());
        const utcNac = Date.UTC(fechaNac.getFullYear(), fechaNac.getMonth(), fechaNac.getDate() + 1);
        
        let edad = hoy.getFullYear() - fechaNac.getFullYear();
        const mes = hoy.getMonth() - fechaNac.getMonth();
        if (mes < 0 || (mes === 0 && hoy.getDate() < fechaNac.getDate())) {
            edad--;
        }
        return edad;
    }

    if (fechaNacimientoInput) {
        fechaNacimientoInput.addEventListener('change', function () {
            const fechaStr = this.value;
            if (!fechaStr) {
                mensajeEdad.textContent = "";
                fechaNacimientoInput.setCustomValidity("");
                return;
            }

            const edad = calcularEdad(fechaStr);
            if (edad < 17) {
                mensajeEdad.textContent = "Debes tener al menos 17 años para registrarte en La Paella Real.";
                mensajeEdad.style.color = "#ef4444";
                mensajeEdad.style.fontSize = "0.85rem";
                fechaNacimientoInput.setCustomValidity("Debes tener al menos 17 años.");
            } else {
                mensajeEdad.textContent = `Tienes ${edad} años. ¡Edad apta para el registro!`;
                mensajeEdad.style.color = "#10b981";
                mensajeEdad.style.fontSize = "0.85rem";
                fechaNacimientoInput.setCustomValidity("");
            }
        });
    }

    // ==========================================
    // 2. COINCIDENCIA DE CONTRASEÑAS
    // ==========================================
    function validarContrasenas() {
        if (!passwordInput || !passwordConfirmInput) return;
        
        const p1 = passwordInput.value;
        const p2 = passwordConfirmInput.value;

        if (p2 && p1 !== p2) {
            passwordConfirmInput.setCustomValidity("Las contraseñas no coinciden");
        } else {
            passwordConfirmInput.setCustomValidity("");
        }
    }

    if (passwordInput && passwordConfirmInput) {
        passwordInput.addEventListener('input', validarContrasenas);
        passwordConfirmInput.addEventListener('input', validarContrasenas);
    }

    // ==========================================
    // 3. FORMATO DE NOMBRE DE USUARIO
    // ==========================================
    function validarNombreUsuario() {
        if (!usernameInput) return;

        const val = usernameInput.value;
        const tieneEspacios = /\s/.test(val);
        const tieneMayuscula = /[A-Z]/.test(val);
        const largoCorrecto = val.length <= 20;

        if (tieneEspacios) {
            usernameInput.setCustomValidity("El nombre de usuario no puede contener espacios.");
        } else if (!tieneMayuscula && val.length > 0) {
            usernameInput.setCustomValidity("Debe tener al menos una letra mayúscula.");
        } else if (!largoCorrecto) {
            usernameInput.setCustomValidity("El nombre de usuario no puede superar los 20 caracteres.");
        } else {
            usernameInput.setCustomValidity("");
        }
    }

    if (usernameInput) {
        usernameInput.addEventListener('input', validarNombreUsuario);
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
