document.addEventListener('DOMContentLoaded', () => {
    const moneyInputs = document.querySelectorAll('.money-input');

    function formatNumber(value) {
        if (!value) return '';
        // Remover cualquier cosa que no sea número
        let num = value.replace(/\D/g, '');
        if (!num) return '';
        // Quitar ceros a la izquierda
        num = parseInt(num, 10).toString();
        // Agregar puntos separadores de miles
        return num.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }

    moneyInputs.forEach(input => {
        // Formatear valor inicial si ya hay uno cargado (ej. al editar)
        if (input.value) {
            // Si el backend mandó 1000.00 (con decimales), quitamos los decimales
            let initialVal = input.value.split('.')[0];
            input.value = formatNumber(initialVal);
        }

        input.addEventListener('input', (e) => {
            // Guardar posición del cursor para evitar saltos molestos
            const cursorPosition = e.target.selectionStart;
            const originalLength = e.target.value.length;
            
            e.target.value = formatNumber(e.target.value);
            
            // Ajustar posición del cursor
            const newLength = e.target.value.length;
            let newPosition = cursorPosition + (newLength - originalLength);
            // Asegurarse de que el cursor no se vaya antes de tiempo si borramos un punto
            if (newPosition < 0) newPosition = 0;
            e.target.setSelectionRange(newPosition, newPosition);
        });
        
        // Prevenir ingresar "0" como primer dígito
        input.addEventListener('keypress', (e) => {
            if (e.target.value.length === 0 && e.key === '0') {
                e.preventDefault();
            }
        });
        
        // Al perder el foco, validar que no quede vacío si es requerido
        input.addEventListener('blur', (e) => {
            if (e.target.hasAttribute('required') && !e.target.value) {
                // Se puede mostrar mensaje de error o dejar que HTML5 actúe
            }
        });
    });

    // Formatear textos estáticos en tablas o vistas de detalle
    document.querySelectorAll('.money-text').forEach(el => {
        const rawText = el.textContent.trim();
        // Solo aplicar si hay algo y parece un número
        if (rawText && !isNaN(rawText.replace(/\D/g, ''))) {
            // Si tiene prefijo como $ o COP, se mantiene
            const numericPart = rawText.replace(/[^\d.-]/g, '');
            if (numericPart) {
                // Eliminar decimales si los tiene y parsear
                const intPart = numericPart.split('.')[0];
                const formatted = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
                // Intentar mantener el formato original (ej. $ 1000 -> $ 1.000)
                el.textContent = rawText.replace(numericPart, formatted);
            }
        }
    });

    // Antes de hacer el submit del formulario, le quitamos los puntos para que Django guarde un número real
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            const formMoneyInputs = form.querySelectorAll('.money-input');
            formMoneyInputs.forEach(input => {
                input.value = input.value.replace(/\./g, '');
            });
        });
    });
});
