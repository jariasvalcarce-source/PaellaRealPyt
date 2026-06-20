function initFormProveedor() {
    const form = document.getElementById('formProveedor');

    // Elementos dinámicos
    const radiosTipo = document.querySelectorAll('input[name="tipo_provee"]');
    const labelNomProvee = document.getElementById('label_nom_provee');
    const labelNitCedula = document.getElementById('label_nit_cedula');
    const inputNitCedula = document.getElementById('nit_cedula_provee');
    const inputNomProvee = document.getElementById('nom_provee');
    const fieldNombreContacto = document.getElementById('field_nombre_contacto');
    const inputNombreContacto = document.getElementById('nombre_contacto_provee');
    const textareaObs = document.getElementById('observaciones_provee');
    const charCounter = document.getElementById('char-counter');

    if (!radiosTipo.length || !labelNomProvee) return;

    // Cambiar vista según el tipo
    function updateFormType() {
        const checkedRadio = document.querySelector('input[name="tipo_provee"]:checked');
        if (!checkedRadio) return;
        const tipo = checkedRadio.value;
        if (tipo === 'empresa') {
            labelNomProvee.innerHTML = 'Nombre Empresa <span class="req">*</span>';
            inputNomProvee.placeholder = 'Ej: Distribuidora Lácteos del Valle';
            labelNitCedula.innerHTML = 'NIT <span class="req">*</span>';
            inputNitCedula.placeholder = 'Solo números (ej: 900123456)';
            fieldNombreContacto.style.display = 'block';
        } else {
            labelNomProvee.innerHTML = 'Nombre Completo <span class="req">*</span>';
            inputNomProvee.placeholder = 'Ej: Carlos Martínez Ruiz';
            labelNitCedula.innerHTML = 'Cédula <span class="req">*</span>';
            inputNitCedula.placeholder = 'Solo números (ej: 1023456789)';
            fieldNombreContacto.style.display = 'none';
            inputNombreContacto.value = ''; // Limpiar
            setValid(inputNombreContacto.closest('.input-wrap'), document.getElementById('msg-nombre_contacto_provee'));
        }
    }

    radiosTipo.forEach(r => r.addEventListener('change', () => {
        updateFormType();
        // Revalidar
        validateField(inputNomProvee);
        validateField(inputNitCedula);
    }));

    // Contador de caracteres observaciones
    if (textareaObs && charCounter) {
        textareaObs.addEventListener('input', () => {
            const length = textareaObs.value.length;
            charCounter.textContent = `${length} / 300`;
            if (length > 300) {
                charCounter.style.color = '#ef4444';
            } else {
                charCounter.style.color = '#64748b';
            }
        });
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

    const nameRegex = /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s\-\.\(\)]+$/;
    const phoneRegex = /^3\d{9}$/;
    const emailRegex = /^[^@\s]{6,}@[a-zA-Z][a-zA-Z0-9\-\.]*\.(com|co|com\.co)$/i;
    const numbersOnlyRegex = /^\d+$/;

    function validateField(input) {
        const wrap = input.closest('.input-wrap');
        const msg = document.getElementById('msg-' + input.id);
        const value = input.value.trim();
        const tipo = document.querySelector('input[name="tipo_provee"]:checked').value;

        if (input.id === 'nom_provee') {
            if (!value || value.length < 3) {
                setInvalid(wrap, msg, 'El nombre es muy corto.');
                return false;
            }
            if (!nameRegex.test(value)) {
                setInvalid(wrap, msg, 'Contiene caracteres no permitidos.');
                return false;
            }
            setValid(wrap, msg);
            return true;
        }

        if (input.id === 'nit_cedula_provee') {
            if (!value) {
                setInvalid(wrap, msg, 'Este campo es obligatorio.');
                return false;
            }
            if (!numbersOnlyRegex.test(value)) {
                setInvalid(wrap, msg, 'Debe contener solo números.');
                return false;
            }
            if (tipo === 'empresa' && (value.length < 8 || value.length > 10)) {
                setInvalid(wrap, msg, 'El NIT debe tener entre 8 y 10 dígitos.');
                return false;
            }
            if (tipo === 'persona_natural' && (value.length < 6 || value.length > 10)) {
                setInvalid(wrap, msg, 'La cédula debe tener entre 6 y 10 dígitos.');
                return false;
            }
            setValid(wrap, msg);
            return true;
        }

        if (input.id === 'nombre_contacto_provee' && tipo === 'empresa') {
            if (!value) {
                setInvalid(wrap, msg, 'El nombre de contacto es obligatorio para empresas.');
                return false;
            }
            if (!nameRegex.test(value)) {
                setInvalid(wrap, msg, 'No debe contener caracteres inválidos.');
                return false;
            }
            setValid(wrap, msg);
            return true;
        }

        if (input.id === 'tel_provee') {
            if (!phoneRegex.test(value)) {
                setInvalid(wrap, msg, 'Debe empezar por 3 y tener exactamente 10 dígitos.');
                return false;
            }
            setValid(wrap, msg);
            return true;
        }

        if (input.id === 'correo_provee') {
            if (!emailRegex.test(value)) {
                setInvalid(wrap, msg, 'Por favor, ingresa un correo válido que termine en .com o .co.');
                return false;
            }
            setValid(wrap, msg);
            return true;
        }

        if (input.id === 'direc_provee') {
            if (!value || value.length < 10) {
                setInvalid(wrap, msg, 'La dirección es muy corta (mínimo 10 caracteres).');
                return false;
            }
            setValid(wrap, msg);
            return true;
        }

        return true;
    }

    document.querySelectorAll('#formProveedor input').forEach((input) => {
        if (input.type === 'radio' || input.type === 'checkbox') return;
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => {
            if (input.closest('.input-wrap')?.classList.contains('invalid')) validateField(input);
        });
    });

    if (form) {
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            let valid = true;

            const inputsToValidate = ['nom_provee', 'nit_cedula_provee', 'tel_provee', 'correo_provee', 'direc_provee'];
            const tipo = document.querySelector('input[name="tipo_provee"]:checked').value;
            if (tipo === 'empresa') inputsToValidate.push('nombre_contacto_provee');

            inputsToValidate.forEach(id => {
                const el = document.getElementById(id);
                if (el && !validateField(el)) valid = false;
            });

            if (!valid) {
                const firstInvalid = form.querySelector('.input-wrap.invalid input');
                if (firstInvalid) firstInvalid.focus();
                return;
            }

            Swal.fire({
                title: '¿Registrar proveedor?',
                text: 'Revisa que la información sea correcta antes de guardar.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Sí, guardar',
                cancelButtonText: 'Cancelar',
                reverseButtons: true,
                confirmButtonColor: '#3b82f6',
                cancelButtonColor: '#94a3b8'
            }).then((result) => {
                if (result.isConfirmed) form.submit();
            });
        });
    }

    // Inicializar la vista
    updateFormType();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFormProveedor);
} else {
    initFormProveedor();
}
