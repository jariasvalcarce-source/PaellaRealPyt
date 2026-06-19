const input = document.getElementById('buscar-cliente');
const cards = document.querySelectorAll('.emp-card');
const grid = document.getElementById('cli-grid');
const empty = document.getElementById('cli-empty');
const counter = document.getElementById('cli-count');
const filterBtns = document.querySelectorAll('.emp-filter-btn');
let activeFilter = 'todos';

const usernameRegex = /^(?=.*[A-Z])(?=.*\d)[A-Za-z\d_]{4,20}$/;
const nameRegex = /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{2,}$/;
const phoneRegex = /^3\d{9}$/;
const emailRegex = /^[^@\s]{6,}@[a-zA-Z][a-zA-Z0-9\-\.]*\.(com|co|com\.co)$/i;

function calcularEdad(fecha) {
    if (!fecha) return 0;
    const nacimiento = new Date(fecha);
    const hoy = new Date();
    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    const mes = hoy.getMonth() - nacimiento.getMonth();
    const dia = hoy.getDate() - nacimiento.getDate();
    if (mes < 0 || (mes === 0 && dia < 0)) edad -= 1;
    return edad;
}

function setValidationState(input, valid, message) {
    const wrap = input.closest('.input-wrap');
    if (wrap) {
        wrap.classList.toggle('valid', valid);
        wrap.classList.toggle('invalid', !valid);
    }
    const msg = document.getElementById(`msg-${input.id}`);
    if (msg) {
        msg.textContent = valid ? '' : message;
    }
    return valid;
}

function validateClienteField(input) {
    const value = input.value.trim();
    switch (input.id) {
        case 'edit_usuario':
            if (!value) return setValidationState(input, false, 'El nombre de usuario es requerido.');
            if (value.includes(' ')) return setValidationState(input, false, 'No se permiten espacios.');
            if (!usernameRegex.test(value)) return setValidationState(input, false, 'Debe tener 4-20 caracteres, mayúscula y número.');
            return setValidationState(input, true, '');
        case 'edit_nom':
        case 'edit_apellido':
            if (!value) return setValidationState(input, false, 'Este campo es obligatorio.');
            if (!nameRegex.test(value)) return setValidationState(input, false, 'Solo letras y espacios, mínimo 2 caracteres.');
            return setValidationState(input, true, '');
        case 'edit_fecha':
            if (!value) return setValidationState(input, false, 'Ingrese la fecha de nacimiento.');
            if (calcularEdad(value) < 15) return setValidationState(input, false, 'Debes tener al menos 15 años.');
            return setValidationState(input, true, '');
        case 'edit_tel':
            if (!value) return setValidationState(input, false, 'El teléfono es obligatorio.');
            if (!phoneRegex.test(value)) return setValidationState(input, false, 'Teléfono inválido, debe iniciar con 3 y tener 10 dígitos.');
            return setValidationState(input, true, '');
        case 'edit_correo':
            if (!value) return setValidationState(input, false, 'El correo es obligatorio.');
            if (!emailRegex.test(value)) return setValidationState(input, false, 'Por favor, ingresa un correo válido que termine en .com o .co.');
            return setValidationState(input, true, '');
        case 'edit_direc':
            if (!value) return setValidationState(input, false, 'La dirección es obligatoria.');
            if (value.length < 5) return setValidationState(input, false, 'La dirección debe tener al menos 5 caracteres.');
            return setValidationState(input, true, '');
        default:
            return true;
    }
}

function validateEditForm() {
    const editInputs = Array.from(document.querySelectorAll('#editForm input'));
    let isFormValid = true;
    let firstInvalid = null;

    editInputs.forEach(input => {
        const valid = validateClienteField(input);
        if (!valid && !firstInvalid) {
            firstInvalid = input;
            isFormValid = false;
        }
    });

    if (!isFormValid && firstInvalid) {
        firstInvalid.focus();
    }
    return isFormValid;
}

function filterCards() {
    const q = input.value.toLowerCase().trim();
    let visible = 0;

    cards.forEach(card => {
        const matchSearch = !q
            || card.dataset.nombre.toLowerCase().includes(q)
            || card.dataset.correo.toLowerCase().includes(q)
            || card.dataset.telefono.includes(q);
        const matchFilter = activeFilter === 'todos' || card.dataset.estado === activeFilter;
        const show = matchSearch && matchFilter;

        card.style.display = show ? '' : 'none';
        if (show) visible++;
    });

    counter.textContent = visible;
    empty.style.display = visible === 0 ? 'flex' : 'none';
    grid.style.display = visible === 0 ? 'none' : '';
}

function initializeFilters() {
    if (input) {
        input.addEventListener('input', filterCards);
    }
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeFilter = btn.dataset.filter;
            filterCards();
        });
    });
}

function initializeLogoUpload() {
    const logoUpload = document.getElementById('logo-upload');
    const logoImg = document.getElementById('logo-img');
    const logoPlaceholder = document.getElementById('logo-placeholder');

    if (logoImg && logoPlaceholder) {
        logoImg.addEventListener('error', () => {
            logoImg.style.display = 'none';
            logoPlaceholder.style.display = 'flex';
        });
    }

    if (logoUpload && logoImg && logoPlaceholder) {
        logoUpload.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (ev) {
                logoImg.src = ev.target.result;
                logoImg.style.display = 'block';
                logoPlaceholder.style.display = 'none';
            };
            reader.readAsDataURL(file);
        });
    }
}

function initTablaCliente() {
    initializeFilters();
    initializeLogoUpload();

    const editForm = document.getElementById('editForm');
    if (editForm) {
        const editInputs = Array.from(editForm.querySelectorAll('input'));
        editInputs.forEach(input => {
            input.addEventListener('blur', () => validateClienteField(input));
            input.addEventListener('input', () => {
                if (input.closest('.input-wrap')?.classList.contains('invalid')) {
                    validateClienteField(input);
                }
            });
        });

        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!validateEditForm()) {
                return;
            }

            Swal.fire({
                title: '¿Estás seguro?',
                text: 'Se actualizarán los datos de este cliente.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: 'var(--primary)',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Sí, guardar cambios',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    editForm.submit();
                }
            });
        });
    }


    // Mensajes de Django ahora se manejan globalmente por premium-alerts.js

}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTablaCliente);
} else {
    initTablaCliente();
}
