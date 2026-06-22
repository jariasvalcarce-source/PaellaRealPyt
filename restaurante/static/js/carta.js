// =========================================
// carta.js
// =========================================

// Favoritos (localStorage)
const FAVORITOS_STORAGE_KEY = window.PAELLA_FAVORITOS_KEY || 'paellaFavoritos';
const FAVORITOS_LEGACY_KEY  = 'paellaFavoritos';

function cargarFavoritos() {
    try {
        const actual = JSON.parse(localStorage.getItem(FAVORITOS_STORAGE_KEY) || '{}') || {};
        if (Object.keys(actual).length > 0) {
            return actual;
        }

        const legacy = JSON.parse(localStorage.getItem(FAVORITOS_LEGACY_KEY) || '{}') || {};
        if (Object.keys(legacy).length > 0) {
            localStorage.setItem(FAVORITOS_STORAGE_KEY, JSON.stringify(legacy));
            localStorage.removeItem(FAVORITOS_LEGACY_KEY);
            return legacy;
        }
    } catch (e) {
        // Si hay un error al parsear, ignorar y usar un objeto vacío.
    }
    return {};
}

let favoritos = cargarFavoritos();

function guardarFavoritos() {
    localStorage.setItem(FAVORITOS_STORAGE_KEY, JSON.stringify(favoritos));
    actualizarBadge();
}

function actualizarBadge() {
    const count = Object.keys(favoritos).length;
    const floatBadge = document.getElementById('floatingFavBadge');
    if (floatBadge) floatBadge.textContent = count;

    const sb = document.getElementById('sidebar-fav-badge');
    if (sb) {
        if (count > 0) {
            sb.textContent = count;
            sb.style.display = 'flex';
        } else {
            sb.style.display = 'none';
        }
    }
}

function toggleLike(btn, id, nombre, precio, img, desc) {
    btn.classList.add('pop');
    btn.addEventListener('animationend', () => btn.classList.remove('pop'), { once: true });

    let csrfToken = '';
    const form = document.getElementById('csrf-form-global');
    if (form) {
        const input = form.querySelector('[name=csrfmiddlewaretoken]');
        if (input) csrfToken = input.value;
    }

    if (favoritos[id]) {
        delete favoritos[id];
        btn.classList.remove('liked');
        btn.querySelector('i').className = 'bx bx-heart';
        alertaFavoritoEliminado();
    } else {
        favoritos[id] = { id, nombre, precio, img, desc };
        btn.classList.add('liked');
        btn.querySelector('i').className = 'bx bxs-heart';
        alertaFavoritoAgregado();
    }

    guardarFavoritos();
    
    // Sync with backend database
    if (csrfToken) {
        fetch(`/usuarios/sync/favorito/${id}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        }).catch(err => console.error("Error sincronizando favorito:", err));
    }
}

function filtrar(btn, tipo) {
    document.querySelectorAll('.filtro-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.categoria-menu').forEach(cat => {
        cat.style.display = (tipo === 'todos' || cat.dataset.tipo === tipo)
            ? 'block'
            : 'none';
    });
}

function buscar(q) {
    q = q.toLowerCase().trim();
    document.querySelectorAll('.producto-card').forEach(card => {
        const nombre = (card.dataset.nombre || '').toLowerCase();
        card.style.display = (!q || nombre.includes(q)) ? '' : 'none';
    });
}

function toggleNotifDropdown(event) {
    event.stopPropagation();
    const dropdown = document.getElementById('notifDropdown');
    if (dropdown) {
        dropdown.classList.toggle('open');
    }
}

function leerItem(item) {
    if (item.classList.contains('no-leida')) {
        item.classList.remove('no-leida');
        const badge = document.getElementById('badge-campana');
        const badgeDrop = document.getElementById('badge-drop');
        let count = parseInt(badge.textContent) - 1;
        if (isNaN(count) || count < 0) count = 0;
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
        badgeDrop.textContent = count > 0 ? count + ' nuevas' : 'Todo leído';
    }
}

function marcarTodasLeidas(event) {
    event.stopPropagation();
    document.querySelectorAll('.notif-item.no-leida').forEach(i => i.classList.remove('no-leida'));
    const badge = document.getElementById('badge-campana');
    if (badge) {
        badge.textContent = '0';
        badge.style.display = 'none';
    }
    const badgeDrop = document.getElementById('badge-drop');
    if (badgeDrop) {
        badgeDrop.textContent = 'Todo leído';
    }
}

function cerrarDropdownsAlClicar(event) {
    const dropdown = document.getElementById('notifDropdown');
    if (dropdown && !event.target.closest('.notif-wrap')) {
        dropdown.classList.remove('open');
    }
}

function initLikes() {
    document.querySelectorAll('.btn-like').forEach(btn => {
        const onclick = btn.getAttribute('onclick');
        const match = onclick && onclick.match(/toggleLike\(this,\s*(\d+),/);
        if (match) {
            const id = match[1];
            if (favoritos[id]) {
                btn.classList.add('liked');
                btn.querySelector('i').className = 'bx bxs-heart';
            }
        }
    });
    actualizarBadge();
}

// Inicialización
initLikes();
document.addEventListener('click', cerrarDropdownsAlClicar);
