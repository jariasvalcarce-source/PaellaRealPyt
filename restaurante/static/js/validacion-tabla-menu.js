window.abrirModalMenu = function(id, nom, precio, des, tipoId, disponible) {
    document.getElementById('modal-menu-nom').value    = nom;
    document.getElementById('modal-menu-precio').value = precio;
    document.getElementById('modal-menu-des').value    = des;
    document.getElementById('modal-menu-disponible').checked = disponible === '1';

    setSelectValue('modal-menu-tipo', tipoId);

    document.getElementById('form-editar-menu').action =
        `/admin-panel/inventario/menu/${id}/editar/`;

    document.getElementById('modal-overlay-menu').classList.add('activo');
    document.body.style.overflow = 'hidden';
};

function setSelectValue(selectId, value) {
    const select = document.getElementById(selectId);
    if (!select) return;
    for (let option of select.options) {
        option.selected = (option.value == value);
    }
}

window.cerrarModalMenu = function() {
    document.getElementById('modal-overlay-menu').classList.remove('activo');
    document.body.style.overflow = '';
};

window.cerrarModalMenuOverlay = function(e) {
    if (e.target === document.getElementById('modal-overlay-menu')) {
        window.cerrarModalMenu();
    }
};

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.cerrarModalMenu();
});

// Delegación: abrir modal desde data-* attributes
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn-abrir-modal-menu');
    if (!btn) return;
    window.abrirModalMenu(
        btn.dataset.id,
        btn.dataset.nom,
        btn.dataset.precio,
        btn.dataset.des,
        btn.dataset.tipo,
        btn.dataset.disponible
    );
});

// ══════════════════════════════════════════
// FILTROS Y BÚSQUEDA
// ══════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

    window.filtrar = (estado, btnClicado) => {
        document.querySelectorAll('.btn-filtro').forEach(b => b.classList.remove('active'));
        if (btnClicado) btnClicado.classList.add('active');

        document.querySelectorAll('#lista-menus .card').forEach(card => {
            card.style.display =
                (estado === 'todos' || card.dataset.estado === estado) ? '' : 'none';
        });
        actualizarContador();
    };

    const inputBuscar = document.getElementById('buscar-menu');
    if (inputBuscar) {
        inputBuscar.addEventListener('input', function () {
            const texto = this.value.toLowerCase();
            document.querySelectorAll('#lista-menus .card').forEach(card => {
                card.style.display =
                    card.innerText.toLowerCase().includes(texto) ? '' : 'none';
            });
            actualizarContador();
        });
    }

    function actualizarContador() {
        const contador = document.getElementById('contador');
        if (!contador) return;
        const visibles = document.querySelectorAll('#lista-menus .card:not([style*="display: none"])').length;
        contador.textContent = `${visibles} menú(s) encontrado(s)`;
    }

    actualizarContador();
});