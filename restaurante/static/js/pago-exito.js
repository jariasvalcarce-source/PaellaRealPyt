// =========================================
// pago-exito.js
// =========================================

document.addEventListener('DOMContentLoaded', () => {
    // Cuando se llega a esta pantalla (pago exitoso), vaciar el carrito para este usuario
    const carritoKey = window.PAELLA_CARRITO_KEY || 'miCarritoPaella';
    localStorage.removeItem(carritoKey);
});

function toggleUserMenu() {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

window.onclick = function (e) {
    const dropdown = document.getElementById('userDropdown');
    if (!e.target.closest('.sidebar-footer') && dropdown) {
        dropdown.classList.remove('show');
    }
};
