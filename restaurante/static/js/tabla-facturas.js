document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('buscar-factura');
    const cards = Array.from(document.querySelectorAll('.emp-card'));
    const grid = document.getElementById('fac-grid');
    const empty = document.getElementById('fac-empty');
    const counter = document.getElementById('fac-count');
    const filterBtns = Array.from(document.querySelectorAll('.emp-filter-btn'));
    let activeFilter = 'todos';

    function updateResults() {
        const query = input ? input.value.toLowerCase().trim() : '';
        let visible = 0;

        cards.forEach(card => {
            const matchSearch = !query ||
                card.dataset.nombre.toLowerCase().includes(query) ||
                card.dataset.factura.toLowerCase().includes(query) ||
                card.dataset.pedido.toLowerCase().includes(query);
            const matchFilter = activeFilter === 'todos' || card.dataset.estado === activeFilter;
            const show = matchSearch && matchFilter;

            card.style.display = show ? '' : 'none';
            if (show) visible++;
        });

        if (counter) {
            counter.textContent = String(visible);
        }

        if (empty) {
            empty.style.display = visible === 0 ? 'flex' : 'none';
        }

        if (grid) {
            grid.style.display = visible === 0 ? 'none' : '';
        }
    }

    if (input) {
        input.addEventListener('input', updateResults);
    }

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeFilter = btn.dataset.filter || 'todos';
            updateResults();
        });
    });

    const logoUpload = document.getElementById('logo-upload');
    const logoImg = document.getElementById('logo-img');
    const logoPlaceholder = document.getElementById('logo-placeholder');

    const printButton = document.getElementById('btn-print-facturas');

    if (logoUpload && logoImg && logoPlaceholder) {
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

    if (printButton) {
        printButton.addEventListener('click', () => {
            window.print();
        });
    }

    updateResults();
});
