// =========================================
// pedido.js
// =========================================

// ── Fechas mínimas ──────────────────────────────
const hoy = new Date();
const hoyStr = hoy.toISOString().split('T')[0];

// Domicilio: no se puede pedir para ayer ni para el pasado
const fechaDomi = document.getElementById('fecha-domi');
if (fechaDomi) {
    fechaDomi.min = hoyStr;
}

// ── Validar antes de continuar ──────────────────
function validarYContinuar() {
    const dir = document.querySelector('[name="direc_domi"]').value.trim();
    const barrio = document.querySelector('[name="id_barrio_domi_fk"]').value;
    const fecha = document.querySelector('[name="fecha_domi"]').value;
    const hora = document.querySelector('[name="hora_entrega_domi"]').value;

    if (!dir || !barrio) {
        alertaCamposIncompletosDomicilio();
        return;
    }

    // No permitir fechas pasadas
    if (fecha < hoyStr) {
        alertaError('La fecha de entrega no puede ser en el pasado.');
        return;
    }

    // Eliminadas validaciones de hora/fecha porque ahora es siempre inmediato

    // Enviar el formulario al backend
    document.getElementById('formCrearPedido').submit();
}

// ── Función auxiliar para errores ────────────────
function alertaError(mensaje) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({ icon: 'error', title: 'Error', text: mensaje });
    } else {
        alert(mensaje);
    }
}

// Habilitar botón continuar por defecto y setear fecha de hoy
document.addEventListener("DOMContentLoaded", function() {
    const botonContinuar = document.getElementById('btn-continuar');
    if (botonContinuar) botonContinuar.disabled = false;

    // Asignar siempre la fecha de hoy al campo oculto
    const fechaInput = document.getElementById('fecha-domi');
    if (fechaInput) {
        fechaInput.value = hoyStr;
    }
});
