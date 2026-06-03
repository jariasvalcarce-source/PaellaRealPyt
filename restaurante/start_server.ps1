param(
    [switch]$NoStart
)

Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Error "No se encontró el entorno virtual en .venv/Scripts/Activate.ps1"
    exit 1
}

& ".\.venv\Scripts\Activate.ps1"

if ($NoStart) {
    Write-Host "Entorno activado correctamente."
    python --version
    exit 0
}

Write-Host "Iniciando Django en http://127.0.0.1:8000 ..."
python manage.py runserver
