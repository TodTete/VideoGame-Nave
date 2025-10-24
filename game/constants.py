# =========================
# Configuración / Constantes
# =========================
ANCHO, ALTO = 800, 600
FPS = 60

GAME_TITLE = "spaces astro"

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO   = (255, 0, 0)
AZUL   = (0, 120, 255)
AMARILLO = (255, 215, 0)      # Amarillo dorado (HUD)
VERDE = (0, 200, 120)
MORADO = (170, 120, 255)      # Encabezados de opciones/dificultad
GRIS = (40, 40, 50)
ORO = (212, 175, 55)          # Dorado más “metálico” para título

# Estados
MENU_MAIN = "MENU_MAIN"
MENU_OPTIONS = "MENU_OPTIONS"
MENU_DIFFICULTY = "MENU_DIFFICULTY"
MENU_CHARACTER = "MENU_CHARACTER"  # << NUEVO
LEVEL_INTRO = "LEVEL_INTRO"
BOSS_INTRO = "BOSS_INTRO"
JUGANDO = "JUGANDO"
PAUSA = "PAUSA"
GAME_OVER = "GAME_OVER"

# (Opcional) etiquetas visibles de naves
SHIP_DISPLAY = {
    "BRAYAN":   "N. de Brayan",
    "FERNANDA": "N. de Fer",
    "MARLIN":   "N. de Mar",
    "TETE":     "N. de Tete",
}
SHIP_ORDER = ["BRAYAN", "FERNANDA", "MARLIN", "TETE"]

# Progresión
BOSS_POINTS_PER_LEVEL = 250

# Duraciones
LEVEL_INTRO_MS = 1500
BOSS_INTRO_MS = 1200

# Sprites
ASTEROID_W, ASTEROID_H = 40, 40
PLAYER_W, PLAYER_H = 60, 60
BOSS_W, BOSS_H = 220, 100

# Cámara
CAM_LERP   = 0.12
CAM_FACTOR = 0.35
CAM_MAX    = 120

# Dificultad (multiplicadores)
# => EXTREMA ahora es sensiblemente más dura
DIFFICULTY_PRESETS = {
    "BAJA":     {"enemy_speed": 0.85, "boss_hp": 0.85},
    "MEDIA":    {"enemy_speed": 1.00, "boss_hp": 1.00},
    "ALTA":     {"enemy_speed": 1.20, "boss_hp": 1.20},
    "EXTREMA":  {"enemy_speed": 1.75, "boss_hp": 1.90},  # ↑ antes 1.45 / 1.45
}
DIFFICULTY_ORDER = ["BAJA", "MEDIA", "ALTA", "EXTREMA"]
