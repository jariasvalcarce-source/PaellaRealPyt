/* ====================
Ajustes del Admin
==================== */

document.addEventListener('DOMContentLoaded', function () {
    let toastTimer;

    /* ===================================================================
        NAVEGACIÓN ENTRE PANELES
        Cambiar entre las diferentes secciones de ajustes
    =================================================================== */

    document.querySelectorAll('.settings-nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const panelId = 'panel-' + item.dataset.panel;

            // Remover clase 'active' de todos los elementos
            document.querySelectorAll('.settings-nav-item').forEach(i => i.classList.remove('active'));
            document.querySelectorAll('.settings-panel').forEach(p => p.classList.remove('active'));

            // Agregar clase 'active' al elemento actual
            item.classList.add('active');
            document.getElementById(panelId)?.classList.add('active');
        });
    });

    /* ===================================================================
        CARGA Y VISTA PREVIA DE AVATAR
        Permitir al usuario seleccionar imagen de perfil
    =================================================================== */

    document.getElementById('avatar-upload')?.addEventListener('change', function () {
        const file = this.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            const big = document.getElementById('avatar-big');
            let img = big.querySelector('img');
            if (!img) {
                img = document.createElement('img');
                big.prepend(img);
            }
            img.src = e.target.result;
            big.style.fontSize = '0';
        };
        reader.readAsDataURL(file);
        showToast('Foto de perfil actualizada');
    });

    /* ===================================================================
        MODALES - ABRIR Y CERRAR
        Gestionar diálogos de confirmación
    =================================================================== */

    function openModal(id) {
        document.getElementById(id)?.classList.add('open');
    }
    function closeModal(id) {
        document.getElementById(id)?.classList.remove('open');
    }

    // Cerrar modal al hacer clic en el overlay
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.classList.remove('open');
        });
    });

    /* ===================================================================
        EVENT LISTENERS DINÁMICOS
        Escuchar clics en elementos con data-action
    =================================================================== */

    document.querySelectorAll('[data-action]').forEach(el => {
        const action = el.dataset.action;
        if (action === 'openModal') {
            el.addEventListener('click', () => openModal(el.dataset.modal));
        } else if (action === 'closeModal') {
            el.addEventListener('click', () => closeModal(el.dataset.modal));
        } else if (action === 'showToast') {
            el.addEventListener('click', () => showToast(el.dataset.message));
        }
    });

    /* ===================================================================
        NOTIFICACIONES TIPO TOAST
        Mostrar mensajes flotantes al usuario
    =================================================================== */

    function showToast(msg) {
        const toast = document.getElementById('toast');
        document.getElementById('toast-msg').textContent = msg;
        toast.classList.add('show');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
    }

    /* ===================================================================
        EXPOSICIÓN GLOBAL DE FUNCIONES
        Funciones disponibles en el scope global para onclick heredados
    =================================================================== */

    window.openModal = openModal;
    window.closeModal = closeModal;
    window.showToast = showToast;
});
