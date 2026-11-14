@echo off
rem Base Lunar - doble clic para jugar (necesita Python con pygame-ce y numpy)
cd /d "%~dp0"
python main.py
if errorlevel 1 (
  echo.
  echo No se pudo abrir el juego. Si dice que falta pygame, escribi:  pip install pygame-ce numpy
  pause
)
