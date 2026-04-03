// ===============================
// Mostrar fecha actual
// ===============================
const fechaActual = document.getElementById('fecha-actual');

const opciones = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
};

const fecha = new Date().toLocaleDateString('es-ES', opciones);

fechaActual.textContent = fecha.charAt(0).toUpperCase() + fecha.slice(1);