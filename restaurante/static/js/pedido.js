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

    if (!dir || !barrio || !fecha) {
        alertaCamposIncompletosDomicilio();
        return;
    }

    if (fecha !== hoyStr && !hora) {
        alertaCamposIncompletosDomicilio();
        return;
    }

    // No permitir fechas pasadas
    if (fecha < hoyStr) {
        alertaError('La fecha de entrega no puede ser en el pasado.');
        return;
    }

    // El horario de entrega es de 12:00 PM a 8:00 PM (solo para días futuros)
    if (fecha !== hoyStr) {
        if (hora < '12:00' || hora > '20:00') {
            alertaError('El horario de entrega programado es de 12:00 PM a 8:00 PM.');
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

    // Lógica para deshabilitar hora si la fecha es hoy
    const fechaInput = document.getElementById('fecha-domi');
    const horaInput = document.getElementById('hora-domi');
    const horaGroup = horaInput ? horaInput.closest('.campo-grupo') : null;

    if (fechaInput && horaInput) {
        function verificarFecha() {
            if (fechaInput.value === hoyStr) {
                horaInput.disabled = true;
                horaInput.value = '';
                horaInput.style.display = 'none';
                
                // Añadir un texto de "Lo antes posible"
                let txt = document.getElementById('asap-text');
                if (!txt) {
                    txt = document.createElement('div');
                    txt.id = 'asap-text';
                    txt.style.padding = '0.8rem';
                    txt.style.color = '#10b981';
                    txt.style.fontWeight = '500';
                    txt.style.background = 'rgba(16, 185, 129, 0.1)';
                    txt.style.borderRadius = '8px';
                    txt.style.marginTop = '0.5rem';
                    txt.innerHTML = "<i class='bx bx-run'></i> Se enviará lo antes posible";
                    horaInput.parentNode.appendChild(txt);
                }
                txt.style.display = 'block';
            } else {
                horaInput.disabled = false;
                horaInput.style.display = 'block';
                const txt = document.getElementById('asap-text');
                if (txt) txt.style.display = 'none';
            }
        }

        fechaInput.addEventListener('change', verificarFecha);
        verificarFecha(); // Ejecutar al inicio
    }
});
