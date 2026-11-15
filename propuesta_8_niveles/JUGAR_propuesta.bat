@echo off
setlocal
rem Prueba la propuesta de 8 tareas sin tocar el juego del repositorio (usa una copia temporal).
rem Usa el mismo entorno .venv que game\JUGAR.bat (lo crea si no existe).
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 -m venv .venv
    ) else (
        python -m venv .venv
    )
    if errorlevel 1 goto error
)
echo Comprobando dependencias...
".venv\Scripts\python.exe" -m pip install -r "game\requirements.txt"
if errorlevel 1 goto error
echo Abriendo la propuesta...
".venv\Scripts\python.exe" "propuesta_8_niveles\probar_propuesta.py"
if errorlevel 1 goto error
exit /b 0

:error
echo.
echo No se pudo abrir la propuesta. Probar primero game\JUGAR.bat (instala lo necesario).
pause
exit /b 1
