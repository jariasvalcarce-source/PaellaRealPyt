// validacion-cliente.js

// ══════════════════════════════════════════
// MODAL — funciones GLOBALES
// ══════════════════════════════════════════

window.abrirModalCliente = function (id, nom, apellido, fecha, tel, correo, direc) {
    document.getElementById('modal-clien-nom').value = nom;
    document.getElementById('modal-clien-apellido').value = apellido;
    document.getElementById('modal-clien-fecha').value = fecha;
    document.getElementById('modal-clien-tel').value = tel;
    document.getElementById('modal-clien-correo').value = correo;
    document.getElementById('modal-clien-direc').value = direc;

    document.getElementById('form-editar-cliente').action =
        `/admin-panel/clientes/${id}/editar/`;

    document.getElementById('modal-overlay-cliente').classList.add('activo');
    document.body.style.overflow = 'hidden';
};

window.cerrarModalCliente = function () {
    document.getElementById('modal-overlay-cliente').classList.remove('activo');
    document.body.style.overflow = '';
};

window.cerrarModalClienteOverlay = function (e) {
    if (e.target === document.getElementById('modal-overlay-cliente')) {
        window.cerrarModalCliente();
    }
};

// Cerrar con ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.cerrarModalCliente();
});

// Delegación: abrir modal desde data-* attributes
document.addEventListener('click', function (e) {
    const btn = e.target.closest('.btn-abrir-modal-cliente');
    if (!btn) return;
    window.abrirModalCliente(
        btn.dataset.id,
        btn.dataset.nom,
        btn.dataset.apellido,
        btn.dataset.fecha,
        btn.dataset.tel,
        btn.dataset.correo,
        btn.dataset.direc
    );
});


document.addEventListener('DOMContentLoaded', () => {

    // ══════════════════════════════════════════
    // FORMULARIO DE REGISTRO
    // ══════════════════════════════════════════
    const form = document.querySelector('.form');

    if (form) {
        const fechaNacimiento = document.getElementById('fecha-nacimiento');

        if (fechaNacimiento) {
            // ── Igual que registro.html: max = hace exactamente 17 años ──
            const hoy = new Date();
            const maxDate = [
                hoy.getFullYear() - 17,
                String(hoy.getMonth() + 1).padStart(2, '0'),
                String(hoy.getDate()).padStart(2, '0')
            ].join('-');

            fechaNacimiento.max = maxDate;

            // Función para disparar la SweetAlert sin borrar los demás datos
            function validarEdadInstante(valor) {
                if (valor && valor > maxDate) {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Aviso de Edad',
                        text: 'El cliente debe tener al menos 17 años para ser registrado en La Paella Real.',
                        confirmButtonText: 'Entendido',
                        confirmButtonColor: '#d33',
                        showClass: { popup: 'animate__animated animate__shakeX' }
                    });
                    fechaNacimiento.value = ''; // ⬅ Solo limpia la fecha, los demás campos quedan intactos
                    return false;
                }
                return true;
            }

            // ── Si el usuario logra escribir una fecha inválida → Swal Inmediato ──
            fechaNacimiento.addEventListener('change', function () {
                validarEdadInstante(this.value);
            });

            // ── Submit: pide confirmación antes de guardar ────────────────
            form.addEventListener('submit', (e) => {
                e.preventDefault();

                // Doble chequeo: Si ingresan directo al botón y la fecha es inválida
                if (!validarEdadInstante(fechaNacimiento.value)) {
                    return;
                }

                // Validación nativa del navegador (campos required, pattern, etc.)
                if (!form.checkValidity()) {
                    form.reportValidity();
                    return;
                }

                // Confirmación SweetAlert2
                Swal.fire({
                    title: '¿Estás seguro?',
                    text: '¿Deseas registrar este cliente?',
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonText: 'Sí, registrar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#7f0404',
                    cancelButtonColor: '#6c757d'
                }).then((result) => {
                    if (result.isConfirmed) form.submit();
                });
            });
        }
    }

    // ══════════════════════════════════════════
    // TABLA — FILTROS Y BÚSQUEDA
    // ══════════════════════════════════════════
    const listaClientes = document.getElementById('lista-clientes');

    if (listaClientes) {

        window.filtrar = (estado, btnClicado) => {
            document.querySelectorAll('.btn-filtro').forEach(btn => btn.classList.remove('active'));
            if (btnClicado) btnClicado.classList.add('active');

            document.querySelectorAll('.card').forEach(card => {
                card.style.display =
                    (estado === 'todos' || card.dataset.estado === estado) ? 'block' : 'none';
            });

            actualizarContador();
        };

        const inputBuscar = document.getElementById('buscar-cliente');
        if (inputBuscar) {
            inputBuscar.addEventListener('input', function () {
                const texto = this.value.toLowerCase();
                document.querySelectorAll('.card').forEach(card => {
                    card.style.display =
                        card.innerText.toLowerCase().includes(texto) ? 'block' : 'none';
                });
                actualizarContador();
            });
        }

        function actualizarContador() {
            const contador = document.getElementById('contador');
            if (!contador) return;
            const visibles = document.querySelectorAll('.card:not([style*="display: none"])').length;
            contador.textContent = `${visibles} cliente(s) encontrado(s)`;
        }

        actualizarContador();
    }
});