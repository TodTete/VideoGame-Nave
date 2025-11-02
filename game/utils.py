import os
import pygame

# --------- Audio helpers ----------
def cargar_sonido(ruta, volumen=0.5):
    try:
        s = pygame.mixer.Sound(ruta)
        s.set_volume(volumen)
        return s
    except Exception as e:
        print(f"[AVISO] No se pudo cargar el sonido '{ruta}': {e}")
        return None

def reproducir(sonido):
    if sonido:
        sonido.play()

# --------- Texto / fuente ----------
_FONT_CANDIDATES = [
    "assets/font/RetroRaceDemoItalic.ttf",
    "assets/font/RetroRaceDemoItalic.otf",
    "RetroRaceDemoItalic.ttf",
    "RetroRaceDemoItalic.otf",
]

def _find_font_path():
    for p in _FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None

def load_font(size, bold=False):
    """Carga la fuente Retronoid si existe; si no, usa Arial."""
    path = _find_font_path()
    if path:
        try:
            f = pygame.font.Font(path, size)
            if bold and hasattr(f, "set_bold"):
                f.set_bold(True)
            return f
        except Exception as e:
            print(f"[AVISO] No se pudo cargar fuente '{path}': {e}")
    # Fallback
    return pygame.font.SysFont("Arial", size, bold=bold)

def dibujar_texto(superficie, texto, fuente, color, x, y, centrado=False):
    img = fuente.render(texto, True, color)
    rect = img.get_rect()
    if centrado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    superficie.blit(img, rect)

# --------- Hiscore ----------
def leer_hiscore(ruta="hiscore.txt"):
    try:
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                return int(f.read().strip() or 0)
    except Exception:
        pass
    return 0

def guardar_hiscore(puntos, ruta="hiscore.txt"):
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(str(puntos))
    except Exception as e:
        print(f"[AVISO] No se pudo guardar hiscore: {e}")
