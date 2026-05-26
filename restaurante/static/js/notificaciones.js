// =========================================
// notificaciones de los usuarios
// =========================================

const badgeTopbar = document.getElementById('badge-topbar');
const cntNuevas = document.getElementById('cnt-nuevas');
const cntNoLeidas = document.getElementById('fp-noleidas');
const cntTotal = document.getElementById('cnt-total');
const cntTodas = document.getElementById('fp-todas');
const estadoVacio = document.getElementById('estado-vacio');

function actualizarContadores() {
    const noLeidasCards = document.querySelectorAll('.notif-card.no-leida');
    const visibles = document.querySelectorAll('.notif-card:not(.eliminando)').length;

    if (cntNuevas) cntNuevas.textContent = noLeidasCards.length;
    if (cntNoLeidas) cntNoLeidas.textContent = noLeidasCards.length;
    if (badgeTopbar) {
        if (noLeidasCards.length > 0) {
            badgeTopbar.textContent = noLeidasCards.length;
            badgeTopbar.style.display = 'flex';
        } else {
            badgeTopbar.style.display = 'none';
        }
    }
    if (cntTotal) cntTotal.textContent = visibles;
    if (cntTodas) cntTodas.textContent = visibles;
}

function leerNotif(card) {
    if (!card.classList.contains('no-leida')) return;
    card.classList.remove('no-leida');
    actualizarContadores();
}

function marcarTodasLeidas() {
    const noLeidasCards = document.querySelectorAll('.notif-card.no-leida');
    if (noLeidasCards.length === 0) {
        return alertaTodoAlDia();
    }

    noLeidasCards.forEach(c => c.classList.remove('no-leida'));
    actualizarContadores();
    alertaNotificacionesLeidas();
}

function eliminarNotif(event, btn) {
    event.stopPropagation();
    const card = btn.closest('.notif-card');
    if (!card) return;

    card.classList.add('eliminando');
    card.addEventListener('animationend', () => {
        card.remove();
        actualizarContadores();
        verificarVacio();
    });
}

function verificarVacio() {
    const visibles = document.querySelectorAll('.notif-card').length;
    if (estadoVacio) {
        estadoVacio.style.display = visibles === 0 ? 'flex' : 'none';
    }
}

function filtrar(btn) {
    document.querySelectorAll('.filtro-notif').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const filtro = btn.dataset.filtro;
    const cards = document.querySelectorAll('.notif-card');

    cards.forEach(card => {
        const tipo = card.dataset.tipo;
        const noLeida = card.classList.contains('no-leida');
        let mostrar = false;

        if (filtro === 'todas') mostrar = true;
        else if (filtro === 'no-leida') mostrar = noLeida;
        else mostrar = tipo === filtro;

        card.style.display = mostrar ? 'flex' : 'none';
    });

    document.querySelectorAll('.notif-grupo').forEach(grupo => {
        const visiblesGrupo = [...grupo.querySelectorAll('.notif-card')]
            .filter(c => c.style.display !== 'none').length;
        grupo.style.display = visiblesGrupo > 0 ? 'block' : 'none';
    });

    const hayAlgo = [...cards].some(c => c.style.display !== 'none');
    if (estadoVacio) {
        estadoVacio.style.display = hayAlgo ? 'none' : 'flex';
    }
}

actualizarContadores();
