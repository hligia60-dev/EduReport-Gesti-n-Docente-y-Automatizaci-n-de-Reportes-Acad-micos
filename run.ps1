# Runner oficial de PowerShell para EduReport
# Permite iniciar el servidor Flask resolviendo automaticamente las directivas de seguridad

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  EduReport - Servidor de Desarrollo Flask" -ForegroundColor Green
Write-Host "  Iniciando servidor local en http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Configurar directiva de ejecución temporal para este proceso
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# 2. Verificar existencia del entorno virtual
if (Test-Path ".\.venv\Scripts\python.exe") {
    Write-Host "[OK] Utilizando entorno virtual .venv" -ForegroundColor Green
    & ".\.venv\Scripts\python.exe" run.py
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    Write-Host "[AVISO] Ejecutando con el lanzador py" -ForegroundColor Yellow
    py run.py
} else {
    Write-Host "[ERROR] No se encontro Python ni .venv" -ForegroundColor Red
}

