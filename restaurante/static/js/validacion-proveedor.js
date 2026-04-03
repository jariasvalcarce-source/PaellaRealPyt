window.abrirModalProveedor = function(id, nom, apellido, fecha, tel, correo, direc) {
    document.getElementById('modal-prov-nom').value = nom;
    document.getElementById('modal-prov-apellido').value = apellido;
    document.getElementById('modal-prov-fecha').value = fecha;
    document.getElementById('modal-prov-tel').value = tel;
    document.getElementById('modal-prov-correo').value = correo;
    document.getElementById('modal-prov-direc').value = direc;

    document.getElementById('form-editar-proveedor').action =
        `/admin-panel/proveedores/${id}/editar/`;

    document.getElementById('modal-overlay-proveedor').classList.add('activo');
    document.body.style.overflow = 'hidden';
};

window.cerrarModalProveedor = function() {
    document.getElementById('modal-overlay-proveedor').classList.remove('activo');
    document.body.style.overflow = '';
};

window.cerrarModalProveedorOverlay = function(e) {
    if (e.target === document.getElementById('modal-overlay-proveedor')) {
        window.cerrarModalProveedor();
    }
};

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.cerrarModalProveedor();
});

// Delegación: abrir modal desde data-* attributes
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn-abrir-modal-proveedor');
    if (!btn) return;
    window.abrirModalProveedor(
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
        const mensajeFecha = document.getElementById('mensaje');

        if (fechaNacimiento) {
            const hoy = new Date().toISOString().split('T')[0];
            fechaNacimiento.setAttribute('max', hoy);

            fechaNacimiento.addEventListener('change', () => {
                if (!fechaNacimiento.value) {
                    mensajeFecha.textContent = '';
                    return;
                }

                const seleccionada = new Date(fechaNacimiento.value);
                const hoyDate = new Date(hoy);

                if (seleccionada > hoyDate) {
                    mensajeFecha.textContent = 'La fecha no puede ser futura.';
                    mensajeFecha.style.color = '#c0392b';
                    fechaNacimiento.value = '';
                    return;
                }

                let edad = hoyDate.getFullYear() - seleccionada.getFullYear();
                const mes = hoyDate.getMonth() - seleccionada.getMonth();
                if (mes < 0 || (mes === 0 && hoyDate.getDate() < seleccionada.getDate())) {
                    edad--;
                }

                mensajeFecha.textContent = `Edad: ${edad} años`;
                mensajeFecha.style.color = '#27ae60';
            });
        }

        form.addEventListener('submit', (e) => {
            const errores = [];
            const hoy = new Date().toISOString().split('T')[0];

            if (!form.checkValidity()) {
                errores.push('Hay campos incompletos o inválidos.');
            }

            if (fechaNacimiento && !fechaNacimiento.value) {
                errores.push('La fecha de nacimiento es obligatoria.');
            } else if (fechaNacimiento && fechaNacimiento.value > hoy) {
                errores.push('La fecha de nacimiento no puede ser futura.');
            }

            if (errores.length > 0) {
                e.preventDefault();
                alert(errores.join('\n'));
            }
        });
    }

    // ══════════════════════════════════════════
    // TABLA — FILTROS Y BÚSQUEDA
    // ══════════════════════════════════════════
    const listaProveedores = document.getElementById('lista-proveedores');

    if (listaProveedores) {

        window.filtrar = (estado, btnClicado) => {
            document.querySelectorAll('.btn-filtro').forEach(btn => btn.classList.remove('active'));
            if (btnClicado) btnClicado.classList.add('active');

            document.querySelectorAll('.card').forEach(card => {
                card.style.display =
                    (estado === 'todos' || card.dataset.estado === estado) ? 'block' : 'none';
            });

            actualizarContador();
        };

        const inputBuscar = document.getElementById('buscar-proveedor');
        if (inputBuscar) {
            inputBuscar.addEventListener('input', function() {
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
            contador.textContent = `${visibles} proveedor(es) encontrado(s)`;
        }

        actualizarContador();
    }
});