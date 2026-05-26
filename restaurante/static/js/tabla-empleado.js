const input = document.getElementById('buscar-empleado');
const cards = document.querySelectorAll('.emp-card');
const grid = document.getElementById('emp-grid');
const empty = document.getElementById('emp-empty');
const counter = document.getElementById('emp-count');
const filterBtns = document.querySelectorAll('.emp-filter-btn');
let activeFilter = 'todos';

function filterCards() {
    const q = input.value.toLowerCase().trim();
    let visible = 0;

    cards.forEach(card => {
        const matchSearch = !q
            || card.dataset.nombre.toLowerCase().includes(q)
            || card.dataset.correo.toLowerCase().includes(q)
            || card.dataset.telefono.includes(q);
        const matchFilter = activeFilter === 'todos' || card.dataset.estado === activeFilter;
        const show = matchSearch && matchFilter;

        card.style.display = show ? '' : 'none';
        if (show) visible++;
    });

    counter.textContent = visible;
    empty.style.display = visible === 0 ? 'flex' : 'none';
    grid.style.display = visible === 0 ? 'none' : '';
}

function initializeFilters() {
    input.addEventListener('input', filterCards);
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeFilter = btn.dataset.filter;
            filterCards();
        });
    });
}

function initializeLogoUpload() {
    const logoUpload = document.getElementById('logo-upload');
    const logoImg = document.getElementById('logo-img');
    const logoPlaceholder = document.getElementById('logo-placeholder');

    logoImg.addEventListener('error', () => {
        logoImg.style.display = 'none';
        logoPlaceholder.style.display = 'flex';
    });

    logoUpload.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (ev) {
            logoImg.src = ev.target.result;
            logoImg.style.display = 'block';
            logoPlaceholder.style.display = 'none';
        };
        reader.readAsDataURL(file);
    });
}

function initTablaEmpleado() {
    initializeFilters();
    initializeLogoUpload();

    // --- Lógica de SweetAlert2 para Toasts ---
    if (typeof Swal !== 'undefined') {
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 4000,
            timerProgressBar: true,
            background: '#fff',
            color: '#333',
            didOpen: (toast) => {
                toast.onmouseenter = Swal.stopTimer;
                toast.onmouseleave = Swal.resumeTimer;
            }
        });

        const msgs = document.querySelectorAll('.django-message');
        msgs.forEach(msg => {
            Toast.fire({
                icon: msg.getAttribute('data-type'),
                title: msg.innerText
            });
        });
        
        // --- Confirmación de Envío del Formulario (Editar) ---
        const editForm = document.getElementById('editForm');
        if (editForm) {
            editForm.addEventListener('submit', function(e) {
                e.preventDefault();
                // Validar usando checkValidity de HTML5
                if (!this.checkValidity()) {
                    this.reportValidity();
                    return;
                }
                
                Swal.fire({
                    title: '¿Estás seguro?',
                    text: "Se actualizarán los datos de este empleado.",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: 'var(--primary)',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Sí, guardar cambios',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        this.submit();
                    }
                });
            });
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTablaEmpleado);
} else {
    initTablaEmpleado();
}
