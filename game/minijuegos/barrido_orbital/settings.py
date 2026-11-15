import os
# ==========================================
# VARIABLES DE ENTRADA (CONFIGURACIÓN)
# ==========================================

# Ventana y Rendimiento
WIDTH = 1024
HEIGHT = 640
FPS = 60
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paleta de Colores (RGB)
BG_COLOR = (10, 14, 26)
SAA_BG_COLOR = (38, 12, 24)
TEXT_COLOR = (230, 240, 255)
MODULE_BASE_COLOR = (45, 65, 95)
MODULE_BORDER_COLOR = (100, 180, 255)
MODULE_HIT_FILL = (180, 40, 60)
MODULE_HIT_BORDER = (255, 100, 120)

# Configuración de Módulos (Nombre, X, Y, Ancho, Alto, Ruta_Imagen)
MODULES_CONFIG = [
    ("Columbus", 50, 115, 140, 90, os.path.join(BASE_DIR, "assets", "columbus.png")),
    ("US Lab",   50, 270, 140, 90, os.path.join(BASE_DIR, "assets", "us_lab.png")),
    ("SM",       50, 425, 140, 90, os.path.join(BASE_DIR, "assets", "sm.png")),
]

# Configuración de Partículas
PARTICLE_TYPES = {
    "electron": {
        "color": (0, 220, 255),
        "speed": 400,
        "radius": 6,
        "dose": 5.0,
        "points": 10,
        "ideal": "LIULIN"
    },
    "proton": {
        "color": (255, 200, 0),
        "speed": 350,
        "radius": 10,
        "dose": 12.0,
        "points": 25,
        "ideal": "TIMEPIX"
    },
    "heavy_ion": {
        "color": (255, 50, 100),
        "speed": 200,
        "radius": 15,
        "dose": 25.0,
        "points": 50,
        "ideal": "ALTEA"
    }
}

# Parámetros de Gameplay y Órbita
SPAWN_INTERVAL = 1.0         # Segundos entre cada partícula
CLICK_MARGIN = 12            # Píxeles extra para facilitar el clic
TRAIL_MAX_LENGTH = 14        # Largo de la estela visual
ORBIT_DURATION = 15.0        # Duración total en segundos
SAA_START = 7.0             # Inicio Anomalía del Atlántico Sur
SAA_END = 12.0               # Fin Anomalía del Atlántico Sur
MAX_DOSE = 30             # Límite de radiación antes de perder

# Configuración de Detectores
DETECTORS_CONFIG = {
    "LIULIN": {
        "key": "1",
        "label": "[1] LIULIN (Área + -Dosis)",
        "color": (0, 220, 255),
        "aoe_radius": 45,         # Radio de barrido en área (px)
        "dose_reduction": 1.5,    # Reduce dosis si acierta el ideal (electrón)
        "cooldown": 0.15
    },
    "TIMEPIX": {
        "key": "2",
        "label": "[2] TIMEPIX (Tracks + Lento)",
        "color": (255, 200, 0),
        "slow_radius": 130,       # Radio alrededor del cursor que ralentiza
        "cooldown": 0.25
    },
    "ALTEA": {
        "key": "3",
        "label": "[3] ALTEA (Iones x3 Pts)",
        "color": (255, 50, 100),
        "ion_multiplier": 3,      # Multiplicador de puntos en iones pesados
        "cooldown": 0.35
    }
}

# Nombres científicos reales de iones para mostrar con ALTEA
HEAVY_ION_NAMES = ["Fe-56 (Hierro)", "C-12 (Carbono)", "O-16 (Oxígeno)", "Si-28 (Silicio)"]

# Tasas de aparición y probabilidades (Órbita Normal vs Anomalía del Atlántico Sur)
NORMAL_SPAWN_INTERVAL = 1.15     # 1 partícula cada 1.15s en órbita normal
SAA_SPAWN_INTERVAL = 0.42        # 1 partícula cada 0.42s dentro de la SAA

# Pesos de probabilidad: [electron, proton, heavy_ion]
NORMAL_WEIGHTS = [0.60, 0.30, 0.10]
SAA_WEIGHTS = [0.25, 0.45, 0.30]

# Configuración de Explosiones (Chispas)
EXPLOSION_PARTICLE_COUNT = 14    # Cantidad de chispas por explosión
EXPLOSION_SPEED_MIN = 60         # Velocidad mínima de las chispas (px/s)
EXPLOSION_SPEED_MAX = 240        # Velocidad máxima de las chispas (px/s)
EXPLOSION_LIFETIME = 0.45        # Duración de la explosión en segundos

# ==========================================
# VARIABLES DE ENTRADA (CONFIGURACIÓN)
# ==========================================

# Rutas de Recursos (Compatible con PyInstaller y ejecución normal)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "assets", "PressStart2P-Regular.ttf")

# Tamaños de Fuente
MAIN_FONT_SIZE = 14
SMALL_FONT_SIZE = 10

# Configuración de Audio Procedural (NumPy + Pygame Mixer)
SAMPLE_RATE = 44100          # Frecuencia de muestreo estándar (Hz)
MASTER_VOLUME = 0.35         # Volumen general (0.0 a 1.0)

# Configuración de Flotación Espacial (Gravedad Cero en Módulos)
FLOAT_AMPLITUDE_Y = 5.0      # Píxeles que sube y baja el módulo
FLOAT_AMPLITUDE_X = 2.0      # Píxeles que deriva ligeramente hacia los lados
FLOAT_SPEED = 1.8            # Velocidad de oscilación orbital
FLOAT_TILT_ANGLE = 2.2       # Grados máximos de inclinación suave

# ==========================================
# GESTOR GLOBAL DE FUENTES (Solo rutas y tamaños)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "assets", "PressStart2P-Regular.ttf")

MAIN_FONT_SIZE = 14
SMALL_FONT_SIZE = 10
TINY_FONT_SIZE = 8

# Configuración de Fondo Estelar (Parallax Orbital)
STAR_COUNT = 65              # Cantidad total de estrellas en pantalla
STAR_SPEED_MIN = 15.0        # Velocidad estrellas lejanas (px/s)
STAR_SPEED_MAX = 65.0        # Velocidad estrellas cercanas (px/s)

