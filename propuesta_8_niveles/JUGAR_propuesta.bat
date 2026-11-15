@echo off
rem Prueba la propuesta de 8 tareas sin tocar el juego del repositorio (usa una copia temporal).
python "%~dp0probar_propuesta.py"
if errorlevel 1 pause
