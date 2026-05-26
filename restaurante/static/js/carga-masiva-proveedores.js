let parsedData  = [];   // filas del CSV/Excel
let logResults  = [];   // resultados del envío
let httpMethod  = 'POST';
let abortFlag   = false;

function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

const dropzone  = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');

function initCargaMasiva() {
    document.getElementById('btn-descargar-csv').addEventListener('click', handleDownloadCsv);
    document.getElementById('btn-post').addEventListener('click', () => setMethod('POST'));
    document.getElementById('btn-get').addEventListener('click', () => setMethod('GET'));
    document.getElementById('btn-add-header').addEventListener('click', addHeaderRow);
    document.getElementById('btn-validar').addEventListener('click', validateData);
    document.getElementById('btn-enviar').addEventListener('click', sendToAPI);
    document.getElementById('btn-export-log').addEventListener('click', exportLogCsv);
    document.getElementById('btn-limpiar').addEventListener('click', clearAll);
    document.getElementById('send-mode').addEventListener('change', handleModeChange);
    document.getElementById('btn-remove-file').addEventListener('click', clearFile);

    dropzone.addEventListener('dragover',  e => { e.preventDefault(); dropzone.classList.add('drag-over'); });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drag-over'));
    dropzone.addEventListener('drop', e => {
        e.preventDefault(); dropzone.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file) processFile(file);
    });
    fileInput.addEventListener('change', () => {
        if (fileInput.files[0]) processFile(fileInput.files[0]);
    });

    document.querySelectorAll('.btn-remove-row:not([disabled])').forEach(btn => {
        btn.addEventListener('click', () => btn.closest('.header-row').remove());
    });

    handleModeChange();
}

function handleDownloadCsv() {
    const header = [
        'nom_provee','apellido_provee','fecha_naci_provee',
        'tel_provee','correo_provee','direc_provee','estado_provee'
    ].join(',');
    const example = [
        'Distribuidora Ejemplo','','1980-01-01',
        '3001234567','ejemplo@correo.com','Calle 123','activo'
    ].join(',');
    const csv = header + '\n' + example;
    downloadText(csv, 'plantilla_proveedores.csv', 'text/csv');
}

function downloadText(content, filename, mime) {
    const blob = new Blob([content], { type: mime });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
}

function processFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!['csv','xlsx','xls'].includes(ext)) {
        alert('Formato no soportado. Usa CSV o Excel (.xlsx/.xls)');
        return;
    }
    if (ext === 'csv') {
        const reader = new FileReader();
        reader.onload = e => {
            parsedData = parseCSV(e.target.result);
            onDataLoaded(file.name);
        };
        reader.readAsText(file, 'UTF-8');
    } else {
        alert('Para Excel, convierte a CSV primero o usa la plantilla CSV provista.');
    }
}

function parseCSV(text) {
    const lines = text.trim().split('\n').filter(l => l.trim());
    if (lines.length < 2) return [];
    const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g,''));
    return lines.slice(1).map(line => {
        const vals = line.split(',').map(v => v.trim().replace(/^"|"$/g,''));
        const obj = {};
        headers.forEach((h, i) => { obj[h] = vals[i] ?? ''; });
        return obj;
    });
}

function onDataLoaded(fileName) {
    document.getElementById('file-name').textContent = fileName;
    document.getElementById('file-rows').textContent = parsedData.length + ' filas detectadas';
    document.getElementById('file-loaded').classList.add('visible');
    updateJSONPreview();
    document.getElementById('btn-enviar').disabled = false;
    setStep(3);
}

function updateJSONPreview() {
    const preview = parsedData.slice(0, 3);
    const mode    = document.getElementById('send-mode').value;
    let text;
    if (mode === 'bulk') {
        text = syntaxHighlight(JSON.stringify(preview, null, 2));
    } else {
        text = syntaxHighlight(JSON.stringify(preview[0] ?? {}, null, 2));
    }
    document.getElementById('json-preview').innerHTML = text;
    document.getElementById('json-count').textContent =
        `${parsedData.length} proveedores cargados · mostrando primeros ${Math.min(3, parsedData.length)}`;
}

function syntaxHighlight(json) {
    return json
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, match => {
            let cls = 'json-num';
            if (/^"/.test(match)) {
                cls = /:$/.test(match) ? 'json-key' : 'json-str';
            } else if (/true|false/.test(match)) { cls = 'json-bool'; }
            else if (/null/.test(match)) { cls = 'json-null'; }
            return `<span class="${cls}">${match}</span>`;
        });
}

function handleModeChange() {
    const oneByOne = document.getElementById('send-mode').value === 'one-by-one';
    document.getElementById('delay-field').style.display = oneByOne ? 'flex' : 'none';
    if (parsedData.length) updateJSONPreview();
}

function setMethod(m) {
    httpMethod = m;
    document.getElementById('btn-post').className = 'method-btn' + (m==='POST' ? ' active-post' : '');
    document.getElementById('btn-get').className  = 'method-btn' + (m==='GET'  ? ' active-get'  : '');
}

function addHeaderRow() {
    const list = document.getElementById('headers-list');
    const row  = document.createElement('div');
    row.className = 'header-row';
    row.innerHTML = `
        <input type="text" placeholder="Nombre del header" />
        <input type="text" placeholder="Valor" />
        <button class="btn-remove-row">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>`;
    const removeBtn = row.querySelector('.btn-remove-row');
    removeBtn.addEventListener('click', () => row.remove());
    list.appendChild(row);
}

function getHeaders() {
    const headers = {};
    // Siempre incluir CSRF token para peticiones Django
    const csrfToken = getCSRFToken();
    if (csrfToken) headers['X-CSRFToken'] = csrfToken;
    document.querySelectorAll('.header-row').forEach(row => {
        const inputs = row.querySelectorAll('input');
        const key = inputs[0].value.trim();
        const val = inputs[1].value.trim();
        if (key && val) headers[key] = val;
    });
    return headers;
}

function validateData() {
    if (!parsedData.length) { alert('Primero carga un archivo.'); return; }
    const required = ['nom_provee','fecha_naci_provee','tel_provee','correo_provee','direc_provee','estado_provee'];
    let errCount = 0;
    parsedData.forEach(row => {
        required.forEach(field => {
            if (!row[field]) errCount++;
        });
    });
    if (errCount === 0) {
        alert(`✅ Validación OK — ${parsedData.length} proveedores listos para enviar`);
    } else {
        alert(`⚠️ Se encontraron ${errCount} campos vacíos requeridos. Revisa el archivo.`);
    }
}

async function sendToAPI() {
    if (!parsedData.length) { alert('Carga un archivo primero.'); return; }
    const url     = document.getElementById('api-url').value.trim();
    if (!url) { alert('Ingresa la URL del endpoint.'); return; }

    const mode    = document.getElementById('send-mode').value;
    const headers = getHeaders();
    const delay   = parseInt(document.getElementById('delay-ms').value) || 0;

    logResults = [];
    abortFlag  = false;
    setStep(4);
    showProgress(true);
    document.getElementById('btn-enviar').disabled = true;
    document.getElementById('results-section').classList.remove('visible');
    document.getElementById('log-tbody').innerHTML = '';

    const startTime = Date.now();

    if (mode === 'bulk') {
        await sendBulk(url, headers, startTime);
    } else {
        await sendOneByOne(url, headers, delay, startTime);
    }
}

async function sendBulk(url, headers, startTime) {
    try {
        const res = await fetch(url, {
            method: httpMethod,
            headers,
            credentials: 'same-origin',
            body: httpMethod !== 'GET' ? JSON.stringify(parsedData) : undefined
        });
        const status = res.status;
        let msg = '';
        try { const j = await res.json(); msg = JSON.stringify(j).slice(0, 80); } catch { msg = res.statusText; }
        const ok = res.ok;
        parsedData.forEach((row, i) => {
            logResults.push({ idx: i+1, name: row.nom_provee, status, ok, msg: ok ? 'Registrado' : msg });
        });
    } catch (err) {
        parsedData.forEach((row, i) => {
            logResults.push({ idx: i+1, name: row.nom_provee, status: 0, ok: false, msg: err.message });
        });
    }
    finishSend(startTime);
}

async function sendOneByOne(url, headers, delay, startTime) {
    for (let i = 0; i < parsedData.length; i++) {
        if (abortFlag) break;
        const row = parsedData[i];
        updateProgress(i, parsedData.length, `Enviando ${i+1} / ${parsedData.length}: ${row.nom_provee}`);
        try {
            const res = await fetch(url, {
                method: httpMethod,
                headers,
                credentials: 'same-origin',
                body: httpMethod !== 'GET' ? JSON.stringify(row) : undefined
            });
            const status = res.status;
            let msg = '';
            try { const j = await res.json(); msg = JSON.stringify(j).slice(0, 80); } catch { msg = res.statusText; }
            logResults.push({ idx: i+1, name: row.nom_provee, status, ok: res.ok, msg: res.ok ? 'Registrado' : msg });
        } catch (err) {
            logResults.push({ idx: i+1, name: row.nom_provee, status: 0, ok: false, msg: err.message });
        }
        if (delay > 0 && i < parsedData.length - 1) await sleep(delay);
    }
    finishSend(startTime);
}

function finishSend(startTime) {
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    const okCount  = logResults.filter(r => r.ok).length;
    const errCount = logResults.filter(r => !r.ok).length;

    updateProgress(logResults.length, logResults.length, 'Completado');
    setTimeout(() => showProgress(false), 800);

    document.getElementById('res-total').textContent = logResults.length;
    document.getElementById('res-ok').textContent    = okCount;
    document.getElementById('res-err').textContent   = errCount;
    document.getElementById('res-time').textContent  = elapsed + 's';

    const tbody = document.getElementById('log-tbody');
    tbody.innerHTML = '';
    logResults.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${r.idx}</td>
            <td><strong>${escapeHTML(r.name || '—')}</strong></td>
            <td><code>${r.status || '—'}</code></td>
            <td class="text-center">
                <span class="status-badge ${r.ok ? 'status-ok' : 'status-err'}">
                    <span class="status-dot"></span>
                    ${r.ok ? 'OK' : 'Error'}
                </span>
            </td>
            <td class="log-message">${escapeHTML(r.msg || '')}</td>`;
        tbody.appendChild(tr);
    });

    document.getElementById('results-section').classList.add('visible');
    document.getElementById('btn-enviar').disabled = false;
}

function exportLogCsv() {
    if (!logResults.length) return;
    const header = '#,Proveedor,Status HTTP,Resultado,Mensaje';
    const rows   = logResults.map(r =>
        `${r.idx},"${r.name}",${r.status},${r.ok ? 'OK' : 'Error'},"${r.msg}"
    `);
    downloadText([header, ...rows].join('\n'), 'log_carga_masiva.csv', 'text/csv');
}

function clearFile() {
    parsedData = [];
    fileInput.value = '';
    document.getElementById('file-loaded').classList.remove('visible');
    document.getElementById('json-preview').innerHTML = '<span class="preview-placeholder">// Aquí aparecerá el JSON generado</span>';
    document.getElementById('json-count').textContent = 'Carga un archivo para ver la preview';
    document.getElementById('btn-enviar').disabled = true;
    setStep(2);
}

function clearAll() {
    clearFile();
    logResults = [];
    document.getElementById('results-section').classList.remove('visible');
    document.getElementById('log-tbody').innerHTML = '';
    showProgress(false);
    setStep(1);
}

function showProgress(visible) {
    document.getElementById('progress-wrap').classList.toggle('visible', visible);
}
function updateProgress(done, total, label) {
    const pct = total ? Math.round((done / total) * 100) : 0;
    document.getElementById('progress-fill').style.width = pct + '%';
    document.getElementById('progress-pct').textContent  = pct + '%';
    document.getElementById('progress-text').textContent = label;
}

function setStep(n) {
    for (let i = 1; i <= 4; i++) {
        const s = document.getElementById('step-' + i);
        s.classList.remove('active','done');
        if (i < n) s.classList.add('done');
        if (i === n) s.classList.add('active');
    }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function escapeHTML(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

initCargaMasiva();
