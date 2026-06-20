document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('buscar');
    const filterButtons = document.querySelectorAll('.emp-filter-btn');
    const cards = document.querySelectorAll('.emp-card');

    function filtrar(estado) {
        filterButtons.forEach(button => {
            button.classList.toggle('active', button.getAttribute('onclick')?.includes(`filtrar('${estado}'`));
        });

        cards.forEach(card => {
            card.style.display = (estado === 'todos' || card.dataset.estado === estado) ? '' : 'none';
        });
    }

    function buscar(query) {
        const texto = query.toLowerCase();
        cards.forEach(card => {
            card.style.display = card.innerText.toLowerCase().includes(texto) ? '' : 'none';
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', function () {
            buscar(this.value);
        });
    }

    window.filtrar = filtrar;
});
