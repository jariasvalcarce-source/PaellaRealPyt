document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('formProveedor');

    /* Helpers */
    function setValid(wrap, msg) {
        wrap.classList.add('valid');
        wrap.classList.remove('invalid');
        if (msg) msg.textContent = '';
    }
    function setInvalid(wrap, msg, txt) {
        wrap.classList.add('invalid');
        wrap.classList.remove('valid');
        if (msg) msg.textContent = txt;
    }
    function clearState(wrap) {
        wrap.classList.remove('valid', 'invalid');
    }

    /* Validación en tiempo real por campo */
    const rules = [
        {
            id: 'nom_provee', msgId: 'msg-nom',
            validate: v => v.trim().length >= 2,
            error: 'El nombre debe tener al menos 2 caracteres'
        },
        {
            id: 'tel_provee', msgId: 'msg-tel',
            validate: v => /^\d{7,13}$/.test(v.trim()),
            error: 'Ingresa un teléfono válido (7–13 dígitos)'
        },
        {
            id: 'correo_provee', msgId: 'msg-correo',
            validate: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()),
            error: 'Ingresa un correo electrónico válido'
        },
        {
            id: 'direc_provee', msgId: 'msg-direc',
            validate: v => v.trim().length >= 5,
            error: 'La dirección debe tener al menos 5 caracteres'
        },
        {
            id: 'estado_provee', msgId: 'msg-estado',
            validate: v => v !== '',
            error: 'Selecciona un estado'
        },
    ];

    rules.forEach(({ id, msgId, validate, error }) => {
        const input = document.getElementById(id);
        const msg   = document.getElementById(msgId);
        if (!input) return;

        input.addEventListener('blur', () => {
            if (!input.value && !input.required) { clearState(input.closest('.input-wrap')); return; }
            const wrap = input.closest('.input-wrap');
            validate(input.value)
                ? setValid(wrap, msg)
                : setInvalid(wrap, msg, error);
        });

        input.addEventListener('input', () => {
            if (input.closest('.input-wrap').classList.contains('invalid')) {
                validate(input.value) && setValid(input.closest('.input-wrap'), msg);
            }
        });
    });

    /* Envío */
    if (form) {
        form.addEventListener('submit', e => {
            e.preventDefault();
            let ok = true;

            rules.forEach(({ id, msgId, validate, error }) => {
                const input = document.getElementById(id);
                const msg   = document.getElementById(msgId);
                if (!input) return;
                if (!input.value && !input.required) return;
                const wrap = input.closest('.input-wrap');
                if (!validate(input.value)) {
                    setInvalid(wrap, msg, error);
                    ok = false;
                } else {
                    setValid(wrap, msg);
                }
            });

            if (ok) {
                // TODO: enviar al backend
                alert('✅ Proveedor registrado correctamente');
            }
        });
    }
});
