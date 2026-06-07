// =========================================
// pago-factura.js
// =========================================

// Total del pedido (se inyecta desde el HTML via data-attribute)
const totalPedido = parseFloat(document.getElementById('formPago')?.dataset.total || 0);
const pedidoId = document.querySelector('input[name="pedido_id"]')?.value || '';

// ── Plantillas de campos dinámicos por método ──

function camposEfectivo() {
    return `
        <div class="instruccion-bloque">
            <i class='bx bx-money'></i>
            <div>
                <h4>Pago en Efectivo</h4>
                <p>Prepara el monto al momento de la entrega. Nuestro repartidor llevará cambio.</p>
            </div>
        </div>

        <div class="campo-ref">
            <label>¿Con cuánto vas a pagar?</label>
            <div class="input-icon">
                <i class='bx bx-dollar'></i>
                <input type="text"
                       id="monto-efectivo-vista"
                       placeholder="Ej: 100.000"
                       oninput="formatearMonto(this); calcularDevuelta()"
                       required>
                <input type="hidden"
                       id="monto-efectivo"
                       name="monto_con_el_que_paga">
            </div>
            <span class="hint">Mínimo: $${totalPedido.toLocaleString('es-CO')} (total del pedido)</span>
        </div>

        <div id="devuelta-info" class="devuelta-box" style="display:none;">
            <i class='bx bx-transfer'></i>
            <div>
                <span class="devuelta-label">Tu devuelta será:</span>
                <span class="devuelta-valor" id="devuelta-valor">$0</span>
            </div>
        </div>
    `;
}

function camposNequi() {
    return `
        <div class="instruccion-bloque nequi-instruc">
            <i class='bx bx-mobile'></i>
            <div>
                <h4>Transfiere desde tu Nequi</h4>
                <p>Abre la app y envía <strong>$${totalPedido.toLocaleString('es-CO')}</strong> al <strong>300 123 4567</strong>.</p>
            </div>
        </div>
        <div class="pasos-pago">
            <div class="paso-item"><span class="paso-num">1</span> Abre tu app Nequi.</div>
            <div class="paso-item"><span class="paso-num">2</span> Transfiere el monto exacto al número indicado.</div>
            <div class="paso-item"><span class="paso-num">3</span> Anota el número de comprobante/aprobación.</div>
            <div class="paso-item"><span class="paso-num">4</span> Toma un pantallazo y llena los datos aquí.</div>
        </div>
        <div class="campo-ref">
            <label>Tu número de celular Nequi <span class="txt-rojo">*</span></label>
            <div class="input-icon">
                <i class='bx bx-phone'></i>
                <input type="number" id="celular-nequi" name="celular_origen" placeholder="Ej: 3001234567" required>
            </div>
            <span class="hint">El número desde donde nos enviaste el dinero.</span>
        </div>
        <div class="campo-ref">
            <label>Número de Aprobación o Referencia <span class="txt-rojo">*</span></label>
            <div class="input-icon">
                <i class='bx bx-hash'></i>
                <input type="text" id="ref-nequi" name="referencia_pago" placeholder="Ej: 123456" oninput="this.value = this.value.replace(/[^0-9]/g, '')" required>
            </div>
        </div>
        <div class="campo-ref">
            <label>Comprobante de pago <span class="txt-rojo">*</span></label>
            <label for="comprobante-nequi" class="upload-area">
                <i class='bx bx-upload'></i>
                <span>Toca para subir imagen</span>
                <small>Formatos: JPG, PNG (Máx 5MB)</small>
                <div class="upload-nombre" id="nombre-archivo-nequi"></div>
            </label>
            <input type="file" id="comprobante-nequi" name="comprobante_img" accept="image/jpeg, image/png" style="display: none;" onchange="mostrarPreview(this, 'nombre-archivo-nequi')" required>
        </div>
    `;
}

function camposBancolombia() {
    return `
        <div class="instruccion-bloque banco-instruc">
            <i class='bx bxs-bank'></i>
            <div>
                <h4>Transferencia App Personas</h4>
                <p>Transfiere <strong>$${totalPedido.toLocaleString('es-CO')}</strong> a la Cuenta de Ahorros <strong>987-654321-00</strong>.</p>
            </div>
        </div>

        <div class="pasos-pago">
            <div class="paso-item"><span class="paso-num">1</span> Abre tu App Personas Bancolombia</div>
            <div class="paso-item"><span class="paso-num">2</span> Transfiere el monto a nuestra cuenta</div>
            <div class="paso-item"><span class="paso-num">3</span> Copia el número de comprobante (9 dígitos)</div>
            <div class="paso-item"><span class="paso-num">4</span> Completa los datos y sube tu pantallazo</div>
        </div>

        <div class="campo-ref">
            <label>Nombre del titular de la cuenta</label>
            <div class="input-icon">
                <i class='bx bx-user'></i>
                <input type="text" id="titular-banco" name="nombre_titular" placeholder="Nombre completo" required>
            </div>
        </div>

        <div class="campo-ref">
            <label>Número de Comprobante <span class="txt-rojo">*</span></label>
            <div class="input-icon">
                <i class='bx bx-hash'></i>
                <input type="text"
                       id="ref-banco"
                       name="referencia_pago"
                       placeholder="Ej: 123456789"
                       oninput="this.value = this.value.replace(/[^0-9]/g, '')"
                       maxlength="9"
                       required>
            </div>
        </div>

        <div class="campo-ref">
            <label>Comprobante de pago (pantallazo o PDF)</label>
            <div class="upload-area" id="upload-area-banco" onclick="document.getElementById('comprobante-banco').click()">
                <i class='bx bx-cloud-upload'></i>
                <span>Haz clic o arrastra tu comprobante aquí</span>
                <small>JPG, PNG o PDF · Máx 5 MB</small>
            </div>
            <input type="file"
                   id="comprobante-banco"
                   name="comprobante_img"
                   accept="image/*,.pdf"
                   style="display:none"
                   onchange="mostrarPreview(this, 'upload-area-banco')">
        </div>
    `;
}

function camposStripe() {
    return `
        <div class="instruccion-bloque stripe-instruc">
            <i class='bx bx-credit-card'></i>
            <div>
                <h4>Pago con Tarjeta (Stripe)</h4>
                <p>Serás redirigido a la plataforma segura de <strong>Stripe</strong> para ingresar los datos de tu tarjeta débito o crédito.</p>
            </div>
        </div>

        <div class="stripe-seguridad">
            <div class="seguridad-item">
                <i class='bx bx-lock-alt'></i>
                <span>Conexión cifrada SSL</span>
            </div>
            <div class="seguridad-item">
                <i class='bx bx-shield-quarter'></i>
                <span>Procesado por Stripe</span>
            </div>
            <div class="seguridad-item">
                <i class='bx bx-check-shield'></i>
                <span>No guardamos tus datos</span>
            </div>
        </div>

        <div class="stripe-total-box">
            <span>Total a cobrar:</span>
            <strong>$${totalPedido.toLocaleString('es-CO')} COP</strong>
        </div>
    `;
}

// ── Seleccionar método ──

function seleccionarMetodo(metodo) {
    document.querySelectorAll('.metodo-card').forEach(c => c.classList.remove('seleccionado'));
    const card = document.getElementById('card-' + metodo);
    if (card) card.classList.add('seleccionado');

    const contenedor = document.getElementById('campos-metodo');
    if (!contenedor) return;

    const btnPagar = document.getElementById('btnPagar');

    switch (metodo) {
        case 'efectivo':
            contenedor.innerHTML = camposEfectivo();
            btnPagar.textContent = '';
            btnPagar.innerHTML = "<i class='bx bx-money'></i> Confirmar Pago en Efectivo";
            btnPagar.onclick = null;
            btnPagar.type = 'submit';
            break;
        case 'nequi':
            contenedor.innerHTML = camposNequi();
            btnPagar.textContent = '';
            btnPagar.innerHTML = "<i class='bx bx-check-circle'></i> Confirmar Pago Nequi";
            btnPagar.onclick = null;
            btnPagar.type = 'submit';
            break;
        case 'bancolombia':
            contenedor.innerHTML = camposBancolombia();
            btnPagar.textContent = '';
            btnPagar.innerHTML = "<i class='bx bx-check-circle'></i> Confirmar Transferencia";
            btnPagar.onclick = null;
            btnPagar.type = 'submit';
            break;
        case 'stripe':
            contenedor.innerHTML = camposStripe();
            btnPagar.textContent = '';
            btnPagar.innerHTML = "<i class='bx bx-credit-card'></i> Pagar con Tarjeta";
            btnPagar.onclick = null;
            btnPagar.type = 'submit';
            break;
    }
}

// ── Calcular devuelta (efectivo) ──

function formatearMonto(input) {
    let valor = input.value.replace(/\D/g, '');
    if (valor === '') {
        document.getElementById('monto-efectivo').value = '';
        input.value = '';
        return;
    }
    document.getElementById('monto-efectivo').value = valor;
    input.value = parseInt(valor).toLocaleString('es-CO');
}

function calcularDevuelta() {
    const input = document.getElementById('monto-efectivo');
    const info = document.getElementById('devuelta-info');
    const valorEl = document.getElementById('devuelta-valor');

    if (!input || !info || !valorEl) return;

    const monto = parseFloat(input.value) || 0;

    if (monto > totalPedido) {
        const devuelta = monto - totalPedido;
        valorEl.textContent = '$' + devuelta.toLocaleString('es-CO');
        info.style.display = 'flex';
        info.classList.remove('error');
    } else if (monto === totalPedido) {
        valorEl.textContent = 'Pago exacto, sin vueltas';
        info.style.display = 'flex';
        info.classList.remove('error');
    } else if (monto > 0) {
        valorEl.textContent = `El monto debe ser mínimo $${totalPedido.toLocaleString('es-CO')}`;
        info.style.display = 'flex';
        info.classList.add('error');
    } else {
        info.style.display = 'none';
    }
}

// ── Preview de comprobante subido ──

function mostrarPreview(inputFile, areaId) {
    const area = document.getElementById(areaId);
    if (!area || !inputFile.files.length) return;

    const file = inputFile.files[0];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (file.size > maxSize) {
        alert('El archivo es muy grande. Máximo 5 MB.');
        inputFile.value = '';
        return;
    }

    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function (e) {
            area.innerHTML = `
                <img src="${e.target.result}" alt="Comprobante" style="max-height:140px;border-radius:8px;">
                <span class="upload-nombre">${file.name}</span>
                <small style="color:var(--success);">✓ Comprobante cargado</small>
            `;
        };
        reader.readAsDataURL(file);
    } else {
        area.innerHTML = `
            <i class='bx bx-file' style="font-size:2.5rem;color:var(--primario);"></i>
            <span class="upload-nombre">${file.name}</span>
            <small style="color:var(--success);">✓ Archivo cargado</small>
        `;
    }
}

// ── Validación antes de enviar ──

document.getElementById('formPago')?.addEventListener('submit', function (e) {
    const metodoEl = document.querySelector('input[name="id_met_pago_fk"]:checked');
    if (!metodoEl) {
        e.preventDefault();
        if (typeof Swal !== 'undefined') {
            Swal.fire({ icon: 'warning', title: 'Método de pago', text: 'Selecciona un método de pago.' });
        } else {
            alert('Selecciona un método de pago.');
        }
        return;
    }

    const metodo = metodoEl.value;

    // Efectivo: validar monto
    if (metodo === 'efectivo') {
        const monto = parseFloat(document.getElementById('monto-efectivo')?.value || 0);
        if (monto < totalPedido) {
            e.preventDefault();
            if (typeof Swal !== 'undefined') {
                Swal.fire({ icon: 'error', title: 'Monto insuficiente', text: `El monto mínimo es $${totalPedido.toLocaleString('es-CO')}.` });
            }
            return;
        }
    }

    // Nequi: validar celular y comprobante
    if (metodo === 'nequi') {
        const cel = document.getElementById('celular-nequi')?.value.trim();
        const ref = document.getElementById('ref-nequi')?.value.trim();
        const comp = document.getElementById('comprobante-nequi');
        if (!cel || cel.length !== 10 || !cel.startsWith('3')) {
            e.preventDefault();
            if (typeof Swal !== 'undefined') {
                Swal.fire({ icon: 'error', title: 'Celular inválido', text: 'El número de Nequi debe tener exactamente 10 dígitos y empezar por 3.' });
            }
            return;
        }
        if (!ref || ref.length < 6 || !/^\d+$/.test(ref)) {
            e.preventDefault();
            if (typeof Swal !== 'undefined') {
                Swal.fire({ icon: 'error', title: 'Referencia inválida', text: 'La referencia debe tener al menos 6 números.' });
            }
            return;
        }
        if (!comp || !comp.files.length) {
            e.preventDefault();
            if (typeof Swal !== 'undefined') {
                Swal.fire({ icon: 'error', title: 'Comprobante requerido', text: 'Sube el pantallazo de tu transferencia Nequi.' });
            }
            return;
        }
    }

    // Bancolombia: validar titular, referencia y comprobante
    if (metodo === 'bancolombia') {
        const titular = document.getElementById('titular-banco')?.value.trim();
        const ref = document.getElementById('ref-banco')?.value.trim();
        const comp = document.getElementById('comprobante-banco');
        if (!titular || titular.length < 5 || !/^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$/.test(titular)) {
            e.preventDefault();
            if (typeof Swal !== 'undefined') {
                Swal.fire({ icon: 'error', title: 'Titular inválido', text: 'El nombre debe tener mínimo 5 caracteres y solo contener letras.' });
            }
            return;
        }
        if (!ref || ref.length !== 9 || !/^\d{9}$/.test(ref)) {
            e.preventDefault();
            if (typeof Swal !== 'undefined') {
                Swal.fire({ icon: 'error', title: 'Referencia inválida', text: 'El número de comprobante Bancolombia debe tener exactamente 9 dígitos.' });
            }
            return;
        }
        if (!comp || !comp.files.length) {
            e.preventDefault();
            if (typeof Swal !== 'undefined') {
                Swal.fire({ icon: 'error', title: 'Comprobante requerido', text: 'Sube la imagen de tu comprobante de transferencia.' });
            }
            return;
        }
    }

    // If it has already been confirmed, allow submit
    if (this.dataset.confirmado === 'true') {
        return;
    }

    e.preventDefault();

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: '¿Confirmar Pago?',
            text: '¿Estás seguro de registrar tu pago con este método y de que todos los datos ingresados son correctos?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#d98829',
            cancelButtonColor: '#7A5C52',
            confirmButtonText: 'Sí, confirmar pago',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                this.dataset.confirmado = 'true';
                this.submit();
            }
        });
    } else {
        if (confirm('¿Estás seguro de registrar tu pago con este método y de que todos los datos ingresados son correctos?')) {
            this.dataset.confirmado = 'true';
            this.submit();
        }
    }
});

// ── Dropdown usuario ──

function toggleUserMenu() {
    document.getElementById('userDropdown')?.classList.toggle('show');
}

window.onclick = function (e) {
    if (!e.target.closest('.sidebar-footer')) {
        document.getElementById('userDropdown')?.classList.remove('show');
    }
};
