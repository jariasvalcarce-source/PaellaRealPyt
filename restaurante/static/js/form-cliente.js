// =========================================
// Formulario Registro Cliente - Validaciones
// =========================================

const nameRegex = /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/;
const usernameRegex = /^(?=.*[A-Z])(?=.*\d)[A-Za-z\d_]{4,20}$/;
const phoneRegex = /^3\d{9}$/;
const emailRegex = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z][a-zA-Z0-9\-]*\.com$/;

// Funciones de validación
function calcularEdad(fecha) {
    const hoy = new Date();
    const nacimiento = new Date(fecha);
    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    const m = hoy.getMonth() - nacimiento.getMonth();
    if (m < 0 || (m === 0 && hoy.getDate() < nacimiento.getDate())) edad--;
    return edad;
}

function setValid(wrap, msg) {
    if (!wrap) return;
    wrap.classList.add('valid');
    wrap.classList.remove('invalid');
    if (msg) msg.textContent = '';
}

function setInvalid(wrap, msg, text) {
    if (!wrap) return;
    wrap.classList.add('invalid');
    wrap.classList.remove('valid');
    if (msg) msg.textContent = text;
}

// Validación de duplicidad de nombre de usuario
async function verificarDuplicidadUsername(username) {
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        const response = await fetch('/api/check-username/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken ? csrfToken.value : '',
            },
            body: JSON.stringify({ username: username })
        });
        const data = await response.json();
        return data.disponible === true;
    } catch (e) {
        console.error('Error checking username:', e);
        return true; // Por defecto, asumir disponible si hay error
    }
}

function validateField(input) {
    const wrap = input.closest('.input-wrap');
    const msg = document.getElementById('msg-' + input.id);
    const value = input.value.trim();

    // Nombre de usuario
    if (input.id === 'nombre_usuario') {
        if (!value) {
            setInvalid(wrap, msg, 'El nombre de usuario es obligatorio.');
            return false;
        }
        if (!usernameRegex.test(value)) {
            setInvalid(wrap, msg, 'Min. 4 caracteres, al menos una mayúscula, un número, sin espacios.');
            return false;
        }
        setValid(wrap, msg);
        return true;
    }

    // Nombres
    if (input.id === 'nombres') {
        if (!value || value.length < 2) {
            setInvalid(wrap, msg, 'El nombre es obligatorio.');
            return false;
        }
        if (!nameRegex.test(value)) {
            setInvalid(wrap, msg, 'El nombre solo puede contener letras y espacios.');
            return false;
        }
        setValid(wrap, msg);
        return true;
    }

    // Apellidos
    if (input.id === 'apellidos') {
        if (!value || value.length < 2) {
            setInvalid(wrap, msg, 'El apellido es obligatorio.');
            return false;
        }
        if (!nameRegex.test(value)) {
            setInvalid(wrap, msg, 'El apellido solo puede contener letras y espacios.');
            return false;
        }
        setValid(wrap, msg);
        return true;
    }

    // Fecha de nacimiento
    if (input.id === 'fecha_nacimiento') {
        if (!value) {
            setInvalid(wrap, msg, 'La fecha de nacimiento es obligatoria.');
            return false;
        }
        const edad = calcularEdad(value);
        if (edad < 15) {
            setInvalid(wrap, msg, 'Debes tener al menos 15 años.');
            return false;
        }
        setValid(wrap, msg);
        return true;
    }

    // Teléfono
    if (input.id === 'telefono') {
        if (!phoneRegex.test(value)) {
            setInvalid(wrap, msg, 'El teléfono debe tener 10 dígitos y comenzar con 3.');
            return false;
        }
        setValid(wrap, msg);
        return true;
    }

    // Correo
    if (input.id === 'correo') {
        if (!emailRegex.test(value)) {
            setInvalid(wrap, msg, 'Correo inválido (ej: usuario@gmail.com).');
            return false;
        }
        setValid(wrap, msg);
        return true;
    }

    // Dirección
    if (input.id === 'direccion') {
        if (!value || value.length < 5) {
            setInvalid(wrap, msg, 'La dirección debe tener al menos 5 caracteres.');
            return false;
        }
        setValid(wrap, msg);
        return true;
    }

    return true;
}

document.addEventListener('DOMContentLoaded', function () {
    const formCliente = document.getElementById('formCliente');
    
    // Event listeners para validaciones en tiempo real
    if (formCliente) {
        const inputs = formCliente.querySelectorAll('input[type="text"], input[type="date"], input[type="tel"], input[type="email"]');
        
        inputs.forEach((input) => {
            input.addEventListener('blur', async () => {
                if (input.id === 'nombre_usuario') {
                    // Validar formato
                    if (!validateField(input)) return;
                    // Verificar duplicidad
                    const wrap = input.closest('.input-wrap');
                    const msg = document.getElementById('msg-' + input.id);
                    const disponible = await verificarDuplicidadUsername(input.value.trim());
                    if (!disponible) {
                        setInvalid(wrap, msg, 'Este nombre de usuario ya está en uso.');
                    } else {
                        setValid(wrap, msg);
                    }
                } else {
                    validateField(input);
                }
            });
            
            input.addEventListener('input', () => {
                const wrap = input.closest('.input-wrap');
                if (wrap?.classList.contains('invalid')) {
                    validateField(input);
                }
            });
        });

        // Submit del formulario
        formCliente.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            let valid = true;
            const inputs = formCliente.querySelectorAll('input[type="text"], input[type="date"], input[type="tel"], input[type="email"]');
            
            for (let input of inputs) {
                if (!validateField(input)) {
                    valid = false;
                }
                // Verificar duplicidad de username si es necesario
                if (input.id === 'nombre_usuario') {
                    const disponible = await verificarDuplicidadUsername(input.value.trim());
                    const wrap = input.closest('.input-wrap');
                    const msg = document.getElementById('msg-' + input.id);
                    if (!disponible) {
                        setInvalid(wrap, msg, 'Este nombre de usuario ya está en uso.');
                        valid = false;
                    }
                }
            }

            if (!valid) {
                const firstInvalid = formCliente.querySelector('.input-wrap.invalid input');
                if (firstInvalid) firstInvalid.focus();
                return;
            }

            // Mostrar confirmación
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '¿Registrar Cliente?',
                    text: "Se guardarán los datos de este nuevo cliente.",
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: 'var(--primary)',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Sí, registrar',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        formCliente.submit();
                    }
                });
            } else {
                if (confirm('¿Registrar este cliente?')) {
                    formCliente.submit();
                }
            }
        });
    }


    // Mensajes de Django ahora se manejan globalmente por premium-alerts.js
});
