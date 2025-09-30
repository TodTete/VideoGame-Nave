import os, pygame
from .config import HISCORE_FILE

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

def dibujar_texto(superficie, texto, fuente, color, x, y, centrado=False):
    img = fuente.render(texto, True, color)
    rect = img.get_rect()
    if centrado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    superficie.blit(img, rect)

def leer_hiscore(ruta=HISCORE_FILE):
    try:
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                return int(f.read().strip() or 0)
    except Exception:
        pass
    return 0

def guardar_hiscore(puntos, ruta=HISCORE_FILE):
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(str(puntos))
    except Exception as e:
        print(f"[AVISO] No se pudo guardar hiscore: {e}")
