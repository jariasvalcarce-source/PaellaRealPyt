document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('formMovimiento');
    const tipoInputs = document.querySelectorAll('input[name="tipo_movi"]');
    const motivoSelect = document.getElementById('motivo_movi');
    const fechaMovi = document.getElementById('fecha_movi');
    const productoSelect = document.getElementById('id_produ_movi_fk');
    const unidadSelect = document.getElementById('unidad_movi');
    const cantidadInput = document.getElementById('cant_movi');
    const notaInput = document.getElementById('nota_movi');
    
    const stockAnterior = document.getElementById('stock_anterior');
    const stockPosterior = document.getElementById('stock_posterior');
    
    const resTipo = document.getElementById('res-tipo');
    const resProducto = document.getElementById('res-producto');
    const resCant = document.getElementById('res-cant');
    const resStockAnterior = document.getElementById('res-stock-anterior');
    const resStockPosterior = document.getElementById('res-stock-posterior');
    const resEmple = document.getElementById('res-emple');

    // Inicializar Fechas
    function initFechas() {
        if (!fechaMovi) return;
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        const nowStr = now.toISOString().slice(0, 16);
        
        const past = new Date();
        past.setDate(past.getDate() - 30);
        past.setMinutes(past.getMinutes() - past.getTimezoneOffset());
        const pastStr = past.toISOString().slice(0, 16);

        fechaMovi.max = nowStr;
        fechaMovi.min = pastStr;
        fechaMovi.value = nowStr;
    }
    initFechas();

    // ── Motivos según tipo de movimiento ──
    const MOTIVOS_ENTRADA = [
        { value: 'compra',           text: 'Compra a proveedor' },
        { value: 'ajuste_entrada',   text: 'Ajuste por conteo físico' },
        { value: 'devolucion_cocina', text: 'Devolución de cocina' },
        { value: 'stock_inicial',    text: 'Stock inicial' },
    ];
    const MOTIVOS_SALIDA = [
        { value: 'merma',           text: 'Merma o desperdicio' },
        { value: 'vencimiento',     text: 'Producto vencido' },
        { value: 'ajuste_salida',   text: 'Ajuste por conteo físico' },
        { value: 'consumo_interno', text: 'Consumo interno' },
    ];

    function updateMotivos() {
        const tipo = document.querySelector('input[name="tipo_movi"]:checked')?.value;
        if (!motivoSelect || !tipo) return;

        // Guardar selección actual
        const currentVal = motivoSelect.value;

        // Limpiar y reconstruir opciones
        motivoSelect.innerHTML = '<option value="">Seleccionar motivo…</option>';

        const motivos = tipo === 'entrada' ? MOTIVOS_ENTRADA : MOTIVOS_SALIDA;
        motivos.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.value;
            opt.textContent = m.text;
            motivoSelect.appendChild(opt);
        });

        // Restaurar selección si sigue siendo válida
        const stillValid = motivos.some(m => m.value === currentVal);
        motivoSelect.value = stillValid ? currentVal : '';
    }

    // Funciones de utilidad y conversión
    function getConversion(fromUnit, toUnit) {
        fromUnit = (fromUnit || '').toLowerCase();
        toUnit = (toUnit || '').toLowerCase();
        if (fromUnit === toUnit) return 1;
        if (fromUnit === 'kg' && toUnit === 'g') return 1000;
        if (fromUnit === 'g' && toUnit === 'kg') return 0.001;
        if (fromUnit === 'l' && toUnit === 'ml') return 1000;
        if (fromUnit === 'ml' && toUnit === 'l') return 0.001;
        return null; // Incompatible
    }

    function formatNum(val) {
        return Number(val).toLocaleString('es-CO', { minimumFractionDigits: 0, maximumFractionDigits: 3 });
    }

    // Actualizar vista previa y cálculos en tiempo real
    function updatePreview() {
        const tipo = document.querySelector('input[name="tipo_movi"]:checked')?.value || '—';
        const prodOption = productoSelect?.selectedOptions[0];
        const prodName = prodOption && prodOption.value ? prodOption.text.split('—')[0].trim() : '—';
        
        const baseUnit = prodOption?.dataset.unidad?.toLowerCase() || '';
        
        // Bloquear y autoseleccionar la unidad base
        if (prodOption && prodOption.value && unidadSelect) {
            unidadSelect.value = baseUnit;
            unidadSelect.style.pointerEvents = 'none';
            unidadSelect.style.background = '#f3f4f6';
            unidadSelect.style.opacity = '0.8';
        } else if (unidadSelect) {
            unidadSelect.value = '';
            unidadSelect.style.pointerEvents = 'auto';
            unidadSelect.style.background = '#f8f9fb';
            unidadSelect.style.opacity = '1';
        }
        
        // Actualizar etiqueta de cantidad
        const labelUnidad = document.getElementById('cantidad-unidad-text');
        if (labelUnidad) {
            labelUnidad.textContent = baseUnit ? '(en ' + baseUnit + ')' : '';
        }
        if (cantidadInput) {
            cantidadInput.placeholder = baseUnit ? 'Ej: 5 (' + baseUnit + ')' : 'Ej: 5.000';
        }
        
        const selectedUnit = unidadSelect?.value?.toLowerCase() || '';
        
        const rawStock = parseFloat(prodOption?.dataset.stock?.replace(',', '.') || 0);
        const rawMin = parseFloat(prodOption?.dataset.min?.replace(',', '.') || 0);
        const rawCant = parseFloat(cantidadInput?.value?.replace(',', '.') || 0);

        // Conversión a unidad base para los cálculos de stock posterior
        const conversion = getConversion(selectedUnit, baseUnit);
        const cantInBaseUnit = conversion !== null ? rawCant * conversion : 0;
        
        const delta = tipo === 'salida' ? -cantInBaseUnit : cantInBaseUnit;
        const posterior = rawStock + delta;

        // Actualizar UI de solo lectura
        if (stockAnterior) stockAnterior.value = formatNum(rawStock) + ' ' + (baseUnit.toUpperCase());
        if (stockPosterior) stockPosterior.value = formatNum(posterior) + ' ' + (baseUnit.toUpperCase());

        // Colores semáforo para stock posterior
        if (stockPosterior && prodOption && prodOption.value) {
            stockPosterior.style.fontWeight = 'bold';
            if (posterior < 0) {
                stockPosterior.style.color = '#dc2626'; // Rojo
                stockPosterior.style.backgroundColor = '#fef2f2';
            } else if (posterior === 0) {
                stockPosterior.style.color = '#b91c1c'; // Rojo suave
                stockPosterior.style.backgroundColor = '#fef2f2';
            } else if (posterior <= rawMin * 0.5) {
                stockPosterior.style.color = '#ea580c'; // Naranja
                stockPosterior.style.backgroundColor = '#fff7ed';
            } else if (posterior <= rawMin) {
                stockPosterior.style.color = '#ca8a04'; // Amarillo
                stockPosterior.style.backgroundColor = '#fefce8';
            } else {
                stockPosterior.style.color = '#16a34a'; // Verde
                stockPosterior.style.backgroundColor = '#f0fdf4';
            }
        } else if (stockPosterior) {
            stockPosterior.style.color = 'inherit';
            stockPosterior.style.backgroundColor = '#f3f4f6';
        }

        // Resumen
        if (resTipo) resTipo.textContent = tipo === 'entrada' ? 'Entrada' : tipo === 'salida' ? 'Salida' : '—';
        if (resProducto) resProducto.textContent = prodName;
        if (resCant) resCant.textContent = rawCant > 0 ? `${formatNum(rawCant)} ${selectedUnit.toUpperCase()}` : '—';
        if (resStockAnterior) resStockAnterior.textContent = prodOption && prodOption.value ? `${formatNum(rawStock)} ${baseUnit.toUpperCase()}` : '—';
        if (resStockPosterior) resStockPosterior.textContent = prodOption && prodOption.value ? `${formatNum(posterior)} ${baseUnit.toUpperCase()}` : '—';
        
        const empOpt = document.getElementById('id_emple_movi_fk')?.selectedOptions[0];
        if (resEmple) resEmple.textContent = empOpt && empOpt.value ? empOpt.text.split('—')[0].trim() : '—';
        
        // Validación visual en el campo de unidad si es incompatible
        if (selectedUnit && baseUnit && conversion === null) {
            unidadSelect.setCustomValidity('Unidad incompatible con el producto');
            if (resStockPosterior) resStockPosterior.textContent = 'Error: Unidad Incompatible';
            if (stockPosterior) stockPosterior.value = 'Incompatible';
        } else if (unidadSelect) {
            unidadSelect.setCustomValidity('');
        }
    }

    // Event Listeners
    tipoInputs.forEach(i => i.addEventListener('change', () => {
        updateMotivos();
        updatePreview();
    }));
    
    productoSelect?.addEventListener('change', () => {
        const prodOption = productoSelect.selectedOptions[0];
        const baseUnit = prodOption?.dataset.unidad?.toLowerCase() || '';
        // Pre-seleccionar la unidad base si está disponible
        if (baseUnit && unidadSelect) {
            const matchOpt = Array.from(unidadSelect.options).find(o => o.value.toLowerCase() === baseUnit);
            if (matchOpt) {
                unidadSelect.value = matchOpt.value;
                // Bloquear para evitar que el usuario la cambie y cometa errores
                unidadSelect.style.pointerEvents = 'none';
                unidadSelect.style.backgroundColor = '#f3f4f6';
                unidadSelect.style.color = '#6b7280';
            }
        } else if (unidadSelect) {
            // Desbloquear si no hay producto seleccionado
            unidadSelect.style.pointerEvents = 'auto';
            unidadSelect.style.backgroundColor = '';
            unidadSelect.style.color = '';
        }
        updatePreview();
    });
    
    unidadSelect?.addEventListener('change', updatePreview);
    cantidadInput?.addEventListener('input', updatePreview);
    document.getElementById('id_emple_movi_fk')?.addEventListener('change', updatePreview);

    // Initial setup
    updateMotivos();
    updatePreview();
    if (productoSelect && productoSelect.value) {
        productoSelect.dispatchEvent(new Event('change'));
    }

    // Validaciones al Enviar (Submit)
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // Native form validity
            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            const tipo = document.querySelector('input[name="tipo_movi"]:checked').value;
            const motivo = motivoSelect.value;
            const prodOption = productoSelect.selectedOptions[0];
            const baseUnit = prodOption.dataset.unidad.toLowerCase();
            const selectedUnit = unidadSelect.value.toLowerCase();
            const rawStock = parseFloat(prodOption.dataset.stock.replace(',', '.'));
            const rawMin = parseFloat(prodOption.dataset.min.replace(',', '.'));
            const rawCant = parseFloat(cantidadInput.value.replace(',', '.'));
            const nota = notaInput.value.trim();

            const conversion = getConversion(selectedUnit, baseUnit);
            if (conversion === null) {
                Swal.fire('Error', `No puedes usar ${selectedUnit.toUpperCase()} para un producto medido en ${baseUnit.toUpperCase()}.`, 'error');
                return;
            }

            const cantInBaseUnit = rawCant * conversion;
            const posterior = tipo === 'salida' ? rawStock - cantInBaseUnit : rawStock + cantInBaseUnit;

            // Validaciones Estrictas
            if (tipo === 'salida' && posterior < 0) {
                Swal.fire({
                    icon: 'error',
                    title: 'Stock insuficiente',
                    text: `No hay suficiente stock. Disponible: ${formatNum(rawStock)} ${baseUnit.toUpperCase()}`
                });
                return;
            }

            if (tipo === 'salida' && (motivo === 'merma' || motivo === 'ajuste_salida') && nota.length < 10) {
                Swal.fire('Nota requerida', 'Debes ingresar una observación de al menos 10 caracteres para mermas o ajustes.', 'warning');
                return;
            }

            // Warnings antes de confirmar
            let warningText = `Se registrará una ${tipo} de ${formatNum(rawCant)} ${selectedUnit.toUpperCase()}.`;
            let iconType = 'question';

            if (tipo === 'salida') {
                if (posterior === 0) {
                    warningText += '<br><br><b>⚠️ El producto quedará agotado (Stock 0).</b>';
                    iconType = 'warning';
                } else if (posterior <= rawMin) {
                    warningText += '<br><br><b>⚠️ Este movimiento dejará el stock en nivel mínimo o crítico.</b>';
                    iconType = 'warning';
                }
            }

            Swal.fire({
                title: '¿Confirmar Movimiento?',
                html: warningText,
                icon: iconType,
                showCancelButton: true,
                confirmButtonText: 'Sí, registrar',
                cancelButtonText: 'Cancelar',
                reverseButtons: true
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();
                }
            });
        });
    }
});
