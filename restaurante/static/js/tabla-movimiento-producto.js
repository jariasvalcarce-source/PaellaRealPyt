document.addEventListener('DOMContentLoaded', () => {
    const input      = document.getElementById('buscar-movimiento');
    const cards      = document.querySelectorAll('#movi-grid .emp-card');
    const grid       = document.getElementById('movi-grid');
    const empty      = document.getElementById('movi-empty');
    const counter    = document.getElementById('movi-count');
    const filterBtns = document.querySelectorAll('.emp-filter-btn');
    let activeFilter = 'todos';

    function filterCards() {
        const q = input.value.toLowerCase().trim();
        let visible = 0;
        cards.forEach(card => {
            const matchSearch = !q
                || card.dataset.producto.toLowerCase().includes(q)
                || card.dataset.motivo.toLowerCase().includes(q)
                || card.dataset.responsable.toLowerCase().includes(q);
            const matchFilter = activeFilter === 'todos' || card.dataset.tipo === activeFilter;
            const show = matchSearch && matchFilter;
            card.style.display = show ? '' : 'none';
            if (show) visible++;
        });
        counter.textContent = visible;
        empty.style.display = visible === 0 ? 'flex' : 'none';
        grid.style.display  = visible === 0 ? 'none' : '';
    }

    if (input) input.addEventListener('input', filterCards);
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeFilter = btn.dataset.filter;
            filterCards();
        });
    });

    // Inicializar estado
    filterCards();
});
