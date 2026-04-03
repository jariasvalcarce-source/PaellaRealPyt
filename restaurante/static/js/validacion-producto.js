window.abrirModalProducto = function(id, nom, des, stockActual, stockMinimo, precio, fecha, proveedorId, unidadId, categoriaId) {
    document.getElementById('modal-prod-nom').value = nom;
    document.getElementById('modal-prod-des').value = des;
    document.getElementById('modal-prod-stock-actual').value = stockActual;
    document.getElementById('modal-prod-stock-minimo').value = stockMinimo;
    document.getElementById('modal-prod-precio').value = precio;
    document.getElementById('modal-prod-fecha').value = fecha;

    // Seleccionar la opción correcta en cada select
    setSelectValue('modal-prod-proveedor', proveedorId);
    setSelectValue('modal-prod-unidad', unidadId);
    setSelectValue('modal-prod-categoria', categoriaId);

    document.getElementById('form-editar-producto').action =
        `/admin-panel/productos/${id}/editar/`;

    document.getElementById('modal-overlay-producto').classList.add('activo');
    document.body.style.overflow = 'hidden';
};

function setSelectValue(selectId, value) {
    const select = document.getElementById(selectId);
    if (!select) return;
    for (let option of select.options) {
        option.selected = (option.value == value);
    }
}

window.cerrarModalProducto = function() {
    document.getElementById('modal-overlay-producto').classList.remove('activo');
    document.body.style.overflow = '';
};

window.cerrarModalProductoOverlay = function(e) {
    if (e.target === document.getElementById('modal-overlay-producto')) {
        window.cerrarModalProducto();
    }
};

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.cerrarModalProducto();
});

// Delegación: abrir modal desde data-* attributes
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn-abrir-modal-producto');
    if (!btn) return;
    window.abrirModalProducto(
        btn.dataset.id,
        btn.dataset.nom,
        btn.dataset.des,
        btn.dataset.stockActual,
        btn.dataset.stockMinimo,
        btn.dataset.precio,
        btn.dataset.fecha,
        btn.dataset.proveedor,
        btn.dataset.unidad,
        btn.dataset.categoria
    );
});


document.addEventListener('DOMContentLoaded', () => {

    // ══════════════════════════════════════════
    // FILTROS Y BÚSQUEDA EN LA TABLA
    // ══════════════════════════════════════════
    const listaProductos = document.getElementById('lista-productos');

    if (listaProductos) {

        window.filtrar = (estado, btnClicado) => {
            document.querySelectorAll('.btn-filtro').forEach(btn => btn.classList.remove('active'));
            if (btnClicado) btnClicado.classList.add('active');

            document.querySelectorAll('.card').forEach(card => {
                card.style.display =
                    (estado === 'todos' || card.dataset.estado === estado) ? 'block' : 'none';
            });

            actualizarContador();
        };

        const inputBuscar = document.getElementById('buscar-producto');
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
            const visibles = document.querySelectorAll('.card:not([style*="display: none"])').length;
            contador.textContent = `${visibles} producto(s) encontrado(s)`;
        }

        actualizarContador();
    }

    // ══════════════════════════════════════════
    // VALIDACIÓN MODAL AL GUARDAR
    // ══════════════════════════════════════════
    const formModal = document.getElementById('form-editar-producto');
    if (formModal) {
        formModal.addEventListener('submit', (e) => {
            const stockActual = parseFloat(document.getElementById('modal-prod-stock-actual').value);
            const stockMinimo = parseFloat(document.getElementById('modal-prod-stock-minimo').value);
            const precio = parseFloat(document.getElementById('modal-prod-precio').value);
            const fecha = document.getElementById('modal-prod-fecha').value;
            const hoy = new Date().toISOString().split('T')[0];
            const errores = [];

            if (isNaN(stockActual) || stockActual < 0) {
                errores.push('El stock actual debe ser un número mayor o igual a 0.');
            }
            if (isNaN(stockMinimo) || stockMinimo < 0) {
                errores.push('El stock mínimo debe ser un número mayor o igual a 0.');
            }
            if (isNaN(precio) || precio <= 0) {
                errores.push('El precio debe ser mayor a 0.');
            }
            if (!fecha) {
                errores.push('La fecha de vencimiento es obligatoria.');
            } else if (fecha < hoy) {
                errores.push('La fecha de vencimiento no puede ser pasada.');
            }

            if (errores.length > 0) {
                e.preventDefault();
                alert(errores.join('\n'));
            }
        });
    }
});