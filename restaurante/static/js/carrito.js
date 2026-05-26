// =========================================
// carrito.js
// =========================================

// Estado del carrito
let carrito = {};

// Agregar / quitar cantidad
function cambiarCantidad(id, delta, nombre, precio, img) {
    if (!carrito[id] && delta > 0) {
        carrito[id] = { nombre, precio, img, cantidad: 0 };
    }
    if (!carrito[id]) return;

    carrito[id].cantidad += delta;

    if (carrito[id].cantidad <= 0) {
        delete carrito[id];
    }

    const qtyEl = document.getElementById('qty-' + id);
    if (qtyEl) qtyEl.textContent = carrito[id] ? carrito[id].cantidad : 0;

    renderCarrito();
}

// Eliminar ítem completo
function eliminarItem(id) {
    if (carrito[id]) {
        const qtyEl = document.getElementById('qty-' + id);
        if (qtyEl) qtyEl.textContent = 0;
        delete carrito[id];
        renderCarrito();
    }
}

// Renderizar el panel lateral
function renderCarrito() {
    const contenido  = document.getElementById('carritoContenido');
    const vacio      = document.getElementById('carritoVacio');
    const footer     = document.getElementById('carritoFooter');
    const countEl    = document.getElementById('cartCount');
    const totalEl    = document.getElementById('totalPrecio');
    const badgeFloat = document.getElementById('floatingCartBadge');

    const items = Object.entries(carrito);
    let total      = 0;
    let totalItems = 0;

    contenido.innerHTML = '';

    if (items.length === 0) {
        vacio.style.display     = 'flex';
        footer.style.display    = 'none';
        contenido.style.display = 'none';
    } else {
        vacio.style.display     = 'none';
        footer.style.display    = 'block';
        contenido.style.display = 'flex';

        items.forEach(([id, item]) => {
            const sub   = item.precio * item.cantidad;
            total      += sub;
            totalItems += item.cantidad;

            contenido.innerHTML += `
                <div class="carrito-item">
                    <img class="carrito-item-img"
                         src="${item.img}"
                         alt="${item.nombre}"
                         onerror="this.src='../assets/img/logo.png'">
                    <div class="carrito-item-info">
                        <div class="carrito-item-nombre">${item.nombre}</div>
                        <div class="carrito-item-precio">$${item.precio.toLocaleString('es-CO')}</div>
                        <div class="carrito-item-controles">
                            <button class="btn-cantidad"
                                onclick="cambiarCantidad(${id}, -1)">−</button>
                            <span class="cantidad-display">${item.cantidad}</span>
                            <button class="btn-cantidad"
                                onclick="cambiarCantidad(${id}, 1, '${item.nombre}', ${item.precio}, '${item.img}')">+</button>
                            <button class="btn-cantidad eliminar"
                                onclick="eliminarItem(${id})">
                                <i class='bx bx-trash'></i>
                            </button>
                        </div>
                    </div>
                    <span class="item-subtotal">$${sub.toLocaleString('es-CO')}</span>
                </div>
            `;
        });
    }

    countEl.textContent    = totalItems;
    totalEl.textContent    = '$' + total.toLocaleString('es-CO');
    badgeFloat.textContent = totalItems;
}

// Modal confirmar
function abrirModalConfirmar() {
    const items = Object.values(carrito);
    if (items.length === 0) {
        alertaCarritoVacio();
        return;
    }

    let html  = '';
    let total = 0;

    items.forEach(item => {
        const sub = item.precio * item.cantidad;
        total += sub;
        html += `
            <div class="modal-fila">
                <span>${item.nombre} x${item.cantidad}</span>
                <span>$${sub.toLocaleString('es-CO')}</span>
            </div>
        `;
    });

    html += `
        <div class="modal-fila total">
            <span>Total</span>
            <span>$${total.toLocaleString('es-CO')}</span>
        </div>
    `;

    document.getElementById('modalResumen').innerHTML = html;
    document.getElementById('modalConfirmar').classList.add('show');
}

// Modal cancelar
function abrirModalCancelar() {
    document.getElementById('modalCancelar').classList.add('show');
}

// Cerrar modal
function cerrarModal(id) {
    document.getElementById(id).classList.remove('show');
}

// Enviar pedido
function enviarPedido() {
    const items = Object.entries(carrito);
    if (items.length === 0) return;

    const form = document.getElementById('formCarrito');
    
    // num_items
    const numInput = document.createElement('input');
    numInput.type = 'hidden';
    numInput.name = 'num_items';
    numInput.value = items.length;
    form.appendChild(numInput);

    // items
    items.forEach(([id, item], index) => {
        const idInput = document.createElement('input');
        idInput.type = 'hidden';
        idInput.name = `menu_id_${index}`;
        idInput.value = id;
        form.appendChild(idInput);

        const qtyInput = document.createElement('input');
        qtyInput.type = 'hidden';
        qtyInput.name = `cantidad_${index}`;
        qtyInput.value = item.cantidad;
        form.appendChild(qtyInput);
    });

    // Enviar al backend
    form.submit();
}

// Filtros de categoría
function filtrar(btn, tipo) {
    document.querySelectorAll('.filtro-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.categoria-menu').forEach(cat => {
        cat.style.display = (tipo === 'todos' || cat.dataset.tipo === tipo)
            ? 'block'
            : 'none';
    });
}

// Dropdown usuario (función presente pero no usada en este archivo)
function toggleUserMenu() {
    document.getElementById('userDropdown').classList.toggle('show');
}

window.onclick = function(e) {
    if (!e.target.closest('.sidebar-footer')) {
        document.getElementById('userDropdown').classList.remove('show');
    }
};
