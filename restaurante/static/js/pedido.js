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

    if (!dir || !barrio || !fecha || !hora) {
        alertaCamposIncompletosDomicilio();
        return;
    }

    // No permitir fechas pasadas
    if (fecha < hoyStr) {
        alertaError('La fecha de entrega no puede ser en el pasado.');
        return;
    }

    // El horario de entrega es de 12:00 PM a 8:00 PM
    if (hora < '12:00' || hora > '20:00') {
        alertaError('El horario de entrega es de 12:00 PM a 8:00 PM.');
        return;
    }

    // Si es hoy, validar que la hora sea al menos 2 horas a partir de ahora
    if (fecha === hoyStr) {
        const [h, m] = hora.split(':').map(Number);
        const fechaEntrega = new Date();
        fechaEntrega.setHours(h, m, 0, 0);

        const ahora = new Date();
        const diferenciaMs = fechaEntrega - ahora;
        const diferenciaHoras = diferenciaMs / (1000 * 60 * 60);

        if (diferenciaMs < 0) {
            alertaError('La hora de entrega no puede ser anterior a la hora actual.');
            return;
        }

        if (diferenciaHoras < 2) {
            alertaError('La hora de entrega debe ser al menos con 2 horas de anticipación a partir de la hora actual para pedidos del mismo día.');
            return;
        }
    }

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

// Habilitar botón continuar por defecto
document.addEventListener("DOMContentLoaded", function() {
    const botonContinuar = document.getElementById('btn-continuar');
    if (botonContinuar) botonContinuar.disabled = false;
});

