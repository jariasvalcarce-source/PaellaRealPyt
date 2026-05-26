/* ====================
Inicio Usuarios
==================== */

// ── Toggle menú de usuario ──
function toggleUserMenu() {
    document.getElementById('userDropdown').classList.toggle('show');
}

window.onclick = function(event) {
    if (!event.target.closest('.user-profile-container')) {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) dropdown.classList.remove('show');
    }
}

// ── Cerrar sesión ──
function cerrarSesion() {
    window.location.href = 'login.html';
}

// ── Toggle contraseña en modal ──
function toggleModalPassword(icon, inputId) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('bx-show');
        icon.classList.add('bx-hide');
    } else {
        input.type = 'password';
        icon.classList.remove('bx-hide');
        icon.classList.add('bx-show');
    }
}

// ── Animaciones de entrada con IntersectionObserver ──
document.addEventListener('DOMContentLoaded', function () {

    const observerOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -40px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll(
        '.category-card, .featured-card, .info-card, .cta-section'
    ).forEach(el => {
        el.classList.add('reveal');
        observer.observe(el);
    });
});

// =========================================
// inicio-usuarios.js - Notificaciones
// =========================================

const btnCampana = document.getElementById('btnCampana');
const dropdown = document.getElementById('notifDropdown');
const badgeCampana = document.getElementById('badge-campana');
const badgeDrop = document.getElementById('badge-drop');
const sidebarBadge = document.getElementById('sidebar-badge');

function toggleNotifDropdown(e) {
    e.stopPropagation();
    const abierto = dropdown.classList.contains('show');
    dropdown.classList.toggle('show');
    btnCampana.classList.toggle('activa', !abierto);
}

function cerrarNotifDropdown() {
    if (!dropdown) return;
    dropdown.classList.remove('show');
    btnCampana?.classList.remove('activa');
}

document.addEventListener('click', function (e) {
    if (!e.target.closest('.notif-wrap')) {
        cerrarNotifDropdown();
    }
});

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        cerrarNotifDropdown();
    }
});

function actualizarBadges() {
    const total = document.querySelectorAll('.notif-item.no-leida').length;

    if (badgeCampana) {
        badgeCampana.textContent = total;
        badgeCampana.style.display = total > 0 ? 'flex' : 'none';
    }

    if (sidebarBadge) {
        sidebarBadge.textContent = total;
        sidebarBadge.style.display = total > 0 ? 'flex' : 'none';
    }

    if (badgeDrop) {
        badgeDrop.textContent = total > 0
            ? `${total} nueva${total > 1 ? 's' : ''}`
            : 'Al día ✓';
        badgeDrop.style.background = total > 0 ? '#C8973A' : '#00b894';
    }
}

function leerItem(el) {
    el.classList.remove('no-leida');
    actualizarBadges();
}

function marcarTodasLeidas(e) {
    e.stopPropagation();
    document.querySelectorAll('.notif-item.no-leida')
        .forEach(item => item.classList.remove('no-leida'));
    actualizarBadges();
}

actualizarBadges();