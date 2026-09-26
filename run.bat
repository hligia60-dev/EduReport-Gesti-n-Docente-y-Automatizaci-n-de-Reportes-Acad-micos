@echo off
title EduReport - Servidor de Desarrollo Flask
color 0A

echo ========================================================
echo   EduReport - Sistema de Gestion Docente y Reportes
echo   Iniciando servidor local Flask en http://127.0.0.1:5000
echo ========================================================
echo.

if exist ".venv\Scripts\python.exe" (
    echo [OK] Utilizando entorno virtual .venv
    ".venv\Scripts\python.exe" run.py
) else (
    echo [AVISO] Entorno virtual no encontrado. Intentando con Python global...
    py run.py
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] No se pudo iniciar el servidor.
    pause
)
