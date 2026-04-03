'use strict';

/* ── Funciones Helper UI ── */
window.copiarNequi = function() {
    navigator.clipboard.writeText("3001234567").then(() => {
        Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Número copiado al portapapeles', showConfirmButton: false, timer: 2000 });
    });
};

window.calcularDevuelta = function(input) {
    const total = window.PEDIDO_TOTAL || 0;
    const pagaCon = parseFloat(input.value) || 0;
    const msgEl = document.getElementById('msg-devuelta');
    if (pagaCon >= total && pagaCon > 0) {
        msgEl.innerHTML = `<span style="color:#2b7a0b;"><i class='bx bx-check-circle'></i> Su cambio será de: <strong>$${(pagaCon - total).toLocaleString('es-CO')}</strong></span>`;
    } else if (pagaCon > 0 && pagaCon < total) {
        msgEl.innerHTML = `<span style="color:#da1f5e;"><i class='bx bx-error-circle'></i> Fondos insuficientes. Te faltan <strong>$${(total - pagaCon).toLocaleString('es-CO')}</strong></span>`;
    } else {
        msgEl.innerHTML = '';
    }
};

/* ── Instrucciones por método ── */
const INSTRUCCIONES = {
    efectivo: {
        html: `
        <div class="instruccion-bloque" style="background:#fdfcf0; padding:18px; border-radius:12px; margin-bottom:15px; display:flex; align-items:center; gap:15px; border-left:5px solid #d4a373; box-shadow:0 3px 10px rgba(0,0,0,0.03);">
            <div style="background:#fff; padding:12px; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.06);">
                <i class='bx bx-money-withdraw' style="font-size:28px; color:#d4a373;"></i>
            </div>
            <div>
                <h4 style="color:#6b4d32; margin:0 0 6px 0; font-size:16px;">Pago en Efectivo</h4>
                <p style="margin:0; font-size:14px; color:#5c5c5c; line-height:1.4;">Ten el dinero listo cuando llegue tu pedido. El repartidor llevará cambio si lo necesitas para que el cobro sea rápido.</p>
            </div>
        </div>
        <div class="campo-ref" style="background:#fff; border:1px solid #e2e8f0; padding:18px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.02);">
            <label for="montoEfectivo" style="display:flex; align-items:center; gap:6px; font-weight:600; margin-bottom:10px; color:#333; font-size:14px;">
                <i class='bx bx-money' style="color:#d4a373; font-size:18px;"></i> ¿Con cuánto vas a pagar?
            </label>
            <input id="montoEfectivo" type="number" name="monto_con_el_que_paga"
                   placeholder="Ej: 50000" autocomplete="off" oninput="window.calcularDevuelta(this)"
                   style="width:100%; padding:14px; border:2px solid #edf2f7; border-radius:8px; font-size:15px; outline:none; transition:border 0.2s;"
                   onfocus="this.style.borderColor='#d4a373'" onblur="this.style.borderColor='#edf2f7'">
            <div id="msg-devuelta" style="margin-top:10px; font-size:13.5px;"></div>
        </div>`,
        tieneReferencia: false
    },

    nequi: {
        html: `
        <div class="instruccion-bloque" style="background:#fcf3f8; padding:18px; border-radius:12px; margin-bottom:15px; display:flex; align-items:center; gap:15px; border-left:5px solid #da1f5e; box-shadow:0 3px 10px rgba(0,0,0,0.03);">
            <div style="background:#fff; padding:12px; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.06);">
                <i class='bx bx-mobile-alt' style="font-size:28px; color:#da1f5e;"></i>
            </div>
            <div style="flex:1;">
                <h4 style="color:#da1f5e; margin:0 0 6px 0; font-size:16px;">Transferencia Nequi</h4>
                <p style="margin:0; font-size:14px; color:#555; line-height:1.4;">Envía el pago al número <strong style="color:#222; font-size:15px;">300 123 4567</strong> <button type="button" onclick="window.copiarNequi()" style="background:#da1f5e; color:#fff; border:none; border-radius:4px; padding:2px 6px; cursor:pointer; font-size:12px; margin-left:5px;"><i class='bx bx-copy'></i> Copiar</button><br>con el concepto <strong style="color:#222;">Pedido #PEDIDO_ID</strong>.</p>
            </div>
        </div>
        <div class="campo-ref" style="background:#fff; border:1px solid #e2e8f0; padding:18px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.02); display:flex; flex-direction:column; gap:15px;">
            <div>
                <label for="celularOrigen" style="display:flex; align-items:center; gap:6px; font-weight:600; margin-bottom:10px; color:#333; font-size:14px;">
                    <i class='bx bx-phone' style="color:#da1f5e; font-size:18px;"></i> Celular origen Nequi
                </label>
                <input id="celularOrigen" type="text" name="celular_origen"
                       placeholder="Ej: 300 000 0000" autocomplete="off"
                       style="width:100%; padding:14px; border:2px solid #edf2f7; border-radius:8px; font-size:15px; outline:none; transition:border 0.2s;"
                       onfocus="this.style.borderColor='#da1f5e'" onblur="this.style.borderColor='#edf2f7'">
            </div>
            <div>
                <label for="comprobanteIMG" style="display:flex; align-items:center; gap:6px; font-weight:600; margin-bottom:10px; color:#333; font-size:14px;">
                    <i class='bx bx-image-add' style="color:#da1f5e; font-size:18px;"></i> Subir Pantallazo de Pago
                </label>
                <input id="comprobanteIMG" type="file" name="comprobante_img" accept="image/*"
                       style="width:100%; padding:10px; border:2px dashed #edf2f7; border-radius:8px; background:#fafafa; font-size:14px;">
            </div>
        </div>`,
        tieneReferencia: true
    },

    bancolombia: {
        html: `
        <div class="instruccion-bloque" style="background:#f4f9fd; padding:18px; border-radius:12px; margin-bottom:15px; display:flex; align-items:center; gap:15px; border-left:5px solid #00529b; box-shadow:0 3px 10px rgba(0,0,0,0.03);">
            <div style="background:#fff; padding:12px; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.06);">
                <i class='bx bx-bank' style="font-size:28px; color:#00529b;"></i>
            </div>
            <div>
                <h4 style="color:#00529b; margin:0 0 6px 0; font-size:16px;">Bancolombia / PSE</h4>
                <p style="margin:0; font-size:14px; color:#555; line-height:1.4;">Transfiere a la <strong>Cuenta de Ahorros 123-456789-00</strong><br>Titular <strong style="color:#222;">La Paella Real S.A.S.</strong> · Concepto <strong style="color:#222;">Pedido #PEDIDO_ID</strong>.</p>
            </div>
        </div>
        <div class="campo-ref" style="background:#fff; border:1px solid #e2e8f0; padding:18px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.02); display:flex; flex-direction:column; gap:15px;">
            <div>
                <label for="nombreTitular" style="display:flex; align-items:center; gap:6px; font-weight:600; margin-bottom:10px; color:#333; font-size:14px;">
                    <i class='bx bx-user' style="color:#00529b; font-size:18px;"></i> Nombre del titular girador
                </label>
                <input id="nombreTitular" type="text" name="nombre_titular"
                       placeholder="Ej: Juan Pérez" autocomplete="off"
                       style="width:100%; padding:14px; border:2px solid #edf2f7; border-radius:8px; font-size:15px; outline:none; transition:border 0.2s;"
                       onfocus="this.style.borderColor='#00529b'" onblur="this.style.borderColor='#edf2f7'">
            </div>
            <div>
                <label for="comprobanteIMGB" style="display:flex; align-items:center; gap:6px; font-weight:600; margin-bottom:10px; color:#333; font-size:14px;">
                    <i class='bx bx-file' style="color:#00529b; font-size:18px;"></i> Subir Comprobante
                </label>
                <input id="comprobanteIMGB" type="file" name="comprobante_img" accept="image/*,application/pdf"
                       style="width:100%; padding:10px; border:2px dashed #edf2f7; border-radius:8px; background:#fafafa; font-size:14px;">
            </div>
        </div>`,
        tieneReferencia: true
    }
};

/* ── Seleccionar método de pago ── */
function seleccionarMetodo(metodo) {
    document.querySelectorAll('.metodo-card').forEach(card => card.classList.remove('seleccionado'));
    const cardActiva = document.getElementById('card-' + metodo);
    if (cardActiva) cardActiva.classList.add('seleccionado');

    const pedidoIdInput = document.querySelector('input[name="pedido_id"]');
    const pedidoId = pedidoIdInput ? pedidoIdInput.value : '';

    const contenedor = document.getElementById('campos-metodo');
    const instruccion = INSTRUCCIONES[metodo];
    if (!instruccion) return;

    contenedor.innerHTML = instruccion.html.replace(/PEDIDO_ID/g, pedidoId);
    contenedor.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/* ── Toggle menú de usuario ── */
function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    const btn      = document.querySelector('.perfil-btn');
    if (!dropdown || !btn) return;
    const abierto = dropdown.classList.toggle('activo');
    btn.setAttribute('aria-expanded', String(abierto));
}
document.addEventListener('click', function (e) {
    const wrap = document.querySelector('.perfil-wrap');
    if (wrap && !wrap.contains(e.target)) {
        const dropdown = document.getElementById('userDropdown');
        const btn      = document.querySelector('.perfil-btn');
        if (dropdown) dropdown.classList.remove('activo');
        if (btn) btn.setAttribute('aria-expanded', 'false');
    }
});

/* ── Validación y envío del formulario ── */
document.addEventListener('DOMContentLoaded', function () {
    const form    = document.getElementById('formPago');
    const btnPay  = document.getElementById('btnPagar');
    if (!form || !btnPay) return;

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const metodoSeleccionado = document.querySelector('input[name="id_met_pago_fk"]:checked');
        if (!metodoSeleccionado) {
            Swal.fire({ icon: 'warning', title: 'Método de pago requerido', text: 'Por favor, selecciona cómo deseas pagar tu pedido.', confirmButtonColor: '#7f0404' });
            return;
        }

        const idMetodo = metodoSeleccionado.value;
        const metodosNombres = { "1": "Efectivo", "2": "Nequi", "3": "Bancolombia" };
        const nombreMetodo = metodosNombres[idMetodo] || "el método seleccionado";

        // Validaciones Especiales
        if (idMetodo === "1") { // Efectivo
            const montoInp = document.getElementById('montoEfectivo');
            if (!montoInp || parseFloat(montoInp.value || 0) < window.PEDIDO_TOTAL) {
                Swal.fire({ icon: 'error', title: 'Monto inválido', text: `El monto pagado debe ser igual o mayor al total del pedido ($${window.PEDIDO_TOTAL.toLocaleString('es-CO')}).`, confirmButtonColor: '#7f0404' });
                return;
            }
        } 
        else if (idMetodo === "2") { // Nequi
            const celular = document.getElementById('celularOrigen').value.trim();
            const arch = document.getElementById('comprobanteIMG').files.length;
            if (!celular || arch === 0) {
                Swal.fire({ icon: 'error', title: 'Faltan datos', text: `Por favor ingresa tu celular de origen y adjunta la captura del depósito para pagar con Nequi.`, confirmButtonColor: '#7f0404' });
                return;
            }
        }
        else if (idMetodo === "3") { // Bancolombia
            const titular = document.getElementById('nombreTitular').value.trim();
            const arch = document.getElementById('comprobanteIMGB').files.length;
            if (!titular || arch === 0) {
                Swal.fire({ icon: 'error', title: 'Faltan datos', text: `Por favor completa el nombre del titular y adjunta el comprobante para pagar con Bancolombia.`, confirmButtonColor: '#7f0404' });
                return;
            }
        }

        // Confirmación con SweetAlert
        let htmlConfirmacion = `<p>¿Confirmar el pago con <strong>${nombreMetodo}</strong>?</p>`;
        
        Swal.fire({
            title: 'Procesar Pedido',
            html: htmlConfirmacion,
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#7f0404',
            cancelButtonColor: '#6c757d',
            confirmButtonText: '<i class="bx bx-check"></i> Sí, confirmar y procesar',
            cancelButtonText: 'Revisar',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                btnPay.disabled = true;
                btnPay.innerHTML = "<i class='bx bx-loader-alt bx-spin'></i> Procesando...";
                Swal.fire({ title: 'Enviando pago...', text: 'Verificando información...', allowOutsideClick: false, didOpen: () => { Swal.showLoading(); } });
                form.submit();
            }
        });
    });
});