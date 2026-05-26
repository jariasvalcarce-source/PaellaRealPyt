// =========================================
// pedido.js
// =========================================

// ── Fechas mínimas ──────────────────────────────
const hoy = new Date().toISOString().split('T')[0];
document.getElementById('fecha-domi').min = hoy;

const minEvento = new Date();
minEvento.setDate(minEvento.getDate() + 3);
document.getElementById('fecha-evento').min = minEvento.toISOString().split('T')[0];

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
    }

    // Enviar el formulario al backend
    document.getElementById('formCrearPedido').submit();
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
