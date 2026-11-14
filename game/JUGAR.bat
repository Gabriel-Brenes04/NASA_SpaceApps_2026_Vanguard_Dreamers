@echo off
setlocal

rem Base Lunar - doble clic para jugar
rem Ejecutar desde la raiz del proyecto

cd /d "%~dp0.."

rem Crear entorno virtual si no existe
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

rem Instalar dependencias
echo Comprobando dependencias...
".venv\Scripts\python.exe" -m pip install -r "game\requirements.txt"
if errorlevel 1 goto error

rem Iniciar juego
echo.
echo Iniciando Mission Survival...
echo.
".venv\Scripts\python.exe" -m game.main
if errorlevel 1 goto error

exit /b 0

:error
echo.
echo No se pudo iniciar el juego.
echo Comprueba Python, las dependencias y la conexion a Internet.
echo.
pause
exit /b 1
