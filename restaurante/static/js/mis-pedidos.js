// =========================================
// mis-pedidos.js
// =========================================

function confirmarCancelacion(pedidoId, estado) {
    let warningText = 'Por favor dinos por qué deseas cancelar el pedido #' + pedidoId;
    if (estado === 'confirmado') {
        warningText = '⚠️ ¡Atención! Tu pedido ya fue confirmado por el restaurante. Por favor dinos por qué deseas cancelarlo:';
    }

    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: '¿Cancelar pedido?',
            text: warningText,
            icon: 'warning',
            input: 'textarea',
            inputPlaceholder: 'Escribe aquí tu motivo de cancelación (obligatorio)...',
            showCancelButton: true,
            confirmButtonColor: '#d9534f',
            cancelButtonColor: '#7A5C52',
            confirmButtonText: 'Sí, cancelar',
            cancelButtonText: 'No, regresar',
            preConfirm: (value) => {
                if (!value || value.trim() === '') {
                    Swal.showValidationMessage('El motivo de cancelación es obligatorio.');
                }
                return value;
            }
        }).then((result) => {
            if (result.isConfirmed) {
                const valInput = document.getElementById('motivo-cancelar-val-' + pedidoId);
                if (valInput) {
                    valInput.value = result.value;
                }
                document.getElementById('form-cancelar-' + pedidoId).submit();
            }
        });
    } else {
        const motivo = prompt('Por favor dinos el motivo de la cancelación (obligatorio):');
        if (motivo !== null) {
            if (motivo.trim() === '') {
                alert('El motivo de cancelación es obligatorio.');
                return;
            }
            const valInput = document.getElementById('motivo-cancelar-val-' + pedidoId);
            if (valInput) {
                valInput.value = motivo;
            }
            document.getElementById('form-cancelar-' + pedidoId).submit();
        }
    }
}

function solicitarCancelacion(pedidoId) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'Solicitar Cancelación',
            text: 'Tu pedido ya lleva más de 30 minutos confirmado. Se enviará una solicitud de cancelación para aprobación del restaurante. Por favor ingresa el motivo:',
            icon: 'info',
            input: 'textarea',
            inputPlaceholder: 'Escribe aquí tu motivo de cancelación (obligatorio)...',
            showCancelButton: true,
            confirmButtonColor: '#C8973A',
            cancelButtonColor: '#7A5C52',
            confirmButtonText: 'Enviar solicitud',
            cancelButtonText: 'Cancelar',
            preConfirm: (value) => {
                if (!value || value.trim() === '') {
                    Swal.showValidationMessage('El motivo de cancelación es obligatorio.');
                }
                return value;
            }
        }).then((result) => {
            if (result.isConfirmed) {
                const valInput = document.getElementById('motivo-cancelar-val-' + pedidoId);
                if (valInput) {
                    valInput.value = result.value;
                }
                document.getElementById('form-cancelar-' + pedidoId).submit();
            }
        });
    } else {
        const motivo = prompt('Tu pedido ya lleva más de 30 minutos confirmado. Por favor ingresa el motivo para la solicitud (obligatorio):');
        if (motivo !== null) {
            if (motivo.trim() === '') {
                alert('El motivo de cancelación es obligatorio.');
                return;
            }
            const valInput = document.getElementById('motivo-cancelar-val-' + pedidoId);
            if (valInput) {
                valInput.value = motivo;
            }
            document.getElementById('form-cancelar-' + pedidoId).submit();
        }
    }
}
