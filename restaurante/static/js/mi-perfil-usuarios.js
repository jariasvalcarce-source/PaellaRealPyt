// =========================================
// Perfil Uusuarios
// =========================================

const perfilForm = document.getElementById('perfilForm');
const modalConfirm = document.getElementById('modalConfirm');
const toast = document.getElementById('toast');

if (perfilForm) {
    perfilForm.addEventListener('submit', function (e) {
        e.preventDefault();
        modalConfirm?.classList.add('show');
    });
}

function cerrarModal() {
    modalConfirm?.classList.remove('show');
}

function confirmarGuardar() {
    cerrarModal();

    const nombres = document.querySelector('input[name="nombres"]').value;
    const apellidos = document.querySelector('input[name="apellidos"]').value;
    const nombreCompleto = `${nombres} ${apellidos}`.trim();

    const heroNombre = document.querySelector('.perfil-hero-info h1');
    if (heroNombre) heroNombre.textContent = nombreCompleto;

    if (toast) {
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3500);
    }
}

if (modalConfirm) {
    modalConfirm.addEventListener('click', function (e) {
        if (e.target === this) cerrarModal();
    });
}
