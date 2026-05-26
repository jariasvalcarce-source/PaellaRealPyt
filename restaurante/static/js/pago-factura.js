// =========================================
// pago-factura.js
// =========================================

// Datos dinámicos por método de pago
const instrucciones = {
    efectivo: {
        icono: 'bx-money',
        titulo: 'Pago en Efectivo',
        texto: 'Prepara el monto exacto al momento de la entrega. Nuestro repartidor llevará cambio hasta $50.000.'
    },
    nequi: {
        icono: 'bx-mobile-alt',
        titulo: 'Transferencia Nequi',
        texto: 'Envía el valor exacto al número <strong>300 123 4567</strong> con el concepto <strong>"Pedido #1042"</strong>.',
        conRef: true
    },
    bancolombia: {
        icono: 'bx-bank',
        titulo: 'Transferencia Bancolombia',
        texto: 'Transfiere a la cuenta de ahorros <strong>123-456789-00</strong> a nombre de <em>La Paella Real SAS</em>.',
        conRef: true
    },
    stripe: {
        icono: 'bxl-stripe',
        titulo: 'Pago con Tarjeta',
        texto: 'Serás redirigido de forma segura a la plataforma Stripe para ingresar los datos de tu tarjeta débito o crédito.'
    }
};

function seleccionarMetodo(metodo) {
    document.querySelectorAll('.metodo-card').forEach(c => c.classList.remove('seleccionado'));
    const card = document.getElementById('card-' + metodo);
    if (card) card.classList.add('seleccionado');

    const info = instrucciones[metodo];
    if (!info) return;

    let html = `
        <div class="instruccion-bloque">
            <i class='bx ${info.icono}'></i>
            <div>
                <h4>${info.titulo}</h4>
                <p>${info.texto}</p>
            </div>
        </div>`;

    if (info.conRef) {
        html += `
        <div class="campo-ref">
            <label>Número / Referencia de transferencia</label>
            <div class="input-icon">
                <i class='bx bx-hash'></i>
                <input type="text"
                       id="ref-pago"
                       name="referencia_pago"
                       placeholder="Ej: 123456789012"
                       maxlength="20">
            </div>
            <span class="hint">Ingresa el número de referencia que aparece en tu comprobante.</span>
        </div>`;
    }

    const contenedor = document.getElementById('campos-metodo');
    if (contenedor) contenedor.innerHTML = html;
}

function confirmarPago() {
    const metodoEl = document.querySelector('input[name="id_met_pago_fk"]:checked');
    if (!metodoEl) {
        alertaSeleccionaMetodo();
        return;
    }

    const metodo = metodoEl.value;
    const refInput = document.getElementById('ref-pago');

    if ((metodo === '2' || metodo === '3') && refInput && !refInput.value.trim()) {
        alertaReferenciaRequerida();
        return;
    }

    if (metodo === 'stripe') {
        alertaRedirigiendoStripe().then(() => {
            // window.location.href = 'stripe-checkout.html';
        });
        return;
    }

    const modalExito = document.getElementById('modalExito');
    if (modalExito) modalExito.removeAttribute('hidden');
}

function cerrarModalExitoAlClic(e) {
    const modalExito = document.getElementById('modalExito');
    if (modalExito && e.target === modalExito) {
        modalExito.setAttribute('hidden', '');
    }
}

const modalExito = document.getElementById('modalExito');
if (modalExito) {
    modalExito.addEventListener('click', cerrarModalExitoAlClic);
}

function toggleUserMenu() {
    document.getElementById('userDropdown')?.classList.toggle('show');
}

window.onclick = function(e) {
    if (!e.target.closest('.sidebar-footer')) {
        document.getElementById('userDropdown')?.classList.remove('show');
    }
};
