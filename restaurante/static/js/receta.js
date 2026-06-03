// static/js/receta.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('form-receta');
    const selectMenu = document.getElementById('select-menu');
    const selectProd = document.getElementById('inp-producto');
    const selectUnid = document.getElementById('inp-unidad');
    const inpCant = document.getElementById('inp-cantidad');
    
    // We expect window.RECETA_DATA to be populated from the template
    const productos = window.RECETA_DATA?.productos || [];
    const unidades = window.RECETA_DATA?.unidades || [];
    const ingredientesActuales = window.RECETA_DATA?.ingredientes_actuales || [];

    const previewBox = document.createElement('div');
    previewBox.style.marginTop = '8px';
    previewBox.style.fontSize = '13px';
    previewBox.style.color = '#374151';
    previewBox.style.fontWeight = '500';
    
    if (inpCant) {
        inpCant.parentNode.parentNode.appendChild(previewBox);
    }

    // Helper: conversion logic equivalent to backend
    function getFactorConversion(abrevOrigen, abrevBase) {
        const orig = abrevOrigen.toUpperCase();
        const base = abrevBase.toUpperCase();
        if (orig === base) return 1.0;
        
        // Peso
        if (orig === 'KG' && base === 'G') return 1000.0;
        if (orig === 'LB' && base === 'G') return 453.59;
        if (orig === 'G' && base === 'KG') return 0.001;
        // Volumen
        if (orig === 'L' && base === 'ML') return 1000.0;
        if (orig === 'ML' && base === 'L') return 0.001;
        if (orig === 'OZ' && base === 'ML') return 29.57;
        // Unidades
        if (orig.includes('DOCENA') && base.includes('UN')) return 12.0;
        if (orig.includes('CUBETA') && base.includes('UN')) return 30.0;
        
        return 1.0;
    }

    function updatePreview() {
        if (!selectProd || !selectUnid || !inpCant) return;
        
        const prodId = parseInt(selectProd.value);
        const uniId = parseInt(selectUnid.value);
        const cant = parseFloat(inpCant.value);
        
        if (!prodId || !uniId || isNaN(cant) || cant <= 0) {
            previewBox.innerHTML = '';
            return;
        }

        const prod = productos.find(p => p.id === prodId);
        const unid = unidades.find(u => u.id === uniId);
        
        if (!prod || !unid) {
            previewBox.innerHTML = '';
            return;
        }
        
        // Verify type compatibility
        if (unid.tipo !== prod.tipo_unidad && prod.tipo_unidad && unid.tipo) {
            previewBox.innerHTML = `<span style="color:var(--red);">⚠️ Unidad incompatible (esperada: ${prod.tipo_unidad})</span>`;
            return;
        }

        const factor = getFactorConversion(unid.abreviatura, prod.base_unit_nom);
        const cantConvertida = cant * factor;
        
        let porciones = 0;
        if (cantConvertida > 0) {
            porciones = Math.floor(prod.stock / cantConvertida);
        }
        
        let colorPorciones = '#10b981'; // green
        if (porciones === 0) colorPorciones = '#ef4444'; // red
        else if (porciones < 5) colorPorciones = '#ef4444';
        else if (porciones <= 20) colorPorciones = '#f59e0b'; // yellow

        previewBox.innerHTML = `
            <div style="background:#f3f4f6; border-radius:6px; padding:8px 12px; margin-top:10px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                    <span>Equivale a:</span>
                    <strong>${cantConvertida.toLocaleString(undefined, {maximumFractionDigits:3})} ${prod.base_unit_nom}</strong>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <span>Stock actual permite:</span>
                    <strong style="color:${colorPorciones}">${porciones} porciones</strong>
                </div>
            </div>
        `;
    }

    if (selectProd) selectProd.addEventListener('change', () => {
        // Filter units by product's unit type
        const prodId = parseInt(selectProd.value);
        const prod = productos.find(p => p.id === prodId);
        if (prod && selectUnid) {
            Array.from(selectUnid.options).forEach(opt => {
                if (!opt.value) return; // skip placeholder
                const u = unidades.find(un => un.id === parseInt(opt.value));
                if (u && u.tipo && prod.tipo_unidad && u.tipo !== prod.tipo_unidad) {
                    opt.style.display = 'none';
                } else {
                    opt.style.display = 'block';
                }
            });
            // Auto-select base unit if available
            selectUnid.value = prod.base_unit_id;
        }
        updatePreview();
    });
    
    if (selectUnid) selectUnid.addEventListener('change', updatePreview);
    if (inpCant) inpCant.addEventListener('input', updatePreview);

    if (form) {
        // Eliminar novalidate para usar HTML5 validation
        form.removeAttribute('novalidate');
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Check duplicates in JS
            if (selectProd && selectMenu) {
                const prodId = parseInt(selectProd.value);
                const menuId = parseInt(selectMenu.value);
                if (ingredientesActuales.includes(prodId)) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Ingrediente duplicado',
                        text: 'Este ingrediente ya está en la receta de este menú. Si quieres cambiar la cantidad, usa Editar.'
                    });
                    return;
                }
            }

            Swal.fire({
                title: '¿Guardar en la receta?',
                text: 'Confirma si los datos ingresados son correctos.',
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#7B1535',
                cancelButtonColor: '#9ca3af',
                confirmButtonText: 'Sí, guardar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();
                }
            });
        });
    }
});
