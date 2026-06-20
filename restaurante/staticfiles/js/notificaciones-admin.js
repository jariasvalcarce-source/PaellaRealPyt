// =========================================
// notification-ui.js - Admin
// =========================================

const notificationBtn = document.querySelector('.notification-btn');
const notifDropdown = document.getElementById('notifDropdown');
const badgeCampana = document.getElementById('badge-campana') || document.querySelector('.notification-badge');
const badgeDrop = document.getElementById('badge-drop');
const sidebarBadge = document.getElementById('sidebar-badge');

function toggleNotifDropdown(e) {
    if (e) e.stopPropagation();

    if (notifDropdown) {
        const abierto = notifDropdown.classList.contains('show');
        notifDropdown.classList.toggle('show');
        notificationBtn?.classList.toggle('activa', !abierto);
        return;
    }

    window.location.href = 'notificaciones.html';
}

function toggleNotif(e) {
    return toggleNotifDropdown(e);
}

function cerrarNotifDropdown() {
    if (!notifDropdown) return;
    notifDropdown.classList.remove('show');
    notificationBtn?.classList.remove('activa');
}

document.addEventListener('click', function (e) {
    if (notifDropdown && !e.target.closest('.notif-wrap')) {
        cerrarNotifDropdown();
    }
});

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        cerrarNotifDropdown();
    }
});

function actualizarBadges() {
    const total = document.querySelectorAll('.notif-item.no-leida').length;

    if (badgeCampana) {
        badgeCampana.textContent = total;
        badgeCampana.style.display = total > 0 ? 'flex' : 'none';
    }

    if (sidebarBadge) {
        sidebarBadge.textContent = total;
        sidebarBadge.style.display = total > 0 ? 'flex' : 'none';
    }

    if (badgeDrop) {
        badgeDrop.textContent = total > 0
            ? `${total} nueva${total > 1 ? 's' : ''}`
            : 'Al día ✓';
        badgeDrop.style.background = total > 0 ? '#C8973A' : '#00b894';
    }
}

function leerItem(el) {
    if (!el || !el.classList.contains('no-leida')) return;
    el.classList.remove('no-leida');
    actualizarBadges();
}

function marcarTodasLeidas(e) {
    if (e) e.stopPropagation();
    const items = document.querySelectorAll('.notif-item.no-leida');

    if (items.length === 0) {
        return;
    }

    items.forEach(item => item.classList.remove('no-leida'));
    actualizarBadges();
}

actualizarBadges();

/* =======================
Notificaciones del Admin
======================== */

document.addEventListener('DOMContentLoaded', function () {
    let currentFilter = 'todas';
    const filterChips = document.querySelectorAll('.notif-filter-chip');
    const notifFullList = document.getElementById('notif-full-list');
    const notifEmpty = document.getElementById('notif-empty');
    const resultCount = document.getElementById('result-count');
    const countNoleidas = document.getElementById('count-noleidas');
    const countTodas = document.getElementById('count-todas');
    const badgeTop = document.getElementById('notif-badge-top');
    const btnMarkAll = document.getElementById('btn-mark-all');
    const btnDeleteRead = document.getElementById('btn-delete-read');
    const logoImg = document.getElementById('logo-img');
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');
    let toastTimer;

    if (logoImg) {
        logoImg.addEventListener('error', function () {
            logoImg.style.display = 'none';
        });
    }

    filterChips.forEach(chip => {
        chip.addEventListener('click', function () {
            filterChips.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter;
            applyFilter();
        });
    });

    function applyFilter() {
        const items = document.querySelectorAll('.notif-full-item');
        const groups = document.querySelectorAll('.notif-group-label');
        let visible = 0;

        items.forEach(item => {
            const cat = item.dataset.category;
            const unread = item.classList.contains('unread');
            let show = false;

            if (currentFilter === 'todas') show = true;
            else if (currentFilter === 'no-leidas') show = unread;
            else show = cat === currentFilter;

            item.style.display = show ? '' : 'none';
            if (show) visible++;
        });

        groups.forEach(group => {
            const gKey = group.dataset.group;
            const groupItems = [...items].filter(i => {
                let prev = i.previousElementSibling;
                while (prev) {
                    if (prev.classList.contains('notif-group-label')) {
                        return prev.dataset.group === gKey;
                    }
                    prev = prev.previousElementSibling;
                }
                return false;
            });
            const hasVisible = groupItems.some(i => i.style.display !== 'none');
            group.style.display = hasVisible ? '' : 'none';
        });

        notifEmpty.style.display = visible === 0 ? 'flex' : 'none';
        notifFullList.style.display = visible === 0 ? 'none' : '';
        resultCount.textContent = visible;
    }

    function markReadItem(item) {
        if (!item.classList.contains('unread')) return;
        item.classList.remove('unread');
        const dot = item.querySelector('.notif-unread-indicator');
        if (dot) dot.remove();
        const markBtn = item.querySelector('.notif-quick-btn:not(.delete)');
        if (markBtn) markBtn.remove();
        updateUnreadCount();
        showToast('Notificación marcada como leída');
    }

    function deleteNotifItem(item) {
        item.style.transition = 'opacity 0.25s, transform 0.25s';
        item.style.opacity = '0';
        item.style.transform = 'translateX(20px)';
        setTimeout(() => {
            item.remove();
            applyFilter();
            updateUnreadCount();
            updateTotalCount();
        }, 260);
        showToast('Notificación eliminada');
    }

    if (btnMarkAll) {
        btnMarkAll.addEventListener('click', () => {
            const unreadItems = document.querySelectorAll('.notif-full-item.unread');
            unreadItems.forEach(item => {
                item.classList.remove('unread');
                const dot = item.querySelector('.notif-unread-indicator');
                if (dot) dot.remove();
                const markBtn = item.querySelector('.notif-quick-btn:not(.delete)');
                if (markBtn) markBtn.remove();
            });
            updateUnreadCount();
            showToast('Todas las notificaciones marcadas como leídas');
        });
    }

    if (btnDeleteRead) {
        btnDeleteRead.addEventListener('click', () => {
            const readItems = document.querySelectorAll('.notif-full-item:not(.unread)');
            readItems.forEach(item => {
                item.style.transition = 'opacity 0.2s';
                item.style.opacity = '0';
            });
            setTimeout(() => {
                readItems.forEach(i => i.remove());
                applyFilter();
                updateTotalCount();
            }, 220);
            showToast(`${readItems.length} notificaciones eliminadas`);
        });
    }

    if (notifFullList) {
        notifFullList.addEventListener('click', (e) => {
            const actionBtn = e.target.closest('.notif-quick-btn');
            if (actionBtn) {
                e.stopPropagation();
                if (actionBtn.classList.contains('delete')) {
                    deleteNotifItem(actionBtn.closest('.notif-full-item'));
                } else {
                    markReadItem(actionBtn.closest('.notif-full-item'));
                }
                return;
            }

            const item = e.target.closest('.notif-full-item');
            if (item && item.classList.contains('unread')) {
                markReadItem(item);
            }
        });
    }

    function updateUnreadCount() {
        const count = document.querySelectorAll('.notif-full-item.unread').length;
        if (countNoleidas) countNoleidas.textContent = count;
        if (badgeTop) {
            if (count === 0) {
                badgeTop.style.display = 'none';
            } else {
                badgeTop.style.display = '';
                badgeTop.textContent = count;
            }
        }
    }

    function updateTotalCount() {
        const total = document.querySelectorAll('.notif-full-item').length;
        if (countTodas) countTodas.textContent = total;
        if (resultCount) resultCount.textContent = total;
    }

    function showToast(msg) {
        if (!toast || !toastMsg) return;
        toastMsg.textContent = msg;
        toast.classList.add('show');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => toast.classList.remove('show'), 3000);
    }
});
