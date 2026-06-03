// =========================================
// mis-pedidos.js
// =========================================

function confirmarCancelacion(pedidoId) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: '¿Cancelar pedido?',
            text: 'Por favor dinos por qué deseas cancelar el pedido #' + pedidoId,
            icon: 'warning',
            input: 'textarea',
            inputPlaceholder: 'Escribe aquí tu motivo o nota de cancelación...',
            showCancelButton: true,
            confirmButtonColor: '#d9534f',
            cancelButtonColor: '#7A5C52',
            confirmButtonText: 'Sí, cancelar',
            cancelButtonText: 'No, regresar'
        }).then((result) => {
            if (result.isConfirmed) {
                const form = document.getElementById('form-cancelar-' + pedidoId);
                let inputMotivo = document.createElement('input');
                inputMotivo.type = 'hidden';
                inputMotivo.name = 'motivo_cancelacion';
                inputMotivo.value = result.value || 'Sin motivo especificado';
                form.appendChild(inputMotivo);
                form.submit();
            }
        });
    } else {
        const motivo = prompt('Por favor dinos el motivo de la cancelación:');
        if (motivo !== null) {
            const form = document.getElementById('form-cancelar-' + pedidoId);
            let inputMotivo = document.createElement('input');
            inputMotivo.type = 'hidden';
            inputMotivo.name = 'motivo_cancelacion';
            inputMotivo.value = motivo || 'Sin motivo especificado';
            form.appendChild(inputMotivo);
            form.submit();
        }
    }
}

function confirmarEntregado(pedidoId) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: '¿Marcar como Entregado?',
            text: '¿Confirmas que has recibido tu pedido #' + pedidoId + ' de forma correcta?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#2ecc71',
            cancelButtonColor: '#7A5C52',
            confirmButtonText: 'Sí, recibido',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                document.getElementById('form-entregar-' + pedidoId)?.submit();
            }
        });
    } else {
        if (confirm('¿Confirmas que recibiste el pedido #' + pedidoId + '?')) {
            document.getElementById('form-entregar-' + pedidoId)?.submit();
        }
    }
}
