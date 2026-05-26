// =========================================
// favoritos.js
// =========================================

// Mapa de categorías por id
const CATEGORIAS = {
    1: { label: 'Paella', icon: 'bx-dish' },
    2: { label: 'Paella', icon: 'bx-dish' },
    3: { label: 'Paella', icon: 'bx-dish' },
    4: { label: 'Bebida', icon: 'bx-drink' },
    7: { label: 'Bebida', icon: 'bx-drink' },
    6: { label: 'Postre', icon: 'bx-cookie' },
    8: { label: 'Postre', icon: 'bx-cookie' },
    9: { label: 'Postre', icon: 'bx-cookie' },
    10:{ label: 'Aperitivo', icon: 'bx-food-tag' },
    11:{ label: 'Aperitivo', icon: 'bx-food-tag' },
    12:{ label: 'Aperitivo', icon: 'bx-food-tag' },
};

let favoritos = {};
try {
    favoritos = JSON.parse(localStorage.getItem('paellaFavoritos') || '{}');
} catch (e) {
    favoritos = {};
}

if (Object.keys(favoritos).length === 0) {
    favoritos = {
        1: { id: 1, nombre: 'Paella Valenciana', precio: 45000, img: '../assets/img/menú/paella-valenciana.jpg', desc: 'Clásica paella con pollo, conejo y verduras frescas' },
        2: { id: 2, nombre: 'Paella de Mariscos', precio: 52000, img: '../assets/img/menú/paella-mariscos.jpg', desc: 'Deliciosa paella con mariscos frescos del día' },
        6: { id: 6, nombre: 'Flan Casero', precio: 12000, img: '../assets/img/menú/flan-coco.jpg', desc: 'Flan de huevo con caramelo artesanal' },
        9: { id: 9, nombre: 'Churros con Chocolate', precio: 10000, img: '../assets/img/menú/churros-chocolate.jpg', desc: 'Churros crujientes con salsa de chocolate caliente' },
    };
}

let idParaEliminar = null;

function renderFavoritos(filtro = '') {
    const grid    = document.getElementById('favGrid');
    const vacio   = document.getElementById('favVacio');
    const sinRes  = document.getElementById('sinResultados');
    const statEl  = document.getElementById('statCount');
    const badgeEl = document.getElementById('sidebarFavBadge');

    const items = Object.values(favoritos);
    const total = items.length;

    if (statEl) statEl.textContent = total;
    if (badgeEl) {
        badgeEl.textContent = total;
        badgeEl.style.display = total > 0 ? 'flex' : 'none';
    }

    if (total === 0) {
        if (grid) grid.innerHTML = '';
        if (vacio) vacio.style.display = 'flex';
        if (sinRes) sinRes.style.display = 'none';
        if (grid) grid.style.display = 'none';
        return;
    }

    if (vacio) vacio.style.display = 'none';
    if (grid) grid.style.display = 'grid';

    const filtrados = filtro
        ? items.filter(i => i.nombre.toLowerCase().includes(filtro.toLowerCase()))
        : items;

    if (filtrados.length === 0) {
        if (grid) grid.innerHTML = '';
        if (sinRes) sinRes.style.display = 'flex';
        return;
    }

    if (sinRes) sinRes.style.display = 'none';
    if (grid) {
        grid.innerHTML = filtrados.map((item, idx) => {
            const cat = CATEGORIAS[item.id] || { label: 'Plato', icon: 'bx-food-menu' };
            return `
                <div class="fav-card" style="animation-delay:${idx * 0.06}s">
                    <div class="fav-card-imagen">
                        <img src="${item.img}" alt="${item.nombre}"
                             onerror="this.src='../assets/img/logo.png'">
                        <div class="fav-card-corazon">
                            <i class='bx bxs-heart'></i>
                        </div>
                        <div class="fav-card-cat">
                            <i class='bx ${cat.icon}'></i> ${cat.label}
                        </div>
                    </div>
                    <div class="fav-card-body">
                        <div class="fav-card-nombre">${item.nombre}</div>
                        <div class="fav-card-desc">${item.desc || ''}</div>
                        <div class="fav-card-footer">
                            <div class="fav-card-precio">$${item.precio.toLocaleString('es-CO')}</div>
                            <div class="fav-card-acciones">
                                <button class="btn-quitar" onclick="confirmarEliminar(${item.id}, '${item.nombre.replace(/'/g, "\\'")}')">
                                    <i class='bx bx-heart-square'></i> Quitar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
}

function buscarFav(q) {
    renderFavoritos(q);
}

function confirmarEliminar(id, nombre) {
    idParaEliminar = id;
    const modalDesc = document.getElementById('modalEliminarDesc');
    if (modalDesc) {
        modalDesc.textContent = `"${nombre}" se eliminará de tu lista de favoritos.`;
    }

    const confirmBtn = document.getElementById('btnConfirmarEliminar');
    if (confirmBtn) {
        confirmBtn.onclick = () => {
            delete favoritos[id];
            guardarYRenderizar();
            cerrarModal('modalEliminar');
            alertaFavoritoEliminado();
        };
    }

    const modal = document.getElementById('modalEliminar');
    if (modal) modal.classList.add('show');
}

function confirmarLimpiarTodos() {
    if (Object.keys(favoritos).length === 0) {
        alertaNoFavoritosGuardados();
        return;
    }

    const modal = document.getElementById('modalLimpiar');
    if (modal) modal.classList.add('show');
}

function limpiarTodos() {
    favoritos = {};
    guardarYRenderizar();
    cerrarModal('modalLimpiar');
    alertaFavoritosLimpiados();
}

function guardarYRenderizar() {
    try {
        localStorage.setItem('paellaFavoritos', JSON.stringify(favoritos));
    } catch (e) {
        // ignore storage errors
    }
    const input = document.getElementById('inputBuscarFav');
    renderFavoritos(input ? input.value : '');
}

function cerrarModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove('show');
}

function toggleNotif(e) {
    e.stopPropagation();
    const dropdown = document.getElementById('notifDropdown');
    if (dropdown) dropdown.classList.toggle('open');
}

function cerrarDropdowns(e) {
    const dropdown = document.getElementById('notifDropdown');
    if (dropdown && !e.target.closest('.notif-wrap')) {
        dropdown.classList.remove('open');
    }
}

renderFavoritos();
document.addEventListener('click', cerrarDropdowns);
