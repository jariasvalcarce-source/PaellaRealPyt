/* ============================================
    CAMBIO DE LOGO (sidebar)
============================================ */
const logoUpload = document.getElementById('logo-upload');
if (logoUpload) {
    logoUpload.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (ev) {
            const img = document.getElementById('logo-img');
            if (img) {
                img.src = ev.target.result;
                img.style.display = 'block';
            }
            const placeholder = document.getElementById('logo-placeholder');
            if (placeholder) placeholder.style.display = 'none';
        };
        reader.readAsDataURL(file);
    });
}


/* ============================================
    CAMBIO DE IMAGEN DEL CHEF (hero banner)
============================================ */
const chefUpload = document.getElementById('chef-upload');
if (chefUpload) {
    chefUpload.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function (ev) {
            const img = document.getElementById('chef-img');
            if (img) {
                img.src = ev.target.result;
                img.style.display = 'block';
            }
            const fallback = document.getElementById('chef-fallback');
            if (fallback) fallback.style.display = 'none';
        };
        reader.readAsDataURL(file);
    });
}


/* ============================================
    DROPDOWN DE USUARIO (topbar)
    Abre/cierra al hacer clic en el avatar.
    Se cierra al hacer clic fuera.
============================================*/
const trigger  = document.getElementById('user-menu-trigger');
const dropdown = document.getElementById('user-dropdown');

if (trigger && dropdown) {
    trigger.addEventListener('click', function (e) {
        e.stopPropagation();
        dropdown.classList.toggle('open');
        const notifDropdown = document.getElementById('notif-dropdown');
        if (notifDropdown) notifDropdown.classList.remove('open');
    });

    document.addEventListener('click', function () {
        dropdown.classList.remove('open');
    });
}


/* ============================================
    NOTIFICACIONES
============================================ */
const notifBtn   = document.getElementById('notif-btn');
const notifBadge = document.getElementById('notif-badge');
const notifDropdown = document.getElementById('notif-dropdown');

if (notifBtn && notifBadge && notifDropdown) {
    const notifWrap = notifBtn.closest('.notif-wrap') || (function () {
        const wrap = document.createElement('div');
        wrap.className = 'notif-wrap';
        notifBtn.parentNode.insertBefore(wrap, notifBtn);
        wrap.appendChild(notifBtn);
        wrap.appendChild(notifDropdown);
        return wrap;
    })();

    notifBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        notifDropdown.classList.toggle('open');
        const userDropdown = document.getElementById('user-dropdown');
        if (userDropdown) userDropdown.classList.remove('open');
    });

    document.addEventListener('click', (e) => {
        if (!notifWrap.contains(e.target)) {
            notifDropdown.classList.remove('open');
        }
    });

    document.getElementById('notif-mark-all')?.addEventListener('click', () => {
        document.querySelectorAll('.notif-item.unread').forEach(item => {
            item.classList.remove('unread');
            const dot = item.querySelector('.notif-unread-dot');
            if (dot) dot.remove();
        });
        notifBadge.style.display = 'none';
    });
}


/* ============================================
    FILTROS DE TIEMPO (7d / 30d / 90d)
    Activa el botón presionado dentro del grupo.
============================================ */
document.querySelectorAll('.time-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const filterGroup = this.closest('.time-filter');
        if (filterGroup) {
            filterGroup.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
        }
        this.classList.add('active');
    });
});


/* ============================================
    COLORES BASE DE GRÁFICOS
============================================ */
const PRIMARY       = '#7B1535';
const PRIMARY_LIGHT = 'rgba(123,21,53,0.12)';


/* ============================================
    GRÁFICO DE LÍNEA — Ingresos Semanales
============================================ */
const lineChartEl = document.getElementById('lineChart');
if (lineChartEl) {
    const cData = window.chartData?.ingresosSemanales || {
        labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
        data: [520000, 480000, 610000, 590000, 720000, 850000, 460000]
    };
    new Chart(lineChartEl, {
        type: 'line',
        data: {
            labels: cData.labels,
            datasets: [{
                label: 'Ingresos',
                data: cData.data,
                borderColor: PRIMARY,
                backgroundColor: PRIMARY_LIGHT,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: PRIMARY,
                pointRadius: 3,
                pointHoverRadius: 5,
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#9ca3af', font: { size: 11 } }
                },
                y: {
                    grid: { color: '#f3f4f6' },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 11 },
                        callback: v => '$' + (v / 1000).toFixed(0) + 'k'
                    }
                }
            }
        }
    });
}


/* ============================================
    GRÁFICO DONUT — Categorías de ventas
============================================ */
const donutChartEl = document.getElementById('donutChart');
if (donutChartEl) {
    const donutData = window.chartData?.categorias || {
        labels: ['Paellas', 'Eventos', 'Domicilios'],
        data: [62, 23, 15]
    };
    const donutColors = ['#7B1535', '#c0536e', '#e8a0b0', '#f4cdd5', '#9a2b4b', '#d27c91'];
    
    // Fill legend
    const legendList = document.getElementById('donut-legend-list');
    if (legendList) {
        legendList.innerHTML = '';
        let total = donutData.data.reduce((a, b) => a + b, 0);
        if (total === 0) total = 1; // avoid division by zero
        
        donutData.labels.forEach((label, i) => {
            const pct = Math.round((donutData.data[i] / total) * 100);
            const color = donutColors[i % donutColors.length];
            legendList.innerHTML += `
                <li class="legend-item">
                    <span class="legend-label">
                        <span class="legend-dot" style="background:${color}"></span>${label}
                    </span>
                    <span class="legend-pct">${pct}%</span>
                </li>
            `;
        });
    }

    new Chart(donutChartEl, {
        type: 'doughnut',
        data: {
            labels: donutData.labels,
            datasets: [{
                data: donutData.data,
                backgroundColor: donutColors,
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '68%',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => ctx.label + ': ' + ctx.raw + '%'
                    }
                }
            }
        }
    });
}


/* ============================================
    GRÁFICO DE BARRAS — Ventas Mensuales
============================================ */
const barChartEl = document.getElementById('barChart');
if (barChartEl) {
    const barData = window.chartData?.ventasMensuales || {
        labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        data: [3200000, 2800000, 3600000, 4230000, 3900000, 4500000]
    };
    new Chart(barChartEl, {
        type: 'bar',
        data: {
            labels: barData.labels,
            datasets: [{
                label: 'Ventas',
                data: barData.data,
                backgroundColor: (ctx) =>
                    ctx.dataIndex === barData.data.length - 2 ? 'rgba(123,21,53,0.25)' : PRIMARY,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => 'Ventas: $' + ctx.raw.toLocaleString()
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#9ca3af', font: { size: 11 } }
                },
                y: {
                    grid: { color: '#f3f4f6' },
                    ticks: {
                        color: '#9ca3af',
                        font: { size: 11 },
                        callback: v => '$' + (v / 1000).toFixed(0) + 'k'
                    }
                }
            }
        }
    });
}