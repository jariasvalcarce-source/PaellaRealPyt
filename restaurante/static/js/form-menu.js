document.addEventListener('DOMContentLoaded', () => {
    const btnTipo = document.getElementById('toggle-tipo');
    const formTipo = document.getElementById('form-tipo');
    const cancelTipo = document.getElementById('cancel-tipo');

    if (btnTipo && formTipo) {
        btnTipo.addEventListener('click', () => {
            const open = formTipo.hidden === false;
            formTipo.hidden = open;
            btnTipo.setAttribute('aria-expanded', !open);
            btnTipo.classList.toggle('active', !open);
        });
    }

    if (cancelTipo && formTipo && btnTipo) {
        cancelTipo.addEventListener('click', () => {
            formTipo.hidden = true;
            btnTipo.setAttribute('aria-expanded', false);
            btnTipo.classList.remove('active');
        });
    }
});
