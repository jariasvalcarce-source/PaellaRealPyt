document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.form');
    const inputFecha = document.getElementById('fecha-factura');
    const hoy = new Date().toISOString().split('T')[0];
    if (inputFecha) inputFecha.max = hoy;

    if (form) {
        form.addEventListener('submit', (e) => {
            if (!form.checkValidity() || (inputFecha && inputFecha.value > hoy)) {
                e.preventDefault();
                alert("Revisa los campos: hay errores o la fecha es mayor a hoy.");
            } else {
                // Si todo es válido, abrir la página de facturas
                window.open('Index_factura.html');
            }
        });
    }
});


