// =========================================
// carrito.js
// =========================================

const CARRITO_STORAGE_KEY = window.PAELLA_CARRITO_KEY || 'miCarritoPaella';

// Estado del carrito
let carrito = JSON.parse(localStorage.getItem(CARRITO_STORAGE_KEY) || '{}');

// Al cargar, si hay items, renderizarlos
document.addEventListener('DOMContentLoaded', () => {
    if (Object.keys(carrito).length > 0) {
        renderCarrito();
    }
});

function alertarFaltaStockJS(menuId, menuNom) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'No Disponible',
            text: `Actualmente no se puede escoger "${menuNom}" por falta de ingredientes.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Ok',
            cancelButtonText: 'Alertar a empleados',
            reverseButtons: true
        }).then((result) => {
            if (result.dismiss === Swal.DismissReason.cancel) {
                fetch(`/usuario/alertar-stock/${menuId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : ''
                    }
                }).then(res => res.json()).then(data => {
                    if(data.success) {
                        Swal.fire('Notificado', 'Se ha alertado al personal sobre la falta de ingredientes.', 'success');
                    }
                }).catch(() => {});
            }
        });
    } else {
        alert(`Actualmente no se puede escoger "${menuNom}" por falta de ingredientes.`);
    }
}

// Agregar / quitar cantidad
async function cambiarCantidad(id, delta, nombre, precio, img) {
    if (delta < 0) {
        if (!carrito[id]) return;
        carrito[id].cantidad += delta;
        if (carrito[id].cantidad <= 0) {
            delete carrito[id];
        }
        
        const qtyEl = document.getElementById('qty-' + id);
        if (qtyEl) qtyEl.textContent = carrito[id] ? carrito[id].cantidad : 0;
        localStorage.setItem(CARRITO_STORAGE_KEY, JSON.stringify(carrito));
        renderCarrito();
        return;
    }

    // Preparar carrito temporal con el incremento
    const tempCart = JSON.parse(JSON.stringify(carrito));
    if (!tempCart[id]) {
        tempCart[id] = { nombre, precio, img, cantidad: 0 };
    }
    tempCart[id].cantidad += delta;

    // Convertir el formato al esperado por el backend [{menu_id: ..., cantidad: ...}]
    const itemsParaValidar = Object.entries(tempCart).map(([menuId, item]) => ({
        menu_id: menuId,
        cantidad: item.cantidad
    }));

    // Validar en vivo
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';
        const res = await fetch('/usuario/carrito/verificar-completo/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ items: itemsParaValidar })
        });
        const data = await res.json();
        
        if (!data.es_valido) {
            // Mostrar SweetAlert si no hay stock
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: 'Plato no disponible',
                    text: data.mensaje_error,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Entendido',
                    cancelButtonText: 'Avisar al restaurante',
                    reverseButtons: true
                }).then((result) => {
                    if (result.dismiss === Swal.DismissReason.cancel) {
                        fetch('/usuario/carrito/notificar-stock/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrfToken
                            },
                            body: JSON.stringify({
                                menu_nombre: nombre,
                                mensaje: data.mensaje_error
                            })
                        }).then(r => r.json()).then(d => {
                            if(d.ok) Swal.fire('Notificado', 'Notificación enviada al restaurante', 'success');
                        }).catch(() => {});
                    }
                });
            } else {
                alert(data.mensaje_error);
            }
            return; // Detener sin agregar al carrito real
        }
    } catch (e) {
        console.error("Error al validar stock:", e);
    }

    // Si hay stock, confirmar los cambios
    carrito = tempCart;
    const qtyEl = document.getElementById('qty-' + id);
    if (qtyEl) qtyEl.textContent = carrito[id] ? carrito[id].cantidad : 0;
    
    localStorage.setItem(CARRITO_STORAGE_KEY, JSON.stringify(carrito));
    renderCarrito();
}

// Eliminar ítem completo
function eliminarItem(id) {
    if (carrito[id]) {
        const qtyEl = document.getElementById('qty-' + id);
        if (qtyEl) qtyEl.textContent = 0;
        delete carrito[id];
        localStorage.setItem(CARRITO_STORAGE_KEY, JSON.stringify(carrito));
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

    if (contenido) contenido.innerHTML = '';

    if (items.length === 0) {
        if (vacio) vacio.style.display     = 'flex';
        if (footer) footer.style.display    = 'none';
        if (contenido) contenido.style.display = 'none';
    } else {
        if (vacio) vacio.style.display     = 'none';
        if (footer) footer.style.display    = 'block';
        if (contenido) contenido.style.display = 'flex';

        let hayAgotados = false;

        items.forEach(([id, item]) => {
            const sub   = item.precio * item.cantidad;
            total      += sub;
            totalItems += item.cantidad;

            const isAgotado = window.AGOTADOS_IDS && window.AGOTADOS_IDS.includes(parseInt(id));
            if (isAgotado) hayAgotados = true;

            if (contenido) {
                contenido.innerHTML += `
                    <div class="carrito-item ${isAgotado ? 'agotado-item' : ''}" ${isAgotado ? 'style="opacity: 0.6;"' : ''}>
                        <img class="carrito-item-img"
                             src="${item.img}"
                             alt="${item.nombre}"
                             onerror="this.src='../assets/img/logo.png'"
                             ${isAgotado ? 'style="filter: grayscale(100%);"' : ''}>
                        <div class="carrito-item-info">
                            <div class="carrito-item-nombre" ${isAgotado ? 'style="text-decoration: line-through;"' : ''}>${item.nombre}</div>
                            ${isAgotado ? '<div style="color: red; font-size: 0.8rem; font-weight: bold;">Ya no disponible</div>' : ''}
                            <div class="carrito-item-precio">$${item.precio.toLocaleString('es-CO')}</div>
                            <div class="carrito-item-controles">
                                <button class="btn-cantidad"
                                    onclick="cambiarCantidad(${id}, -1)">−</button>
                                <span class="cantidad-display">${item.cantidad}</span>
                                ${isAgotado ? 
                                `<button class="btn-cantidad" style="background-color: #f3f4f6; color: #9ca3af; cursor: not-allowed;"
                                    onclick="alertarFaltaStockJS(${id}, '${item.nombre}')">+</button>` :
                                `<button class="btn-cantidad"
                                    onclick="cambiarCantidad(${id}, 1, '${item.nombre}', ${item.precio}, '${item.img}')">+</button>`
                                }
                                <button class="btn-cantidad eliminar"
                                    onclick="eliminarItem(${id})">
                                    <i class='bx bx-trash'></i>
                                </button>
                            </div>
                        </div>
                        <span class="item-subtotal">$${sub.toLocaleString('es-CO')}</span>
                    </div>
                `;
            }
        });
        
        const btnProcesar = document.querySelector('.btn-procesar-pedido');
        if (btnProcesar) {
            if (hayAgotados) {
                btnProcesar.disabled = true;
                btnProcesar.style.backgroundColor = '#9CA3AF';
                btnProcesar.style.cursor = 'not-allowed';
                btnProcesar.innerHTML = "<i class='bx bx-error'></i> Retira platos agotados";
            } else {
                btnProcesar.disabled = false;
                btnProcesar.style.backgroundColor = '';
                btnProcesar.style.cursor = '';
                btnProcesar.innerHTML = "<i class='bx bx-check-circle'></i> Procesar Pedido";
            }
        }
    }

    if (countEl) countEl.textContent    = totalItems;
    if (totalEl) totalEl.textContent    = '$' + total.toLocaleString('es-CO');
    if (badgeFloat) badgeFloat.textContent = totalItems;
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

// Vaciar carrito por completo (cuando le dan "Sí, cancelar")
function vaciarCarrito(urlSalida) {
    carrito = {};
    localStorage.removeItem(CARRITO_STORAGE_KEY);
    window.location.href = urlSalida;
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
