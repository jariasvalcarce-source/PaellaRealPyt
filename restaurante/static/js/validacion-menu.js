function previewImagen(input) {
    const preview = document.getElementById('previewCrear');
    if (input.files && input.files[0]) {
        preview.src = URL.createObjectURL(input.files[0]);
        preview.style.display = 'block';
    }
}