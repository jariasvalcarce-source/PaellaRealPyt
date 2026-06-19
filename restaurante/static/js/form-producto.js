function initFormProducto() {
    const btnUnidad = document.getElementById('toggle-unidad');
    const formUnidad = document.getElementById('form-unidad');
    const cancelUnidad = document.getElementById('cancel-unidad');
    const btnCategoria = document.getElementById('toggle-categoria');
    const formCategoria = document.getElementById('form-categoria');
    const cancelCategoria = document.getElementById('cancel-categoria');
    const btnVerProductos = document.getElementById('btn-ver-productos');

    if (btnUnidad && formUnidad && cancelUnidad) {
        const toggleUnidad = () => {
            const open = formUnidad.hidden === false;
            formUnidad.hidden = open;
            btnUnidad.setAttribute('aria-expanded', String(!open));
            btnUnidad.classList.toggle('active', !open);
            if (!open && formCategoria) formCategoria.hidden = true;
        };

        const closeUnidad = () => {
            formUnidad.hidden = true;
            btnUnidad.setAttribute('aria-expanded', 'false');
            btnUnidad.classList.remove('active');
        };

        btnUnidad.addEventListener('click', toggleUnidad);
        cancelUnidad.addEventListener('click', closeUnidad);
    }

    if (btnCategoria && formCategoria && cancelCategoria) {
        const toggleCategoria = () => {
            const open = formCategoria.hidden === false;
            formCategoria.hidden = open;
            btnCategoria.setAttribute('aria-expanded', String(!open));
            btnCategoria.classList.toggle('active', !open);
            if (!open && formUnidad) formUnidad.hidden = true;
        };

        const closeCategoria = () => {
            formCategoria.hidden = true;
            btnCategoria.setAttribute('aria-expanded', 'false');
            btnCategoria.classList.remove('active');
        };

        btnCategoria.addEventListener('click', toggleCategoria);
        cancelCategoria.addEventListener('click', closeCategoria);
    }

    if (btnVerProductos) {
        btnVerProductos.addEventListener('click', () => {
            window.location.href = '../inventario/tabla-productos.html';
        });
    }

    const form = document.getElementById('formProducto');
    if (!form) return;

    const fieldMessages = {
        nom_produ: document.getElementById('msg-nom_produ'),
        stock_actual_produ: document.getElementById('msg-stock_actual_produ'),
        stock_minimo_produ: document.getElementById('msg-stock_minimo_produ'),
        precio_uni_produ: document.getElementById('msg-precio_uni_produ'),
        id_cate_produ_fk: document.getElementById('msg-id_cate_produ_fk'),
        id_uni_medi_produ_fk: document.getElementById('msg-id_uni_medi_produ_fk'),
        id_provee_produ_fk: document.getElementById('msg-id_provee_produ_fk'),
        fecha_venci_produ: document.getElementById('msg-fecha_venci_produ')
    };

    function setFieldStatus(input, isValid, message) {
        const wrap = input.closest('.input-wrap');
        if (wrap) {
            wrap.classList.remove('invalid', 'valid');
            wrap.classList.add(isValid ? 'valid' : 'invalid');
        }

        const msg = fieldMessages[input.name] || document.getElementById('msg-' + input.id);
        if (msg) {
            msg.textContent = message || '';
            msg.style.display = message ? 'block' : 'none';
        }
    }

    function clearStatus(input) {
        setFieldStatus(input, true, '');
    }

    function validateField(input) {
        const name = input.name;
        const value = input.value.trim();

        if (name === 'nom_produ') {
            if (!value) {
                setFieldStatus(input, false, 'El nombre del producto es obligatorio.');
                return false;
            }
            if (/\d/.test(value)) {
                setFieldStatus(input, false, 'El nombre no puede contener números.');
                return false;
            }
            setFieldStatus(input, true, '');
            return true;
        }

        if (name === 'stock_actual_produ' || name === 'stock_minimo_produ' || name === 'precio_uni_produ') {
            let rawValue = value;
            if (input.classList.contains('money-input')) {
                rawValue = value.replace(/\./g, '');
            }
            const numberValue = Number(rawValue);

            if (!value || Number.isNaN(numberValue) || numberValue < 0) {
                if (name === 'precio_uni_produ') {
                    setFieldStatus(input, false, 'El precio unitario es obligatorio y debe ser mayor a 0.');
                } else {
                    setFieldStatus(input, false, 'Ingrese una cantidad válida.');
                }
                return false;
            }

            if (name === 'precio_uni_produ' && numberValue <= 0) {
                setFieldStatus(input, false, 'El precio unitario debe ser mayor a 0.');
                return false;
            }
        }

        if (name === 'stock_actual_produ') {
            const stockActual = Number(value);
            const stockMinimo = Number(form.stock_minimo_produ.value);
            if (stockMinimo && stockMinimo >= stockActual) {
                setFieldStatus(input, false, 'El stock mínimo debe ser menor al stock actual.');
                return false;
            }
            setFieldStatus(input, true, '');
            return true;
        }

        if (name === 'stock_minimo_produ') {
            const stockActual = Number(form.stock_actual_produ.value);
            const stockMinimo = Number(value);
            if (!value || Number.isNaN(stockMinimo) || stockMinimo < 0) {
                setFieldStatus(input, false, 'El stock mínimo es obligatorio.');
                return false;
            }
            if (stockActual <= 0 || stockMinimo >= stockActual) {
                setFieldStatus(input, false, 'El stock mínimo debe ser menor al stock actual.');
                return false;
            }
            setFieldStatus(input, true, '');
            return true;
        }

        if (name === 'id_cate_produ_fk' || name === 'id_uni_medi_produ_fk' || name === 'id_provee_produ_fk') {
            if (!value) {
                setFieldStatus(input, false, 'Este campo es obligatorio.');
                return false;
            }
            setFieldStatus(input, true, '');
            return true;
        }

        if (name === 'fecha_venci_produ') {
            if (!value) {
                setFieldStatus(input, false, 'La fecha de vencimiento es obligatoria.');
                return false;
            }
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const selectedDate = new Date(value);
            if (selectedDate < today) {
                setFieldStatus(input, false, 'La fecha de vencimiento no puede ser anterior al día de hoy.');
                return false;
            }
            setFieldStatus(input, true, '');
            return true;
        }

        return true;
    }

    form.querySelectorAll('input, select').forEach((field) => {
        field.addEventListener('blur', () => validateField(field));
        field.addEventListener('input', () => validateField(field));
    });

    form.addEventListener('submit', (event) => {
        let valid = true;

        form.querySelectorAll('input, select').forEach((field) => {
            if (!validateField(field)) valid = false;
        });

        if (!valid) {
            event.preventDefault();
            const firstInvalid = form.querySelector('.input-wrap.invalid input, .input-wrap.invalid select');
            if (firstInvalid) firstInvalid.focus();
            return;
        }

        event.preventDefault();
        
        // Quitar los puntos de las entradas money-input antes de enviar
        form.querySelectorAll('.money-input').forEach(input => {
            input.value = input.value.replace(/\./g, '');
        });

        Swal.fire({
            title: '¿Crear producto?',
            text: "¿Estás seguro de registrar este nuevo producto en el inventario?",
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#e11d48',
            cancelButtonColor: '#9ca3af',
            confirmButtonText: 'Sí, crear',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                form.submit();
            } else {
                // Si el usuario cancela, restaurar el formato de dinero para que no se vea feo
                form.querySelectorAll('.money-input').forEach(input => {
                    input.dispatchEvent(new Event('input'));
                });
            }
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFormProducto);
} else {
    initFormProducto();
}
