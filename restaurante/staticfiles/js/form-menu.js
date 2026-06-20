document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // 1. VALIDACIÓN NOMBRE MENÚ
    // ==========================================
    const validateName = (input, msgId) => {
        if (!input) return;
        const msg = document.getElementById(msgId);
        input.addEventListener('input', (e) => {
            let val = e.target.value;
            // Remover números al inicio
            if (/^[0-9]/.test(val)) {
                val = val.replace(/^[0-9]+/, '');
                e.target.value = val;
            }
            // Solo letras, números, espacios, (),-
            val = val.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s(),\-]/g, '');
            if (e.target.value !== val) e.target.value = val;
            
            if (msg) {
                if (val.length > 0 && val.length < 3) {
                    msg.textContent = 'Mínimo 3 caracteres';
                    msg.style.color = '#e74c3c';
                } else if (val.length > 100) {
                    msg.textContent = 'Máximo 100 caracteres';
                    msg.style.color = '#e74c3c';
                } else {
                    msg.textContent = '';
                }
            }
        });
    };
    validateName(document.getElementById('nom_menu'), 'msg-nom');
    validateName(document.getElementById('edit-nom'), 'msg-edit-nom');

    // PRECIO FORMATEADO manejado globalmente por money-formatter.js

    // ==========================================
    // 3. DESCRIPCIÓN CONTADOR Y LÍMITES
    // ==========================================
    const initDescCounter = (textareaId, msgId) => {
        const ta = document.getElementById(textareaId);
        if (!ta) return;
        
        const counter = document.createElement('div');
        counter.style.fontSize = '0.8rem';
        counter.style.color = '#6b7280';
        counter.style.textAlign = 'right';
        counter.style.marginTop = '4px';
        ta.parentNode.insertBefore(counter, ta.nextSibling);

        const updateCounter = () => {
            const len = ta.value.length;
            counter.textContent = `${len}/300 caracteres`;
            if (len < 20) {
                counter.style.color = '#e74c3c';
            } else {
                counter.style.color = '#6b7280';
            }
        };
        
        ta.addEventListener('input', updateCounter);
        updateCounter();

        const form = ta.closest('form');
        if (form) {
            form.addEventListener('submit', (e) => {
                if (ta.value.length < 20) {
                    e.preventDefault();
                    Swal.fire({ icon: 'error', title: 'Descripción corta', text: 'La descripción debe tener al menos 20 caracteres.' });
                }
            });
        }
    };
    initDescCounter('des_menu', 'msg-des');
    initDescCounter('edit-des', 'msg-edit-des');

    // ==========================================
    // 4. IMAGEN PREVIEW Y VALIDACIÓN
    // ==========================================
    const initImagePreview = (inputId) => {
        const input = document.getElementById(inputId) || document.querySelector(`input[name="img_menu"]`);
        if (!input) return;

        const container = input.closest('.input-wrap') || input.parentElement;
        const previewImg = document.createElement('img');
        previewImg.style.display = 'none';
        previewImg.style.width = '100px';
        previewImg.style.height = '100px';
        previewImg.style.objectFit = 'cover';
        previewImg.style.borderRadius = '8px';
        previewImg.style.marginTop = '10px';
        container.appendChild(previewImg);

        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                // Validate size (2MB)
                if (file.size > 2 * 1024 * 1024) {
                    Swal.fire({ icon: 'error', title: 'Archivo muy grande', text: 'La imagen no debe superar los 2MB.' });
                    this.value = '';
                    previewImg.style.display = 'none';
                    return;
                }
                // Validate format
                const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
                if (!validTypes.includes(file.type)) {
                    Swal.fire({ icon: 'error', title: 'Formato inválido', text: 'Solo se permiten JPG, PNG o WEBP.' });
                    this.value = '';
                    previewImg.style.display = 'none';
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImg.src = e.target.result;
                    previewImg.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                previewImg.style.display = 'none';
            }
        });
    };
    initImagePreview('img_menu');
    const editImgInput = document.querySelector('#edit-img-wrap input[type="file"]');
    if (editImgInput) {
        editImgInput.id = 'edit_img_menu';
        initImagePreview('edit_img_menu');
    }

    // ==========================================
    // 5. NUEVO TIPO DE MENÚ (MODAL INLINE)
    // ==========================================
    const btnTipo = document.getElementById('toggle-tipo');
    const formTipo = document.getElementById('form-tipo');
    const cancelTipo = document.getElementById('cancel-tipo');
    
    // Desc counter para nuevo tipo desc
    const descTipo = document.getElementById('nuevo_tipo_desc');
    if (descTipo) {
        const descTipoCounter = document.createElement('div');
        descTipoCounter.style.fontSize = '0.75rem';
        descTipoCounter.style.color = '#6b7280';
        descTipoCounter.style.textAlign = 'right';
        descTipo.parentNode.insertBefore(descTipoCounter, descTipo.nextSibling);
        descTipo.addEventListener('input', () => {
            descTipoCounter.textContent = `${descTipo.value.length}/150`;
        });
    }

    const nomTipo = document.getElementById('nuevo_tipo_nombre');
    if (nomTipo) {
        nomTipo.addEventListener('input', (e) => {
            let val = e.target.value;
            val = val.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/g, ''); // Solo letras y espacios
            if (val.length > 0) val = val.charAt(0).toUpperCase() + val.slice(1);
            if (e.target.value !== val) e.target.value = val;
        });
    }

    if (btnTipo && formTipo) {
        btnTipo.addEventListener('click', () => {
            const open = formTipo.hidden === false;
            formTipo.hidden = open;
            btnTipo.setAttribute('aria-expanded', !open);
            btnTipo.classList.toggle('active', !open);
        });
    }

    if (cancelTipo && formTipo && btnTipo) {
        cancelTipo.addEventListener('click', () => {
            formTipo.hidden = true;
            btnTipo.setAttribute('aria-expanded', false);
            btnTipo.classList.remove('active');
        });
    }

    const saveTipoBtn = document.getElementById('save-tipo');
    if (saveTipoBtn) {
        saveTipoBtn.addEventListener('click', () => {
            const nom = document.getElementById('nuevo_tipo_nombre').value.trim();
            const des = document.getElementById('nuevo_tipo_desc').value.trim();
            if (!nom || nom.length < 3) {
                Swal.fire({ icon: 'warning', title: 'Nombre obligatorio (min 3)', showConfirmButton: false, timer: 3000 });
                return;
            }
            
            fetch('/admin-panel/inventario/menu/tipos/ajax-crear/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({ 'nuevo_tipo_nombre': nom, 'nuevo_tipo_desc': des })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    const select = document.getElementById('id_tipo_menu_fk');
                    const opt = new Option(data.nombre, data.id, true, true);
                    select.add(opt);
                    document.getElementById('nuevo_tipo_nombre').value = '';
                    document.getElementById('nuevo_tipo_desc').value = '';
                    
                    formTipo.hidden = true;
                    btnTipo.setAttribute('aria-expanded', false);
                    btnTipo.classList.remove('active');
                    
                    Swal.fire({ icon: 'success', title: 'Tipo guardado', showConfirmButton: false, timer: 3000 });
                } else {
                    Swal.fire({ icon: 'error', title: data.error, showConfirmButton: false, timer: 3000 });
                }
            }).catch(err => console.error(err));
        });
    }
});

function eliminarTipoMenuInline() {
    const select = document.getElementById('id_tipo_menu_fk');
    const id = select.value;
    if (!id) {
        Swal.fire({ icon: 'warning', title: 'Seleccione un tipo para eliminar', showConfirmButton: false, timer: 3000 });
        return;
    }
    const nombre = select.options[select.selectedIndex].text;
    
    Swal.fire({
        title: '¿Eliminar tipo?',
        text: `¿Estás seguro de eliminar el tipo "${nombre}"?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        cancelButtonColor: '#9ca3af',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/admin-panel/inventario/menu/tipos/ajax-eliminar/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    select.remove(select.selectedIndex);
                    Swal.fire({ icon: 'success', title: 'Tipo eliminado', showConfirmButton: false, timer: 3000 });
                } else {
                    Swal.fire({ icon: 'error', title: data.error, showConfirmButton: false, timer: 4000 });
                }
            }).catch(err => console.error(err));
        }
    });
}
