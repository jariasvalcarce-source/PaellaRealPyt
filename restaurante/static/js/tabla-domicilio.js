document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('buscar');

    window.currentFilter = 'todos';
    window.currentSearch = '';

    function filtrar(estado) {
        window.currentFilter = estado;
        const filterButtons = document.querySelectorAll('.emp-filter-btn');
        filterButtons.forEach(button => {
            button.classList.toggle('active', button.getAttribute('onclick').includes(`filtrar('${estado}'`));
        });

        const cards = document.querySelectorAll('.emp-card');
        cards.forEach(card => {
            let matchesEstado = (estado === 'todos' || card.dataset.estado === estado);
            let matchesBusqueda = true;
            if (window.currentSearch.trim() !== '') {
                matchesBusqueda = card.innerText.toLowerCase().includes(window.currentSearch.toLowerCase());
            }
            card.style.display = (matchesEstado && matchesBusqueda) ? '' : 'none';
        });
    }

    function buscar(query) {
        window.currentSearch = query;
        filtrar(window.currentFilter);
    }

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            buscar(this.value);
        });
    }

    window.filtrar = filtrar;
    window.buscar = buscar;

    document.body.addEventListener('htmx:afterSwap', function(evt) {
        if(evt.detail.target.id === 'lista-domicilios') {
            filtrar(window.currentFilter);
        }
    });
});
