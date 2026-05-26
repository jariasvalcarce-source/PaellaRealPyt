/* ================================================
    Validaciones del formulario Registrar Empleado
================================================ */

'use strict';

/**
 * Marca un campo como válido visualmente.
 * @param {HTMLElement} wrap   - El .input-wrap del campo
 * @param {HTMLElement} msgEl  - El span .field-msg (puede ser null)
 * @param {string}      [msg]  - Texto informativo opcional (gris)
 */
function marcarValido(wrap, msgEl, msg) {
    wrap.classList.add('valid');
    wrap.classList.remove('invalid');
    if (msgEl) {
        msgEl.textContent = msg || '';
        msgEl.className   = msg ? 'field-msg info' : 'field-msg';
    }
}

/**
 * Marca un campo como inválido visualmente.
 * @param {HTMLElement} wrap   - El .input-wrap del campo
 * @param {HTMLElement} msgEl  - El span .field-msg (puede ser null)
 * @param {string}      msg    - Mensaje de error
 */
function marcarInvalido(wrap, msgEl, msg) {
    wrap.classList.add('invalid');
    wrap.classList.remove('valid');
    if (msgEl) {
        msgEl.textContent = msg;
        msgEl.className   = 'field-msg';
    }
}

/**
 * Limpia el estado visual de un campo.
 */
function limpiarEstado(wrap, msgEl) {
    wrap.classList.remove('valid', 'invalid');
    if (msgEl) { msgEl.textContent = ''; msgEl.className = 'field-msg'; }
}

/** Calcula la edad en años completos a partir de una fecha (Date). */
function calcularEdad(fecha) {
    var hoy  = new Date();
    var edad = hoy.getFullYear() - fecha.getFullYear();
    var m    = hoy.getMonth() - fecha.getMonth();
    if (m < 0 || (m === 0 && hoy.getDate() < fecha.getDate())) edad--;
    return edad;
}


/* ================================================
    SECCIÓN 1 — INFORMACIÓN PERSONAL
================================================ */

/* ── Foto del empleado ── */
function validarFoto(input) {
    var msgEl = document.getElementById('msg-foto');
    var wrap  = input.closest('.photo-preview') || input.parentElement;

    if (!input.files || input.files.length === 0) {
        return true; // Foto es opcional
    }

    var file      = input.files[0];
    var extensión = file.name.split('.').pop().toLowerCase();
    var tiposOK   = ['jpg', 'jpeg', 'png'];
    var maxBytes  = 2 * 1024 * 1024; // 2 MB

    if (!tiposOK.includes(extensión)) {
        if (msgEl) { msgEl.textContent = 'Solo se permiten imágenes JPG o PNG.'; msgEl.className = 'field-msg'; }
        return false;
    }
    if (file.size > maxBytes) {
        if (msgEl) { msgEl.textContent = 'La imagen no puede superar los 2 MB.'; msgEl.className = 'field-msg'; }
        return false;
    }
    if (msgEl) { msgEl.textContent = ''; }
    return true;
}

/* ── Nombres ── */
function validarNombres() {
    var input = document.getElementById('nom_empleado');
    var wrap  = input.closest('.input-wrap');
    var msgEl = document.getElementById('msg-nom');
    var val   = input.value.trim();
    var regex = /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/;

    if (val === '') {
        marcarInvalido(wrap, msgEl, 'El nombre es obligatorio.');
        return false;
    }
    if (val.length < 2 || val.length > 50) {
        marcarInvalido(wrap, msgEl, 'Debe tener entre 2 y 50 caracteres.');
        return false;
    }
    if (!regex.test(val)) {
        marcarInvalido(wrap, msgEl, 'Solo se permiten letras y espacios.');
        return false;
    }
    marcarValido(wrap, msgEl);
    return true;
}

/* ── Apellidos ── */
function validarApellidos() {
    var input = document.getElementById('apellido_empleado');
    var wrap  = input.closest('.input-wrap');
    var msgEl = document.getElementById('msg-ape');
    var val   = input.value.trim();
    var regex = /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/;

    if (val === '') {
        marcarInvalido(wrap, msgEl, 'Los apellidos son obligatorios.');
        return false;
    }
    if (val.length < 2 || val.length > 50) {
        marcarInvalido(wrap, msgEl, 'Debe tener entre 2 y 50 caracteres.');
        return false;
    }
    if (!regex.test(val)) {
        marcarInvalido(wrap, msgEl, 'Solo se permiten letras y espacios.');
        return false;
    }
    marcarValido(wrap, msgEl);
    return true;
}

/* ── Fecha de nacimiento ── */
function validarFechaNacimiento() {
    var input = document.getElementById('fecha_naci_empleado');
    var wrap  = input.closest('.input-wrap');
    var msgEl = document.getElementById('msg-fecha');
    var val   = input.value;

    if (!val) {
        marcarInvalido(wrap, msgEl, 'La fecha de nacimiento es obligatoria.');
        return false;
    }

    var fecha = new Date(val);
    if (isNaN(fecha.getTime())) {
        marcarInvalido(wrap, msgEl, 'Ingresa una fecha válida.');
        return false;
    }

    var edad = calcularEdad(fecha);
    if (edad < 14) {
        marcarInvalido(wrap, msgEl, 'El empleado debe tener al menos 14 años.');
        return false;
    }
    if (edad > 100) {
        marcarInvalido(wrap, msgEl, 'Verifica la fecha ingresada.');
        return false;
    }

    marcarValido(wrap, msgEl, edad + ' años');
    return true;
}

/* ── Tipo de documento ── */
function validarTipoDoc() {
    var input = document.getElementById('tipo_doc');
    var wrap  = input.closest('.input-wrap');

    if (!input.value) {
        marcarInvalido(wrap, null, '');
        return false;
    }
    marcarValido(wrap, null);
    return true;
}

/* ── Número de documento ── */
function validarNumDoc() {
    var input = document.getElementById('num_doc');
    var wrap  = input.closest('.input-wrap');
    var val   = input.value.trim();
    var regex = /^[0-9]{6,12}$/;

    if (val === '') {
        marcarInvalido(wrap, null, '');
        return false;
    }
    if (!regex.test(val)) {
        marcarInvalido(wrap, null, '');
        return false;
    }
    marcarValido(wrap, null);
    return true;
}

/* ── Cargo ── */
function validarCargo() {
    var input = document.getElementById('cargo_empleado');
    if (!input) return true;
    var wrap  = input.closest('.input-wrap');

    if (!input.value) {
        marcarInvalido(wrap, null, '');
        return false;
    }
    marcarValido(wrap, null);
    return true;
}


/* ================================================
    SECCIÓN 2 — INFORMACIÓN DE CONTACTO
================================================ */

/* ── Teléfono (celular colombiano) ── */
function validarTelefono() {
    var input = document.getElementById('tel_empleado');
    var wrap  = input.closest('.input-wrap');
    var val   = input.value.trim();

    /*
     * Reglas:
     *  - Exactamente 10 dígitos
     *  - Debe iniciar con 3
     *  Prefijos válidos conocidos (3XX):
     *  Claro:    300-304, 310-312, 320-323
     *  Movistar: 313-316, 318
     *  Tigo:     305-307, 319
     *  WOM:      350-351
     *  (otros prefijos con 3 también se aceptan por portabilidad numérica)
     */
    var regexBase   = /^3[0-9]{9}$/;
    var prefijosOK  = /^3(0[0-9]|1[0-9]|2[0-9]|5[01])/;

    if (val === '') {
        marcarInvalido(wrap, null, '');
        return false;
    }
    if (!/^[0-9]+$/.test(val)) {
        marcarInvalido(wrap, null, '');
        return false;
    }
    if (!regexBase.test(val)) {
        marcarInvalido(wrap, null, '');
        return false;
    }
    if (!prefijosOK.test(val)) {
        marcarInvalido(wrap, null, '');
        return false;
    }
    marcarValido(wrap, null);
    return true;
}

/* ── Correo electrónico ── */
function validarCorreo() {
    var input = document.getElementById('correo_empleado');
    var wrap  = input.closest('.input-wrap');
    var val   = input.value.trim();

    /*
     * Reglas:
     *  - No puede iniciar con número
     *  - Debe tener dominio con TLD de al menos 2 caracteres
     *  - No se permiten correos incompletos (ej: smsms@1)
     */
    var regex = /^[a-zA-Z][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;

    if (val === '') {
        marcarInvalido(wrap, null, '');
        return false;
    }
    if (!regex.test(val)) {
        marcarInvalido(wrap, null, '');
        return false;
    }
    marcarValido(wrap, null);
    return true;
}

/* ── Dirección ── */
function validarDireccion() {
    var input = document.getElementById('direc_empleado');
    var wrap  = input.closest('.input-wrap');
    var val   = input.value.trim();
    var regex = /^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s#\-.]+$/;

    if (val === '') {
        marcarInvalido(wrap, null, '');
        return false;
    }
    if (val.length < 5 || val.length > 100) {
        marcarInvalido(wrap, null, '');
        return false;
    }
    if (!regex.test(val)) {
        marcarInvalido(wrap, null, '');
        return false;
    }
    marcarValido(wrap, null);
    return true;
}


/* ================================================═
    SECCIÓN 3 — DATOS DEL CONTRATO
================================================ */

/* ── Fecha de ingreso ── */
function validarFechaIngreso() {
    var input      = document.getElementById('fecha_ingreso');
    var wrap       = input.closest('.input-wrap');
    var msgEl      = document.getElementById('msg-ingreso');
    var val        = input.value;
    var inputNaci  = document.getElementById('fecha_naci_empleado');

    if (!val) {
        marcarInvalido(wrap, msgEl, 'La fecha de ingreso es obligatoria.');
        return false;
    }

    var fecha = new Date(val);
    var hoy   = new Date();
    hoy.setHours(0, 0, 0, 0);

    if (isNaN(fecha.getTime())) {
        marcarInvalido(wrap, msgEl, 'Ingresa una fecha válida.');
        return false;
    }
    if (fecha > hoy) {
        marcarInvalido(wrap, msgEl, 'La fecha de ingreso no puede ser futura.');
        return false;
    }
    if (inputNaci && inputNaci.value) {
        var naci = new Date(inputNaci.value);
        if (fecha < naci) {
            marcarInvalido(wrap, msgEl, 'No puede ser anterior a la fecha de nacimiento.');
            return false;
        }
    }

    marcarValido(wrap, msgEl);
    return true;
}

/* ── Tipo de contrato ── */
function validarTipoContrato() {
    var input = document.getElementById('tipo_contrato');
    var wrap  = input.closest('.input-wrap');

    if (!input.value) {
        marcarInvalido(wrap, null, '');
        return false;
    }
    marcarValido(wrap, null);
    return true;
}

/* ── Salario mensual ── */
function validarSalario() {
    var input = document.getElementById('salario_empleado');
    var wrap  = input.closest('.input-wrap');
    var val   = input.value.trim();

    if (val === '') {
        marcarInvalido(wrap, null, '');
        return false;
    }

    var num = parseFloat(val);

    if (isNaN(num) || num <= 0) {
        marcarInvalido(wrap, null, '');
        return false;
    }

    // Máximo 2 decimales
    if (!/^\d+(\.\d{1,2})?$/.test(val)) {
        marcarInvalido(wrap, null, '');
        return false;
    }

    marcarValido(wrap, null);
    return true;
}


/* ================================================
    VALIDACIÓN GENERAL AL ENVIAR
================================================ */
function validarFormularioCompleto() {
    var fotoInput = document.getElementById('photoInput');
    var fotoOk    = true;
    var msgFoto   = document.getElementById('msg-foto');

    if (!fotoInput.files || fotoInput.files.length === 0) {
        fotoOk = true; // Foto opcional
    } else {
        fotoOk = validarFoto(fotoInput);
    }

    var resultados = [
        fotoOk,
        validarNombres(),
        validarApellidos(),
        validarFechaNacimiento(),
        validarTipoDoc(),
        validarNumDoc(),
        validarCargo(),
        validarTelefono(),
        validarCorreo(),
        validarDireccion(),
        validarFechaIngreso(),
        validarTipoContrato(),
        validarSalario()
    ];

    return resultados.every(function (r) { return r === true; });
}


/* ================================================
    EVENTOS — VALIDACIÓN EN TIEMPO REAL
================================================ */
document.addEventListener('DOMContentLoaded', function () {

    /* Foto */
    var photoInput = document.getElementById('photoInput');
    if (photoInput) {
        photoInput.addEventListener('change', function () { validarFoto(this); });
    }

    /* Texto / select con su función específica */
    var mapaEventos = {
        'nom_empleado':        { fn: validarNombres,       ev: ['input', 'blur'] },
        'apellido_empleado':   { fn: validarApellidos,     ev: ['input', 'blur'] },
        'fecha_naci_empleado': { fn: validarFechaNacimiento, ev: ['change', 'blur'] },
        'tipo_doc':            { fn: validarTipoDoc,        ev: ['change'] },
        'num_doc':             { fn: validarNumDoc,         ev: ['input', 'blur'] },
        'cargo_empleado':      { fn: validarCargo,          ev: ['change'] },
        'tel_empleado':        { fn: validarTelefono,       ev: ['input', 'blur'] },
        'correo_empleado':     { fn: validarCorreo,         ev: ['input', 'blur'] },
        'direc_empleado':      { fn: validarDireccion,      ev: ['input', 'blur'] },
        'fecha_ingreso':       { fn: validarFechaIngreso,   ev: ['change', 'blur'] },
        'tipo_contrato':       { fn: validarTipoContrato,   ev: ['change'] },
        'salario_empleado':    { fn: validarSalario,        ev: ['input', 'blur'] }
    };

    Object.keys(mapaEventos).forEach(function (id) {
        var el    = document.getElementById(id);
        var cfg   = mapaEventos[id];
        if (!el) return;
        cfg.ev.forEach(function (evento) {
            el.addEventListener(evento, cfg.fn);
        });
    });

    /* Envío del formulario */
    var form = document.getElementById('formEmpleado');
    if (form) {
        form.addEventListener('submit', function (e) {
            // Permitir el envío natural HTML5/Django
            validarFormularioCompleto(); // Solo para estilos visuales
            // No usar e.preventDefault() ni form.submit() manual
        });
    }
});

/* ================================================
    PREVIEW FOTO DEL EMPLEADO
================================================ */
function bindPhotoPreview() {
    var photoInput = document.getElementById('photoInput');
    if (!photoInput) return;

    photoInput.addEventListener('change', function (e) {
        var file = e.target.files[0];
        if (!file) return;

        var reader = new FileReader();
        reader.onload = function (ev) {
            var preview = document.getElementById('photoPreview');
            preview.innerHTML =
                '<img src="' + ev.target.result + '" alt="Foto empleado" />' +
                '<input type="file" accept="image/jpeg,image/png" id="photoInput" title="Cambiar foto" />';
            bindPhotoPreview(); // re-bind en el nuevo input
        };
        reader.readAsDataURL(file);
    });
}

/* ================================================
    CAMBIAR LOGO DEL SIDEBAR
================================================ */
function bindLogoUpload() {
    var logoUpload = document.getElementById('logo-upload');
    if (!logoUpload) return;

    logoUpload.addEventListener('change', function (e) {
        var file = e.target.files[0];
        if (!file) return;
        var reader = new FileReader();
        reader.onload = function (ev) {
            document.getElementById('logo-img').src = ev.target.result;
        };
        reader.readAsDataURL(file);
    });
}

/* Inicializar preview y logo al cargar */
document.addEventListener('DOMContentLoaded', function () {
    bindPhotoPreview();
    bindLogoUpload();
    
    // --- Lógica de SweetAlert2 para Toasts ---
    if (typeof Swal !== 'undefined') {
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 4000,
            timerProgressBar: true,
            background: '#fff',
            color: '#333',
            didOpen: (toast) => {
                toast.onmouseenter = Swal.stopTimer;
                toast.onmouseleave = Swal.resumeTimer;
            }
        });

        const msgs = document.querySelectorAll('.django-message');
        msgs.forEach(msg => {
            Toast.fire({
                icon: msg.getAttribute('data-type'),
                title: msg.innerText
            });
        });
        
        // --- Confirmación de Envío del Formulario ---
        const formEmpleado = document.getElementById('formEmpleado');
        if (formEmpleado) {
            formEmpleado.addEventListener('submit', function(e) {
                e.preventDefault();
                // Validar usando checkValidity de HTML5
                if (!this.checkValidity()) {
                    this.reportValidity();
                    return;
                }
                
                Swal.fire({
                    title: '¿Registrar Empleado?',
                    text: "Se guardarán los datos de este nuevo empleado.",
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: 'var(--primary)',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Sí, registrar',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        this.submit();
                    }
                });
            });
        }
    }
});