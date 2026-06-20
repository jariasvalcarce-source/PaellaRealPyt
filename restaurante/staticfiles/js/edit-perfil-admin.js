// ============================================
// edit-perfil-admin.js
// ============================================

document.addEventListener('DOMContentLoaded', function () {
    const avatarInput = document.getElementById('avatarInput');
    const avatarPreview = document.getElementById('avatarPreview');
    const avatarFallback = document.getElementById('avatarFallback');
    const btnEditarPerfil = document.querySelector('.btn-editar-perfil');
    const btnVolverDashboard = document.querySelector('.btn-accion-header');
    const btnCancelar = document.querySelector('.btn-cancel');
    const perfilForm = document.getElementById('perfilForm');
    const togglePassButtons = document.querySelectorAll('.toggle-pass');

    if (avatarPreview && avatarFallback) {
        avatarPreview.onerror = function () {
            avatarPreview.style.display = 'none';
            avatarFallback.style.display = 'flex';
        };
    }

    if (avatarInput && avatarPreview && avatarFallback) {
        avatarInput.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (e) {
                avatarPreview.src = e.target.result;
                avatarPreview.style.display = 'block';
                avatarFallback.style.display = 'none';
            };
            reader.readAsDataURL(file);
        });
    }

    togglePassButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const inputId = button.dataset.target;
            const input = document.getElementById(inputId);
            if (!input) return;

            const show = input.type === 'password';
            input.type = show ? 'text' : 'password';
            button.classList.toggle('active', show);
        });
    });

    if (btnEditarPerfil) {
        btnEditarPerfil.addEventListener('click', function () {
            window.location.href = '../admin/edit-perfil.html';
        });
    }

    if (btnVolverDashboard) {
        btnVolverDashboard.addEventListener('click', function () {
            window.location.href = '../admin/dashboard-admin.html';
        });
    }

    if (btnCancelar) {
        btnCancelar.addEventListener('click', function () {
            if (window.confirm('¿Deseas cancelar los cambios y regresar al dashboard?')) {
                window.history.back();
            }
        });
    }

    if (perfilForm) {
        perfilForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const btn = perfilForm.querySelector('.btn-primary');
            if (!btn) return;

            btn.textContent = '✓ Guardado';
            btn.style.background = '#16a34a';

            setTimeout(function () {
                btn.innerHTML = '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0z" /></svg> Guardar Cambios';
                btn.style.background = '';
            }, 2000);
        });
    }
});