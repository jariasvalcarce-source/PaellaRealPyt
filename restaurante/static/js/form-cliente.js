document.addEventListener('DOMContentLoaded', function () {
    // --- Lógica de SweetAlert2 para Toasts ---
    if (typeof Swal !== 'undefined') {
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 4000,
            timerProgressBar: true,
            background: '#fff',
            color: '#333',
            didOpen: (toast) => {
                toast.onmouseenter = Swal.stopTimer;
                toast.onmouseleave = Swal.resumeTimer;
            }
        });

        const msgs = document.querySelectorAll('.django-message');
        msgs.forEach(msg => {
            Toast.fire({
                icon: msg.getAttribute('data-type'),
                title: msg.innerText
            });
        });
        
        // --- Confirmación de Envío del Formulario ---
        const formCliente = document.getElementById('formCliente');
        if (formCliente) {
            formCliente.addEventListener('submit', function(e) {
                e.preventDefault();
                // Validar usando checkValidity de HTML5
                if (!this.checkValidity()) {
                    this.reportValidity();
                    return;
                }
                
                Swal.fire({
                    title: '¿Registrar Cliente?',
                    text: "Se guardarán los datos de este nuevo cliente.",
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: 'var(--primary)',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Sí, registrar',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        this.submit();
                    }
                });
            });
        }
    }
});
