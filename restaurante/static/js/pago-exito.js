// =========================================
// pago-exito.js
// =========================================

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
