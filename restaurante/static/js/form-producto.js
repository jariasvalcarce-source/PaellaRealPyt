const btnUnidad = document.getElementById('toggle-unidad');
const formUnidad = document.getElementById('form-unidad');
const cancelUnidad = document.getElementById('cancel-unidad');
const btnCategoria = document.getElementById('toggle-categoria');
const formCategoria = document.getElementById('form-categoria');
const cancelCategoria = document.getElementById('cancel-categoria');
const btnVerProductos = document.getElementById('btn-ver-productos');

function toggleUnidad() {
    const open = formUnidad.hidden === false;
    formUnidad.hidden = open;
    btnUnidad.setAttribute('aria-expanded', !open);
    btnUnidad.classList.toggle('active', !open);
    if (!open) formCategoria.hidden = true;
}

function closeUnidad() {
    formUnidad.hidden = true;
    btnUnidad.setAttribute('aria-expanded', false);
    btnUnidad.classList.remove('active');
}

function toggleCategoria() {
    const open = formCategoria.hidden === false;
    formCategoria.hidden = open;
    btnCategoria.setAttribute('aria-expanded', !open);
    btnCategoria.classList.toggle('active', !open);
    if (!open) formUnidad.hidden = true;
}

function closeCategoria() {
    formCategoria.hidden = true;
    btnCategoria.setAttribute('aria-expanded', false);
    btnCategoria.classList.remove('active');
}

function initFormProducto() {
    btnUnidad.addEventListener('click', toggleUnidad);
    cancelUnidad.addEventListener('click', closeUnidad);
    btnCategoria.addEventListener('click', toggleCategoria);
    cancelCategoria.addEventListener('click', closeCategoria);

    if (btnVerProductos) {
        btnVerProductos.addEventListener('click', () => {
            window.location.href = '../inventario/tabla-productos.html';
        });
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFormProducto);
} else {
    initFormProducto();
}
