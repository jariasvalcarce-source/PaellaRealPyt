document.addEventListener('DOMContentLoaded', () => {
    const botonesEditar = document.querySelectorAll('.editar');
    const botonesEliminar = document.querySelectorAll('.eliminar');

    botonesEditar.forEach(boton => {
        boton.addEventListener('click', () => {
            alert('Función Editar aún no implementada');
        });
    });

    botonesEliminar.forEach(boton => {
        boton.addEventListener('click', () => {
            const confirmacion = confirm('¿Está seguro que desea eliminar esta venta?');
            if(confirmacion){
                boton.closest('.card').remove();
            }
        });
    });
});
