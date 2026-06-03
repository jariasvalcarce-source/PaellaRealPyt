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

// Evento: mínimo 7 días de anticipación
const fechaEvento = document.getElementById('fecha-evento');
if (fechaEvento) {
    const minEvento = new Date();
    minEvento.setDate(hoy.getDate() + 7);
    fechaEvento.min = minEvento.toISOString().split('T')[0];
}

// ── Hora fin debe ser al menos 1h después del inicio ──
const horaInicioEvento = document.getElementById('hora-inicio-evento');
if (horaInicioEvento) {
    horaInicioEvento.addEventListener('change', function () {
        const horaFin = document.getElementById('hora-fin-evento');
        if (this.value && horaFin) {
            const [h, m] = this.value.split(':').map(Number);
            const minFin = String(h + 1).padStart(2, '0') + ':' + String(m).padStart(2, '0');
            horaFin.min = minFin;
            if (horaFin.value && horaFin.value <= this.value) {
                horaFin.value = '';
            }
        }
    });
}

// ── Seleccionar tipo de pedido ──────────────────
function seleccionarTipo(tipo) {
    document.getElementById('radio-' + tipo).checked = true;

    document.querySelectorAll('.tipo-opcion').forEach(o => o.classList.remove('selected'));
    document.getElementById('opt-' + tipo).classList.add('selected');

    document.querySelectorAll('.form-section').forEach(s => s.classList.remove('visible'));
    document.getElementById('seccion-' + tipo).classList.add('visible');

    const botonContinuar = document.getElementById('btn-continuar');
    if (botonContinuar) botonContinuar.disabled = false;
}

// ── Validar antes de continuar ──────────────────
function validarYContinuar() {
    const tipo = document.querySelector('input[name="tipo_pedido"]:checked');
    if (!tipo) return;

    if (tipo.value === 'domicilio') {
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

        // No permitir hora después de las 8 PM
        if (hora >= '20:00') {
            alertaError('La hora de entrega no puede ser después de las 8:00 PM.');
            return;
        }

        // Si es hoy, bloquear si ya pasaron las 8 PM
        if (hoy.getHours() >= 20) {
            alertaError('No se pueden realizar pedidos después de las 8:00 PM.');
            return;
        }
    }

    if (tipo.value === 'evento') {
        const nom = document.querySelector('[name="nom_evento"]').value.trim();
        const tipoEv = document.querySelector('[name="id_tipo_evento_fk"]').value;
        const fecha = document.querySelector('[name="fecha_evento"]').value;
        const cant = document.querySelector('[name="cant_invi_evento"]').value;
        const hi = document.querySelector('[name="hora_inicio_evento"]').value;
        const hf = document.querySelector('[name="hora_fin_evento"]').value;
        const ubi = document.querySelector('[name="ubi_evento"]').value.trim();
        const mesa = document.querySelector('[name="id_mesa_evento_fk"]').value;

        if (!nom || !tipoEv || !fecha || !cant || !hi || !hf || !ubi || !mesa) {
            alertaCamposIncompletosEvento();
            return;
        }

        // Mínimo 7 días de anticipación
        const minEvento = new Date();
        minEvento.setDate(hoy.getDate() + 7);
        const minEventoStr = minEvento.toISOString().split('T')[0];
        if (fecha < minEventoStr) {
            alertaError('Los eventos deben reservarse con al menos una semana de anticipación.');
            return;
        }

        // Horario entre 8 AM y 11 PM
        if (hi < '08:00' || hf > '23:00') {
            alertaError('El horario del evento debe estar entre las 8:00 AM y las 11:00 PM.');
            return;
        }

        // Invitados 1-500
        const cantNum = parseInt(cant, 10);
        if (isNaN(cantNum) || cantNum <= 0 || cantNum > 500) {
            alertaError('La cantidad de invitados debe ser entre 1 y 500.');
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

// ── Dropdown usuario ────────────────────────────
function toggleUserMenu() {
    document.getElementById('userDropdown').classList.toggle('show');
}

window.onclick = function (e) {
    if (!e.target.closest('.sidebar-footer')) {
        document.getElementById('userDropdown').classList.remove('show');
    }
};
