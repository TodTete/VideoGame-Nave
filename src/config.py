# =========================
# Configuración / Constantes
# =========================
ANCHO, ALTO = 800, 600
FPS = 60

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO   = (255, 0, 0)
AZUL   = (0, 120, 255)
AMARILLO = (255, 215, 0)
VERDE = (0, 200, 120)
MORADO = (170, 120, 255)
GRIS = (40, 40, 50)

# Estados
MENU = "MENU"
LEVEL_INTRO = "LEVEL_INTRO"
BOSS_INTRO = "BOSS_INTRO"
JUGANDO = "JUGANDO"
PAUSA = "PAUSA"
GAME_OVER = "GAME_OVER"

# Umbral para jefe por nivel
BOSS_POINTS_PER_LEVEL = 250

# Duraciones
LEVEL_INTRO_MS = 1500
BOSS_INTRO_MS = 1200

# Cámara
CAM_LERP   = 0.12
CAM_FACTOR = 0.35
CAM_MAX    = 120

# Bombas del jefe
BOMB_RESPAWN_MS = 9000    # spawn periódico
BOMB_PICKUP_LIFE = 7000   # vida del ítem si no lo recogen

ASSETS_DIR = "assets"
HISCORE_FILE = "hiscore.txt"
