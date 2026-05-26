document.addEventListener('DOMContentLoaded', () => {
    const input      = document.getElementById('buscar-proveedor');
    const cards      = document.querySelectorAll('.emp-card');
    const grid       = document.getElementById('prov-grid');
    const empty      = document.getElementById('prov-empty');
    const counter    = document.getElementById('prov-count');
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
        if (counter) counter.textContent = visible;
        if (empty) empty.style.display  = visible === 0 ? 'flex' : 'none';
        if (grid)  grid.style.display   = visible === 0 ? 'none' : '';
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

    const logoUpload = document.getElementById('logo-upload');
    if (logoUpload) {
        logoUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(ev) {
                const img = document.getElementById('logo-img');
                if (!img) return;
                img.src = ev.target.result;
                img.style.display = 'block';
                const placeholder = document.getElementById('logo-placeholder');
                if (placeholder) placeholder.style.display = 'none';
            };
            reader.readAsDataURL(file);
        });
    }

    // Inicializar
    filterCards();
});
