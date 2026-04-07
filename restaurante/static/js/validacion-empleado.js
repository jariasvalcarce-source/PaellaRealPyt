window.abrirModal = function(id, nom, apellido, fecha, tel, correo, direc, usuario) {
    document.getElementById('modal-nom').value = nom;
    document.getElementById('modal-apellido').value = apellido;
    document.getElementById('modal-fecha').value = fecha;
    document.getElementById('modal-tel').value = tel;
    document.getElementById('modal-correo').value = correo;
    document.getElementById('modal-direc').value = direc;
    
    // Si no tiene usuario, cambiar texto
    const inUsuario = document.getElementById('modal-usuario');
    if(usuario === 'N/A' || !usuario || usuario.trim() === '') {
        inUsuario.value = '(Sin usuario / Creado antiguo)';
        inUsuario.style.color = '#c0392b';
    } else {
        inUsuario.value = usuario;
        inUsuario.style.color = '#333';
    }

    document.getElementById('form-editar-empleado').action =
        `/admin-panel/empleados/${id}/editar/`;

    document.getElementById('modal-overlay').classList.add('activo');
    document.body.style.overflow = 'hidden';
};

window.cerrarModal = function() {
    document.getElementById('modal-overlay').classList.remove('activo');
    document.body.style.overflow = '';
};

window.cerrarModalOverlay = function(e) {
    if (e.target === document.getElementById('modal-overlay')) {
        window.cerrarModal();
    }
};

// Cerrar con ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.cerrarModal();
});

// ── Delegación: abrir modal desde data-* attributes ──
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn-abrir-modal');
    if (!btn) return;
    window.abrirModal(
        btn.dataset.id,
        btn.dataset.nom,
        btn.dataset.apellido,
        btn.dataset.fecha,
        btn.dataset.tel,
        btn.dataset.correo,
        btn.dataset.direc,
        btn.dataset.usuario
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
                    mensajeFecha.style.color = 'gray';
                    return;
                }

                const seleccionada = new Date(fechaNacimiento.value);
                const hoyDate = new Date(hoy);

                if (seleccionada > hoyDate) {
                    mensajeFecha.textContent = 'La fecha de nacimiento no puede ser futura.';
                    mensajeFecha.style.color = '#c0392b';
                    fechaNacimiento.value = '';
                    return;
                }

                let edad = hoyDate.getFullYear() - seleccionada.getFullYear();
                const mes = hoyDate.getMonth() - seleccionada.getMonth();
                if (mes < 0 || (mes === 0 && hoyDate.getDate() < seleccionada.getDate())) {
                    edad--;
                }

                if (edad < 18) {
                    mensajeFecha.textContent = 'El empleado debe tener al menos 18 años.';
                    mensajeFecha.style.color = '#c0392b';
                    fechaNacimiento.value = '';
                } else {
                    mensajeFecha.textContent = `Edad: ${edad} años`;
                    mensajeFecha.style.color = '#27ae60';
                }
            });
        }

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const hoy = new Date().toISOString().split('T')[0];

            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            if (fechaNacimiento) {
                if (!fechaNacimiento.value) {
                    Swal.fire({icon: 'error', title: 'Error', text: 'La fecha de nacimiento es obligatoria.', confirmButtonColor: '#d33'});
                    return;
                } else if (fechaNacimiento.value > hoy) {
                    Swal.fire({icon: 'error', title: 'Error', text: 'La fecha de nacimiento no puede ser futura.', confirmButtonColor: '#d33'});
                    return;
                }
            }

            Swal.fire({
                title: '¿Estás seguro?',
                text: '¿Deseas registrar este empleado?',
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

    // ══════════════════════════════════════════
    // TABLA — FILTROS Y BÚSQUEDA
    // ══════════════════════════════════════════
    const listaEmpleados = document.getElementById('lista-empleados');

    if (listaEmpleados) {

        window.filtrar = (estado, btnClicado) => {
            document.querySelectorAll('.btn-filtro').forEach(btn => btn.classList.remove('active'));
            if (btnClicado) btnClicado.classList.add('active');

            document.querySelectorAll('.card').forEach(card => {
                card.style.display =
                    (estado === 'todos' || card.dataset.estado === estado) ? 'block' : 'none';
            });

            actualizarContador();
        };

        const inputBuscar = document.getElementById('buscar-empleado');
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
            contador.textContent = `${visibles} empleado(s) encontrado(s)`;
        }

        actualizarContador();
    }
});