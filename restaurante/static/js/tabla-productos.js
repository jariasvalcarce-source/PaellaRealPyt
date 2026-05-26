const input = document.getElementById('buscar-producto');
const cards = document.querySelectorAll('#prod-grid .emp-card');
const grid = document.getElementById('prod-grid');
const empty = document.getElementById('prod-empty');
const counter = document.getElementById('prod-count');
const filterBtns = document.querySelectorAll('.emp-filter-btn');
let activeFilter = 'todos';

function filterCards() {
    const q = input.value.toLowerCase().trim();
    let visible = 0;

    cards.forEach(card => {
        const matchSearch = !q
            || card.dataset.nombre.toLowerCase().includes(q)
            || card.dataset.categoria.toLowerCase().includes(q)
            || card.dataset.proveedor.toLowerCase().includes(q);
        const matchFilter = activeFilter === 'todos' || card.dataset.estado === activeFilter;
        const show = matchSearch && matchFilter;

        card.style.display = show ? '' : 'none';
        if (show) visible++;
    });

    counter.textContent = visible;
    empty.style.display = visible === 0 ? 'flex' : 'none';
    grid.style.display = visible === 0 ? 'none' : '';
}

input.addEventListener('input', filterCards);

filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeFilter = btn.dataset.filter;
        filterCards();
    });
});

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
}
