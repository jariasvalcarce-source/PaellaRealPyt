// =========================================
// mis-pedidos.js
// =========================================

function confirmarCancelacion(pedidoId) {
    alertaConfirmarCancelacion(pedidoId)
        .then(function(result) {
            if (result.isConfirmed) {
                alertaPedidoCancelado(pedidoId);
            }
        });
}

function confirmarEntregado(pedidoId) {
    alertaConfirmarEntregado(pedidoId)
        .then(function(result) {
            if (result.isConfirmed) {
                alertaPedidoEntregado(pedidoId);
            }
        });
}
