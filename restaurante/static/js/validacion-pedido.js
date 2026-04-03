document.addEventListener('DOMContentLoaded', () => {

    // ===========================
    // Mostrar formulario según tipo de pedido
    // ===========================
    const tipoPedido = document.getElementById("tipo_pedido");
    const formularioDomicilio = document.getElementById("formulario_domicilio");
    const formularioEvento = document.getElementById("formulario_evento");

    if (tipoPedido) {
        tipoPedido.addEventListener('change', () => {
            const tipo = tipoPedido.value;
            formularioDomicilio.style.display = tipo === "Domicilio" ? "block" : "none";
            formularioEvento.style.display = tipo === "Evento" ? "block" : "none";
        });
    }

    // ===========================
    // Validaciones de fechas
    // ===========================
    const hoy = new Date().toISOString().split('T')[0]; // Fecha actual YYYY-MM-DD

    const fechaPedido = document.getElementById('fecha-pedido');
    const fechaDomicilio = document.getElementById('fecha-domicilio');
    const fechaEvento = document.getElementById('fecha-evento');

    if (fechaPedido) fechaPedido.max = hoy;
    if (fechaDomicilio) fechaDomicilio.max = hoy;
    if (fechaEvento) fechaEvento.min = hoy;

});
