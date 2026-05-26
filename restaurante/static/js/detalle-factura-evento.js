document.addEventListener('DOMContentLoaded', () => {
    const logoUpload = document.getElementById('logo-upload');
    const logoImg = document.getElementById('logo-img');
    const logoPlaceholder = document.getElementById('logo-placeholder');
    const printButton = document.getElementById('btn-print-factura-evento');

    if (logoImg && logoPlaceholder) {
        logoImg.addEventListener('error', () => {
            logoImg.style.display = 'none';
            logoPlaceholder.style.display = 'flex';
        });
    }

    if (logoUpload && logoImg && logoPlaceholder) {
        logoUpload.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (ev) {
                logoImg.src = ev.target.result;
                logoImg.style.display = 'block';
                logoPlaceholder.style.display = 'none';
            };
            reader.readAsDataURL(file);
        });
    }

    if (printButton) {
        printButton.addEventListener('click', () => {
            window.print();
        });
    }
});
