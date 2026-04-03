// ──────────────────────────────────────────────────────────
// ESTADO GLOBAL
// ──────────────────────────────────────────────────────────

const carrito           = {};  // { id: { nombre, precio, img, cantidad } }
const advertenciasStock = {};  // { id: mensajeAdvertencia }


// ──────────────────────────────────────────────────────────
// VERIFICACIÓN DE STOCK (AJAX)
// ──────────────────────────────────────────────────────────

async function verificarStock(menuId, qty) {
    try {
        const resp = await fetch(`/usuario/carrito/stock/${menuId}/?qty=${qty}`);
        return await resp.json();
    } catch (e) {
        // Si falla la red, permitir el pedido igual sin bloquear
        return { disponible: true, advertencia: false, mensaje: '' };
    }
}


// ──────────────────────────────────────────────────────────
// PANTALLA DE ADVERTENCIA DE STOCK
// ──────────────────────────────────────────────────────────

function mostrarToastStock(mensaje) {
    const anterior = document.getElementById('toast-stock');
    if (anterior) anterior.remove();

    const toast = document.createElement('div');
    toast.id = 'toast-stock';
    toast.innerHTML = `
        <div style="
            position:fixed; bottom:2rem; left:50%; transform:translateX(-50%);
            background:#fff3cd; border:1.5px solid #f5a623; border-radius:12px;
            padding:.9rem 1.4rem; display:flex; align-items:flex-start; gap:.7rem;
            box-shadow:0 8px 30px rgba(0,0,0,.15); z-index:9999;
            max-width:420px; width:90%; animation: slideUp .3s ease;
        ">
            <i class='bx bx-info-circle' style="color:#f5a623;font-size:1.3rem;flex-shrink:0;margin-top:2px;"></i>
            <div>
                <strong style="display:block;font-size:.9rem;color:#1a1a2e;margin-bottom:2px;">
                    Stock limitado
                </strong>
                <span style="font-size:.82rem;color:#555;">${mensaje}</span>
            </div>
            <button onclick="document.getElementById('toast-stock').remove()"
                    style="background:none;border:none;cursor:pointer;color:#999;font-size:1.1rem;margin-left:.5rem;flex-shrink:0;">
                <i class='bx bx-x'></i>
            </button>
        </div>
        <style>
          @keyframes slideUp {
            from { opacity:0; transform:translateX(-50%) translateY(20px); }
            to   { opacity:1; transform:translateX(-50%) translateY(0); }
          }
        </style>
    `;
    document.body.appendChild(toast);
    setTimeout(() => { const t = document.getElementById('toast-stock'); if (t) t.remove(); }, 7000);
}


// ──────────────────────────────────────────────────────────
// MARCAR / LIMPIAR TARJETA SIN STOCK
// ──────────────────────────────────────────────────────────

function marcarCardSinStock(id) {
    const card = document.querySelector(`.producto-card[data-id="${id}"]`);
    if (!card) return;
    card.classList.add('sin-stock');
    // Deshabilitar botones de cantidad
    card.querySelectorAll('.qty-btn, .btn-add-cart').forEach(btn => btn.disabled = true);
    // Inyectar badge si no existe
    if (!card.querySelector('.badge-sin-stock')) {
        const badge = document.createElement('div');
        badge.className = 'badge-sin-stock';
        badge.innerHTML = `<i class='bx bx-x-circle'></i> No disponible en este momento`;
        const img = card.querySelector('.producto-imagen');
        if (img) img.appendChild(badge);
    }
}

function limpiarCardSinStock(id) {
    const card = document.querySelector(`.producto-card[data-id="${id}"]`);
    if (!card) return;
    card.classList.remove('sin-stock');
    card.querySelectorAll('.qty-btn, .btn-add-cart').forEach(btn => btn.disabled = false);
    const badge = card.querySelector('.badge-sin-stock');
    if (badge) badge.remove();
}


async function cambiarCantidad(id, delta, nombre, precio, img) {
    const actual = carrito[id] ? carrito[id].cantidad : 0;
    const nueva  = actual + delta;

    // Verificar stock siempre que se intente aumentar la cantidad
    if (delta > 0) {
        const stockData = await verificarStock(id, nueva);

        if (stockData.advertencia) {
            const menuNombre = nombre || document.querySelector(`.producto-card[data-id="${id}"] h4`)?.textContent || 'este menú';

            Swal.fire({
                icon: 'info',
                title: '😔 ¡Lo sentimos mucho!',
                html: `
                    <p style="font-size:0.97rem;color:#444;margin:0 0 .5rem;">
                        En este momento <strong>no contamos con suficientes productos</strong>
                        para preparar <em>${menuNombre}</em>.
                    </p>
                    <p style="font-size:0.85rem;color:#888;">
                        Puedes notificar al administrador para que lo tenga en cuenta.
                    </p>
                `,
                showCancelButton: true,
                confirmButtonText: '<i class="bx bx-bell"></i> Notificar al administrador',
                cancelButtonText: 'Entendido',
                confirmButtonColor: '#7f0404',
                cancelButtonColor: '#6c757d',
                reverseButtons: true,
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
                        const resp = await fetch('/usuario/carrito/notificar-stock/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrf,
                            },
                            body: JSON.stringify({
                                menu_id:      id,
                                menu_nombre:  menuNombre,
                                mensaje:      stockData.mensaje,
                            }),
                        });
                        const data = await resp.json();
                        Swal.fire({
                            icon: 'success',
                            title: '¡Notificación enviada!',
                            text: 'El administrador será informado del faltante. ¡Gracias por avisarnos! 🙏',
                            confirmButtonColor: '#7f0404',
                            timer: 3500,
                            timerProgressBar: true,
                        });
                    } catch {
                        Swal.fire({
                            icon: 'warning',
                            title: 'Sin conexión',
                            text: 'No se pudo enviar la notificación en este momento.',
                            confirmButtonColor: '#7f0404',
                        });
                    }
                }
            });

            // Marcar la tarjeta visualmente como no disponible
            marcarCardSinStock(id);
            // Bloquea el aumento retornando antes de modificar el estado
            return;
        } else {
            // Si el stock sí alcanza, asegurarse de limpiar badge previo
            limpiarCardSinStock(id);
        }
    }

    // Agregar ítem nuevo al carrito
    if (delta > 0 && actual === 0) {
        carrito[id] = {
            nombre:   nombre,
            precio:   parseFloat(precio),
            img:      img,
            cantidad: 1
        };

    // Aumentar cantidad de ítem existente
    } else if (delta > 0 && carrito[id]) {
        carrito[id].cantidad += 1;

    // Disminuir hasta 0 → eliminar
    } else if (nueva <= 0 && carrito[id]) {
        delete carrito[id];
        delete advertenciasStock[id];
        limpiarCardSinStock(id);

    // Disminuir sin llegar a 0
    } else if (carrito[id]) {
        carrito[id].cantidad = nueva;
    }

    // Actualizar cantidad en la tarjeta del producto
    const qtyEl = document.getElementById('qty-' + id);
    if (qtyEl) qtyEl.textContent = carrito[id] ? carrito[id].cantidad : 0;

    renderCarrito();
}


// ──────────────────────────────────────────────────────────
// RENDER DEL CARRITO LATERAL
// ──────────────────────────────────────────────────────────

function renderCarrito() {
    const ids     = Object.keys(carrito);
    const itemsEl = document.getElementById('carritoContenido');
    const vacioEl = document.getElementById('carritoVacio');
    const footEl  = document.getElementById('carritoFooter');
    const countEl = document.getElementById('cartCount');
    const totalEl = document.getElementById('totalPrecio');

    if (ids.length === 0) {
        itemsEl.innerHTML     = '';
        itemsEl.style.display = 'none';
        vacioEl.style.display = '';
        footEl.style.display  = 'none';
        countEl.textContent   = '0';
        return;
    }

    vacioEl.style.display = 'none';
    itemsEl.style.display = '';
    footEl.style.display  = '';

    let html       = '';
    let total      = 0;
    let totalItems = 0;

    ids.forEach(function(id) {
        const it          = carrito[id];
        const sub         = it.precio * it.cantidad;
        const tieneAdvert = !!advertenciasStock[id];
        total      += sub;
        totalItems += it.cantidad;

        html += `
        <div class="carrito-item${tieneAdvert ? ' item-advertencia' : ''}" id="item-${id}">
            <img class="carrito-item-img"
                 src="${it.img}"
                 alt="${it.nombre}"
                 onerror="this.src='/static/img/menu-default.jpg'">
            <div class="carrito-item-info">
                <div class="carrito-item-nombre">${it.nombre}</div>
                ${tieneAdvert ? `
                <span class="badge-stock-bajo" title="${advertenciasStock[id]}">
                    <i class='bx bx-error-circle'></i> Stock bajo
                </span>` : ''}
                <div class="carrito-item-precio">$${formatNum(it.precio)} / unidad</div>
                <div class="carrito-item-controles">
                    <button class="btn-cantidad eliminar"
                            onclick="cambiarCantidad(${id}, -1)"
                            title="Quitar uno">−</button>
                    <span class="cantidad-display">${it.cantidad}</span>
                    <button class="btn-cantidad"
                            onclick="cambiarCantidad(${id}, 1, '${escaparJS(it.nombre)}', ${it.precio}, '${escaparJS(it.img)}')"
                            title="Agregar uno">+</button>
                </div>
            </div>
            <div class="item-subtotal">$${formatNum(sub)}</div>
        </div>`;
    });

    itemsEl.innerHTML   = html;
    countEl.textContent = totalItems;
    totalEl.textContent = '$' + formatNum(total);
}


// ──────────────────────────────────────────────────────────
// FILTROS POR TIPO DE MENÚ
// ──────────────────────────────────────────────────────────

function filtrar(btn, tipo) {
    document.querySelectorAll('.filtro-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    document.querySelectorAll('.categoria-menu').forEach(function(bloque) {
        bloque.style.display = (tipo === 'todos' || bloque.dataset.tipo === String(tipo)) ? '' : 'none';
    });
}


// ──────────────────────────────────────────────────────────
// CONFIRMAR PEDIDO
// ──────────────────────────────────────────────────────────

function abrirModalConfirmar() {
    const ids = Object.keys(carrito);

    if (ids.length === 0) {
        alert('Agrega al menos un menú antes de confirmar.');
        return;
    }

    let html  = '';
    let total = 0;

    ids.forEach(function(id) {
        const it  = carrito[id];
        const sub = it.precio * it.cantidad;
        total += sub;

        html += `
        <div class="modal-fila">
            <span>${it.nombre} × ${it.cantidad}</span>
            <span>$${formatNum(sub)}</span>
        </div>`;
    });

    html += `
    <div class="modal-fila total">
        <span>Total</span>
        <span>$${formatNum(total)}</span>
    </div>`;

    document.getElementById('modalResumen').innerHTML = html;
    document.getElementById('modalConfirmar').classList.add('show');
}


// ──────────────────────────────────────────────────────────
// MODAL: CANCELAR PEDIDO
// ──────────────────────────────────────────────────────────

function abrirModalCancelar() {
    document.getElementById('modalCancelar').classList.add('show');
}

function cerrarModalCancelar() {
    document.getElementById('modalCancelar').classList.remove('show');
}


// ──────────────────────────────────────────────────────────
// CERRAR MODALES (genérico — soporta 'show' y 'activo')
// ──────────────────────────────────────────────────────────

function cerrarModal(idModal) {
    const el = document.getElementById(idModal);
    if (el) {
        el.classList.remove('show');
        el.classList.remove('activo');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.modal-overlay').forEach(function(overlay) {
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                overlay.classList.remove('show');
                overlay.classList.remove('activo');
            }
        });
    });
});


// ──────────────────────────────────────────────────────────
// ENVIAR PEDIDO (POST al servidor)
// ──────────────────────────────────────────────────────────

function enviarPedido() {
    const ids = Object.keys(carrito);

    if (ids.length === 0) {
        cerrarModal('modalConfirmar');
        return;
    }

    const form     = document.getElementById('formPedido');
    const camposEl = document.getElementById('camposItems');
    camposEl.innerHTML = '';

    ids.forEach(function(id, i) {
        const it = carrito[id];

        [
            ['menu_id_'  + i, id],
            ['cantidad_' + i, it.cantidad],
            ['precio_'   + i, it.precio],
        ].forEach(function([nombre, valor]) {
            const inp = document.createElement('input');
            inp.type  = 'hidden';
            inp.name  = nombre;
            inp.value = valor;
            camposEl.appendChild(inp);
        });
    });

    let total = 0;
    ids.forEach(id => { total += carrito[id].precio * carrito[id].cantidad; });

    const inpTotal = document.createElement('input');
    inpTotal.type  = 'hidden';
    inpTotal.name  = 'total';
    inpTotal.value = total;
    camposEl.appendChild(inpTotal);

    const inpNum = document.createElement('input');
    inpNum.type  = 'hidden';
    inpNum.name  = 'num_items';
    inpNum.value = ids.length;
    camposEl.appendChild(inpNum);

    form.submit();
}


// ──────────────────────────────────────────────────────────
// USER MENU DROPDOWN
// ──────────────────────────────────────────────────────────

function toggleUserMenu() {
    document.getElementById('userDropdown').classList.toggle('show');
}

document.addEventListener('click', function(e) {
    const container = document.querySelector('.user-profile-container');
    if (container && !container.contains(e.target)) {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) {
            dropdown.classList.remove('show');
            dropdown.classList.remove('activo');
        }
    }
});


// ──────────────────────────────────────────────────────────
// UTILIDADES
// ──────────────────────────────────────────────────────────

function formatNum(n) {
    return Math.round(n).toLocaleString('es-CO');
}

function escaparJS(str) {
    return String(str).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
}