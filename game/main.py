"""
    NASA space apps challenge 2026
    Vanguard Dreamers

    main.py
    Este archivo se encarga de inicializar el juego

    Dependencias necesarias:

        pip install -r game/requirements.txt
        python -m game.main
"""
import os
import sys
import traceback


def _main():
    from game.logica.juego import main
    main()


if __name__ == "__main__":
    try:
        _main()
    except SystemExit:
        raise
    except Exception:
        # En el .exe no hay consola: el error queda en ~/.mision_lunar/error.txt
        try:
            carpeta = os.path.join(os.path.expanduser("~"), ".mision_lunar")
            os.makedirs(carpeta, exist_ok=True)
            with open(os.path.join(carpeta, "error.txt"), "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
        except Exception:
            pass
        raise
    sys.exit(0)
