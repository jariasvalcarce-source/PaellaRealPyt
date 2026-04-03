window.abrirModalCorrectivo = function(datos) {
    const tipoInvertido = datos.tipo === 'entrada' ? 'salida' : 'entrada';
    const iconTipo      = tipoInvertido === 'entrada' ? '📥' : '📤';
    const labelTipo     = tipoInvertido === 'entrada' ? 'Entrada' : 'Salida';

    document.getElementById('modal-correc-titulo').textContent =
        `Correctivo del Movimiento #${datos.id}`;

    document.getElementById('modal-correc-info').innerHTML = `
        <div style="background:rgba(253,126,20,0.08);border:2px solid rgba(253,126,20,0.3);
                    border-radius:8px;padding:12px 16px;font-size:13px;margin-bottom:16px;line-height:1.6;">
            <strong>⚠️ Movimiento original:</strong><br>
            ${datos.tipo === 'entrada' ? '📥 Entrada' : '📤 Salida'} de
            <strong>${datos.cantidad} ${datos.unidad}</strong> —
            <strong>${datos.producto}</strong>
            &nbsp;·&nbsp; ${datos.fecha}
        </div>
    `;

    document.getElementById('correc-producto-nombre').value = datos.producto;
    document.getElementById('correc-tipo-label').value      = `${iconTipo} ${labelTipo} (correctivo)`;
    document.getElementById('correc-tipo').value            = tipoInvertido;
    document.getElementById('correc-producto').value        = datos.productoId;
    document.getElementById('correc-cantidad').value        = '';
    document.getElementById('correc-empleado').value        = '';
    document.getElementById('correc-motivo').value          = `Corrección de movimiento #${datos.id}`;
    document.getElementById('correc-stock-actual').textContent =
        `Stock actual del producto: ${datos.stockActual} ${datos.unidad}`;

    document.getElementById('modal-overlay-correctivo').classList.add('activo');
    document.body.style.overflow = 'hidden';
};

window.cerrarModalCorrectivo = function() {
    document.getElementById('modal-overlay-correctivo').classList.remove('activo');
    document.body.style.overflow = '';
};

window.cerrarModalCorrectivoOverlay = function(e) {
    if (e.target === document.getElementById('modal-overlay-correctivo')) {
        window.cerrarModalCorrectivo();
    }
};

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.cerrarModalCorrectivo();
});

// Delegación: abrir modal correctivo desde data-* attributes
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn-abrir-correctivo');
    if (!btn) return;
    window.abrirModalCorrectivo({
        id:          btn.dataset.id,
        producto:    btn.dataset.producto,
        productoId:  btn.dataset.productoId,
        tipo:        btn.dataset.tipo,
        cantidad:    btn.dataset.cantidad,
        unidad:      btn.dataset.unidad,
        stockActual: btn.dataset.stockActual,
        fecha:       btn.dataset.fecha,
    });
});


document.addEventListener('DOMContentLoaded', () => {

    // ══════════════════════════════════════════
    // CONFIRMACIÓN SWEETALERT AL REGISTRAR MOVIMIENTO
    // ══════════════════════════════════════════
    const btnConfirmar   = document.getElementById('btn-confirmar');
    const formMovimiento = document.getElementById('form-movimiento');

    if (btnConfirmar && formMovimiento) {
        btnConfirmar.addEventListener('click', () => {
            const tipo      = document.getElementById('tipo_movi').value;
            const motivo    = document.getElementById('motivo_movi').value.trim();
            const cantidad  = parseFloat(document.getElementById('cant_movi').value);
            const selectProd = document.getElementById('id_produ_movi_fk');
            const opcion    = selectProd.options[selectProd.selectedIndex];
            const nombre    = opcion?.dataset?.nombre || '';
            const unidad    = opcion?.dataset?.unidad || '';
            const stock     = parseFloat(opcion?.dataset?.stock);
            const empleadoSel = document.getElementById('id_emple_movi_fk');
            const empleado  = empleadoSel.options[empleadoSel.selectedIndex]?.text || '';

            // ── Validaciones previas ──
            const errores = [];
            if (!tipo)              errores.push('Selecciona el tipo de movimiento.');
            if (!motivo)            errores.push('El motivo es obligatorio.');
            if (!nombre)            errores.push('Selecciona un producto.');
            if (isNaN(cantidad) || cantidad <= 0) errores.push('La cantidad debe ser mayor a 0.');
            if (!empleadoSel.value) errores.push('Selecciona un empleado responsable.');

            if (tipo === 'salida' && !isNaN(stock) && cantidad > stock) {
                errores.push(`Stock insuficiente. Stock actual de ${nombre}: ${stock} ${unidad}`);
            }

            if (errores.length > 0) {
                Swal.fire({
                    icon:              'error',
                    title:             'Datos incompletos',
                    html:              errores.map(e => `• ${e}`).join('<br>'),
                    confirmButtonText: 'Entendido',
                    confirmButtonColor: '#dc3545',
                });
                return;
            }

            // ── Calcular stock resultante ──
            const stockResultante = tipo === 'entrada'
                ? stock + cantidad
                : stock - cantidad;

            const colorStock = stockResultante <= 0
                ? '#dc3545'
                : stockResultante < 2
                    ? '#fd7e14'
                    : '#28a745';

            const iconTipo = tipo === 'entrada' ? '📥' : '📤';

            // ── SweetAlert de confirmación ──
            Swal.fire({
                title:             `¿Confirmar ${tipo}?`,
                icon:              'question',
                html: `
                    <div style="text-align:left;font-size:14px;line-height:2;">
                        <b>${iconTipo} Tipo:</b> ${tipo.charAt(0).toUpperCase() + tipo.slice(1)}<br>
                        <b>🧹 Producto:</b> ${nombre}<br>
                        <b>📦 Cantidad:</b> ${cantidad} kg<br>
                        <b>📝 Motivo:</b> ${motivo}<br>
                        <b>👤 Empleado:</b> ${empleado}<br>
                        <hr style="margin:8px 0;">
                        <b>Stock actual:</b> ${stock} kg<br>
                        <b>Stock después:</b>
                        <span style="color:${colorStock};font-weight:700;">
                            ${stockResultante.toFixed(3)} kg
                            ${stockResultante <= 0 ? ' ⚠️ Quedará en cero' : ''}
                        </span>
                    </div>
                `,
                showCancelButton:   true,
                confirmButtonText:  `Sí, registrar`,
                cancelButtonText:   'Cancelar',
                confirmButtonColor: tipo === 'entrada' ? '#28a745' : '#dc3545',
                cancelButtonColor:  '#6c757d',
                reverseButtons:     true,
            }).then((result) => {
                if (result.isConfirmed) {
                    formMovimiento.submit();
                }
            });
        });
    }


    // ══════════════════════════════════════════
    // CONFIRMACIÓN SWEETALERT PARA CORRECTIVO
    // ══════════════════════════════════════════
    const btnCorrectivo = document.getElementById('btn-confirmar-correctivo');
    const formCorrectivo = document.getElementById('form-correctivo');

    if (btnCorrectivo && formCorrectivo) {
        btnCorrectivo.addEventListener('click', () => {
            const tipoLabel  = document.getElementById('correc-tipo-label').value;
            const producto   = document.getElementById('correc-producto-nombre').value;
            const cantidad   = parseFloat(document.getElementById('correc-cantidad').value);
            const motivo     = document.getElementById('correc-motivo').value.trim();
            const empleadoSel = document.getElementById('correc-empleado');
            const empleado   = empleadoSel.options[empleadoSel.selectedIndex]?.text || '';
            const tipo       = document.getElementById('correc-tipo').value;

            // Extraer stock actual del texto informativo
            const stockTexto = document.getElementById('correc-stock-actual').textContent;
            const stockMatch = stockTexto.match(/[\d.]+/);
            const stock      = stockMatch ? parseFloat(stockMatch[0]) : NaN;
            const unidadMatch = stockTexto.match(/[\d.]+ ([^\s]+)/);
            const unidad     = unidadMatch ? unidadMatch[1] : '';

            const errores = [];
            if (isNaN(cantidad) || cantidad <= 0) errores.push('La cantidad debe ser mayor a 0.');
            if (!empleadoSel.value)               errores.push('Selecciona un empleado responsable.');
            if (!motivo)                          errores.push('El motivo es obligatorio.');

            if (tipo === 'salida' && !isNaN(stock) && cantidad > stock) {
                errores.push(`Stock insuficiente para aplicar este correctivo. Stock actual: ${stock} ${unidad}`);
            }

            if (errores.length > 0) {
                Swal.fire({
                    icon:              'error',
                    title:             'Datos incompletos',
                    html:              errores.map(e => `• ${e}`).join('<br>'),
                    confirmButtonText: 'Entendido',
                    confirmButtonColor: '#dc3545',
                });
                return;
            }

            Swal.fire({
                title:            '¿Aplicar correctivo?',
                icon:             'warning',
                html: `
                    <div style="text-align:left;font-size:14px;line-height:2;">
                        <b>🔧 Tipo:</b> ${tipoLabel}<br>
                        <b>🧺 Producto:</b> ${producto}<br>
                        <b>📦 Cantidad:</b> ${cantidad}<br>
                        <b>📝 Motivo:</b> ${motivo}<br>
                        <b>👤 Empleado:</b> ${empleado}
                    </div>
                `,
                showCancelButton:   true,
                confirmButtonText:  'Sí, aplicar correctivo',
                cancelButtonText:   'Cancelar',
                confirmButtonColor: '#fd7e14',
                cancelButtonColor:  '#6c757d',
                reverseButtons:     true,
            }).then((result) => {
                if (result.isConfirmed) {
                    formCorrectivo.submit();
                }
            });
        });
    }


    // ══════════════════════════════════════════
    // INFO DINÁMICA DEL STOCK EN EL FORMULARIO
    // ══════════════════════════════════════════
    const selectProducto = document.getElementById('id_produ_movi_fk');
    const selectTipo     = document.getElementById('tipo_movi');
    const inputCantidad  = document.getElementById('cant_movi');
    const infoStock      = document.getElementById('info-stock');

    function actualizarInfoStock() {
        if (!selectProducto || !infoStock) return;

        const opcion = selectProducto.options[selectProducto.selectedIndex];
        const stock  = parseFloat(opcion?.dataset?.stock);
        const unidad = opcion?.dataset?.unidad || '';
        const nombre = opcion?.dataset?.nombre || '';
        const tipo   = selectTipo?.value;

        if (!nombre || isNaN(stock) || !tipo) {
            infoStock.style.display = 'none';
            return;
        }

        const cantidad    = parseFloat(inputCantidad?.value) || 0;
        const resultante  = tipo === 'entrada' ? stock + cantidad : stock - cantidad;
        const colorResult = resultante < 0
            ? '#dc3545'
            : resultante === 0
                ? '#fd7e14'
                : '#28a745';

        const iconTipo = tipo === 'entrada' ? '📥' : '📤';

        infoStock.innerHTML = `
            ${iconTipo} Stock actual de <strong>${nombre}</strong>:
            <strong style="margin:0 6px;">${stock} kg</strong>
            ${cantidad > 0
                ? `→ Quedaría: <strong style="color:${colorResult};">${resultante.toFixed(3)} kg</strong>
                   ${resultante < 0 ? ' <span style="color:#dc3545;">⚠️ Stock insuficiente</span>' : ''}`
                : ''}
        `;
        infoStock.style.display    = 'block';
        infoStock.style.background = resultante < 0
            ? 'rgba(220,53,69,0.08)'
            : 'rgba(40,167,69,0.08)';
        infoStock.style.border = `2px solid ${resultante < 0
            ? 'rgba(220,53,69,0.3)'
            : 'rgba(40,167,69,0.3)'}`;
    }

    if (selectProducto) selectProducto.addEventListener('change', actualizarInfoStock);
    if (selectTipo)     selectTipo.addEventListener('change', actualizarInfoStock);
    if (inputCantidad)  inputCantidad.addEventListener('input', actualizarInfoStock);


    // ══════════════════════════════════════════
    // FILTROS Y BÚSQUEDA EN LA TABLA
    // ══════════════════════════════════════════
    const listaMovimientos = document.getElementById('lista-movimientos');

    if (listaMovimientos) {

        window.filtrar = (tipo, btnClicado) => {
            document.querySelectorAll('.btn-filtro').forEach(btn => btn.classList.remove('active'));
            if (btnClicado) btnClicado.classList.add('active');

            document.querySelectorAll('.card').forEach(card => {
                card.style.display =
                    (tipo === 'todos' || card.dataset.tipo === tipo) ? 'block' : 'none';
            });
            actualizarContador();
        };

        const inputBuscar = document.getElementById('buscar-movimiento');
        if (inputBuscar) {
            inputBuscar.addEventListener('input', function() {
                const texto = this.value.toLowerCase();
                document.querySelectorAll('.card').forEach(card => {
                    card.style.display =
                        card.innerText.toLowerCase().includes(texto) ? 'block' : 'none';
                });
                actualizarContador();
            });
        }

        function actualizarContador() {
            const contador = document.getElementById('contador');
            if (!contador) return;
            const visibles = document.querySelectorAll('#lista-movimientos .card:not([style*="display: none"])').length;
            contador.textContent = `${visibles} movimiento(s) encontrado(s)`;
        }

        actualizarContador();
    }

});