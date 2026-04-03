// =====================================================
// FORMULARIO CREAR RECETA — múltiples ingredientes
// =====================================================

const ingredientes = []; // lista en memoria

function agregarIngrediente() {
    const selProducto = document.getElementById('inp-producto');
    const inpCantidad = document.getElementById('inp-cantidad');
    const selUnidad   = document.getElementById('inp-unidad');
    const inpNotas    = document.getElementById('inp-notas');

    const idProducto  = selProducto.value;
    const nomProducto = selProducto.options[selProducto.selectedIndex]?.dataset.nom || '';
    const cantidad    = inpCantidad.value;
    const idUnidad    = selUnidad.value;
    const nomUnidad   = selUnidad.options[selUnidad.selectedIndex]?.dataset.nom || '';
    const abrUnidad   = selUnidad.options[selUnidad.selectedIndex]?.dataset.abr || '';
    const notas       = inpNotas.value.trim();

    // Validaciones
    if (!idProducto) { alert('Selecciona un ingrediente.'); return; }
    if (!cantidad || parseFloat(cantidad) <= 0) { alert('Ingresa una cantidad válida.'); return; }
    if (!idUnidad) { alert('Selecciona una unidad de medida.'); return; }

    // Verificar duplicado en la lista
    if (ingredientes.some(i => i.idProducto === idProducto)) {
        alert(`"${nomProducto}" ya está en la lista.`);
        return;
    }

    // Agregar a memoria
    ingredientes.push({ idProducto, nomProducto, cantidad, idUnidad, nomUnidad, abrUnidad, notas });

    renderTabla();
    renderCamposOcultos();

    // Limpiar inputs (menos el menú)
    selProducto.value = '';
    inpCantidad.value = '';
    selUnidad.value   = '';
    inpNotas.value    = '';
}

function quitarIngrediente(idProducto) {
    const idx = ingredientes.findIndex(i => i.idProducto === idProducto);
    if (idx !== -1) ingredientes.splice(idx, 1);
    renderTabla();
    renderCamposOcultos();
}

function renderTabla() {
    const tbody     = document.getElementById('tbody-ingredientes');
    const filaVacia = document.getElementById('fila-vacia');
    const badge     = document.getElementById('badge-count');
    const btnGuardar = document.getElementById('btn-guardar');

    tbody.innerHTML = '';
    badge.textContent = ingredientes.length;

    if (ingredientes.length === 0) {
        tbody.innerHTML = `<tr id="fila-vacia">
            <td colspan="5" class="sin-ingredientes">Aún no has agregado ingredientes</td>
        </tr>`;
        btnGuardar.disabled = true;
        btnGuardar.style.opacity = '0.5';
        btnGuardar.style.cursor  = 'not-allowed';
        return;
    }

    btnGuardar.disabled = false;
    btnGuardar.style.opacity = '1';
    btnGuardar.style.cursor  = 'pointer';

    ingredientes.forEach(ing => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${ing.nomProducto}</strong></td>
            <td>${ing.cantidad}</td>
            <td>${ing.nomUnidad} (${ing.abrUnidad})</td>
            <td>${ing.notas || '<span style="color:#aaa">—</span>'}</td>
            <td>
                <button type="button" class="btn-quitar"
                        onclick="quitarIngrediente('${ing.idProducto}')">
                    <i class='bx bx-trash'></i> Quitar
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderCamposOcultos() {
    const div = document.getElementById('campos-ocultos');
    div.innerHTML = '';
    ingredientes.forEach((ing, i) => {
        div.innerHTML += `
            <input type="hidden" name="id_produ_fk_${i}"    value="${ing.idProducto}">
            <input type="hidden" name="cantidad_reque_${i}" value="${ing.cantidad}">
            <input type="hidden" name="id_uni_medi_fk_${i}" value="${ing.idUnidad}">
            <input type="hidden" name="notas_${i}"          value="${ing.notas}">
            <input type="hidden" name="total_ingredientes"  value="${ingredientes.length}">
        `;
    });
}

// =====================================================
// TABLA RECETAS — modal editar + búsqueda
// =====================================================

document.addEventListener('DOMContentLoaded', () => {

    // ── Modal editar receta ──
    const overlayReceta = document.getElementById('modal-overlay-receta');

    if (overlayReceta) {
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('.btn-abrir-modal-receta');
            if (!btn) return;

            setSelect('modal-rec-menu',     btn.dataset.menu);
            setSelect('modal-rec-producto', btn.dataset.producto);
            document.getElementById('modal-rec-cantidad').value = btn.dataset.cantidad;
            setSelect('modal-rec-unidad', btn.dataset.unidad);
            document.getElementById('modal-rec-notas').value = btn.dataset.notas || '';

            document.getElementById('form-editar-receta').action =
                `/admin-panel/recetas/${btn.dataset.id}/editar/`;

            overlayReceta.classList.add('activo');
            document.body.style.overflow = 'hidden';
        });

        window.cerrarModalReceta = function() {
            overlayReceta.classList.remove('activo');
            document.body.style.overflow = '';
        };

        window.cerrarModalRecetaOverlay = function(e) {
            if (e.target === overlayReceta) cerrarModalReceta();
        };

        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') cerrarModalReceta();
        });
    }

    // ── Búsqueda tabla recetas ──
    const inputBuscar = document.getElementById('buscar-receta');
    if (inputBuscar) {
        const cards    = document.querySelectorAll('#lista-recetas .card');
        const contador = document.getElementById('contador-receta');

        function actualizarContador() {
            const v = [...cards].filter(c => c.style.display !== 'none').length;
            contador.textContent = `Mostrando ${v} de ${cards.length} receta(s)`;
        }

        inputBuscar.addEventListener('input', function() {
            const q = this.value.toLowerCase().trim();
            cards.forEach(card => {
                const txt = (card.dataset.menu + ' ' + card.dataset.producto + ' ' + card.dataset.unidad);
                card.style.display = txt.includes(q) ? '' : 'none';
            });
            actualizarContador();
        });

        window.filtrarReceta = (tipo, btn) => {
            document.querySelectorAll('.btn-filtro').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            cards.forEach(c => c.style.display = '');
            actualizarContador();
        };

        actualizarContador();
    }
});

function setSelect(id, value) {
    const sel = document.getElementById(id);
    if (!sel) return;
    [...sel.options].forEach(opt => opt.selected = (opt.value == value));
}