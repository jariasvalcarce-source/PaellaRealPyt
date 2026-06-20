// =========================================
// Todas las funciones de alertas
// =========================================

// Alertas -> Carrito
function alertaCarritoVacio() {
    return Swal.fire({
        icon: 'warning',
        title: 'Carrito vacío',
        text: 'Agrega al menos un producto.'
    });
}

function alertaPedidoConfirmado() {
    return Swal.fire({
        icon: 'success',
        title: '¡Pedido confirmado!',
        text: 'El restaurante ha recibido tu pedido.'
    });
}

// Alertas -> Mis pedidos
function alertaConfirmarCancelacion(pedidoId) {
    return Swal.fire({
        icon: 'warning',
        title: '¿Cancelar pedido?',
        text: 'Esta acción no se puede deshacer. ¿Estás seguro de cancelar el pedido #' + pedidoId + '?',
        showCancelButton: true,
        confirmButtonText: 'Sí, cancelar',
        cancelButtonText: 'No, mantener',
        confirmButtonColor: '#e74c3c',
        cancelButtonColor: '#7f0404',
        reverseButtons: true
    });
}

function alertaPedidoCancelado(pedidoId) {
    return Swal.fire({
        icon: 'success',
        title: 'Pedido cancelado',
        text: 'El pedido #' + pedidoId + ' ha sido cancelado.',
        confirmButtonColor: '#7f0404'
    });
}

function alertaConfirmarEntregado(pedidoId) {
    return Swal.fire({
        icon: 'question',
        title: '¿Confirmar entrega?',
        text: '¿Ya recibiste tu pedido #' + pedidoId + '?',
        showCancelButton: true,
        confirmButtonText: 'Sí, ya lo recibí',
        cancelButtonText: 'Aún no',
        confirmButtonColor: '#27ae60',
        cancelButtonColor: '#7f0404',
        reverseButtons: true
    });
}

function alertaPedidoEntregado(pedidoId) {
    return Swal.fire({
        icon: 'success',
        title: '¡Gracias!',
        text: 'Pedido #' + pedidoId + ' marcado como entregado.',
        confirmButtonColor: '#27ae60'
    });
}

// Alertas -> Pedido
function alertaCamposIncompletosDomicilio() {
    return Swal.fire({
        icon: 'warning',
        title: 'Campos incompletos',
        text: 'Por favor completa todos los campos del domicilio.',
        confirmButtonColor: 'var(--rojo)'
    });
}

function alertaCamposIncompletosEvento() {
    return Swal.fire({
        icon: 'warning',
        title: 'Campos incompletos',
        text: 'Por favor completa todos los campos del evento.',
        confirmButtonColor: 'var(--rojo)'
    });
}

// Alertas -> Favoritos, carta
function alertaFavoritoAgregado() {
    return Swal.fire({
        icon: 'success',
        title: '¡Agregado a favoritos! ❤️',
        showConfirmButton: false,
        timer: 1500,
        timerProgressBar: true
    });
}

function alertaFavoritoEliminado() {
    return Swal.fire({
        icon: 'info',
        title: 'Eliminado de favoritos',
        showConfirmButton: false,
        timer: 1500,
        timerProgressBar: true
    });
}

function alertaNoFavoritosGuardados() {
    return Swal.fire({
        icon: 'info',
        title: 'No tienes favoritos guardados',
        showConfirmButton: false,
        timer: 1800,
        timerProgressBar: true
    });
}

function alertaFavoritosLimpiados() {
    return Swal.fire({
        icon: 'success',
        title: 'Lista de favoritos limpiada',
        showConfirmButton: false,
        timer: 1800,
        timerProgressBar: true
    });
}

function alertaTodoAlDia() {
    return Swal.fire({
        icon: 'info',
        title: 'Todo al día',
        text: 'Ya has leído todas tus notificaciones.',
        confirmButtonColor: '#6B1A2B',
        timer: 2000,
        showConfirmButton: false
    });
}

function alertaNotificacionesLeidas() {
    return Swal.fire({
        icon: 'success',
        title: '¡Listo!',
        text: 'Todas las notificaciones marcadas como leídas.',
        confirmButtonColor: '#6B1A2B',
        timer: 2000,
        showConfirmButton: false
    });
}

// Alertas -> Pago y factura
function alertaSeleccionaMetodo() {
    return Swal.fire({
        icon: 'warning',
        title: 'Selecciona un método',
        text: 'Por favor elige un método de pago para continuar.',
        confirmButtonColor: 'var(--rojo)'
    });
}

function alertaReferenciaRequerida() {
    return Swal.fire({
        icon: 'warning',
        title: 'Referencia requerida',
        text: 'Por favor ingresa el número de referencia de tu transferencia.',
        confirmButtonColor: 'var(--rojo)'
    });
}

function alertaRedirigiendoStripe() {
    return Swal.fire({
        icon: 'info',
        title: 'Redirigiendo...',
        text: 'Serás redirigido a Stripe para completar el pago.',
        confirmButtonColor: 'var(--rojo)'
    });
}
