import pygame
from .gif import load_gif_frames
from .constants import (
    ASTEROID_W, ASTEROID_H, PLAYER_W, PLAYER_H, BOSS_W, BOSS_H
)

# Singletons (se llenan tras set_mode)
ASTEROID_FRAMES = ASTEROID_DURS = None, None
PLAYER_FRAMES = PLAYER_DURS = None, None
BOSS_FRAMES = BOSS_DURS = None, None
BALA_IMG = None
BALA2_IMG = None       # << NUEVO (bala ancha)
PLAYER_SKIN = "BRAYAN" # << NUEVO (tracking actual)

def _cargar_asteroid_frames():
    for ruta in ("assets/extra/asteroides.gif",):
        frames, durs = load_gif_frames(ruta, size=(ASTEROID_W, ASTEROID_H))
        if frames:
            print(f"[INFO] Asteroides: {len(frames)} frames")
            return frames, durs
    print("[AVISO] No 'asteroides.gif'. Placeholder.")
    surf = pygame.Surface((ASTEROID_W, ASTEROID_H), pygame.SRCALPHA)
    surf.fill((200, 80, 80, 180))
    return [surf], [120]

def _frames_from_image(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, size)
        return [img], [120]
    except Exception as e:
        print(f"[AVISO] No '{path}': {e}")
        ph = pygame.Surface(size, pygame.SRCALPHA)
        ph.fill((30,120,240,200))
        return [ph], [120]

def _cargar_player_frames_for_skin(skin):
    # BRAYAN = gif animado; el resto: imagen fija escalada
    if skin == "BRAYAN":
        for ruta in ("assets/extra/nave.gif",):
            frames, durs = load_gif_frames(ruta, size=(PLAYER_W, PLAYER_H))
            if frames:
                print(f"[INFO] Nave (BRAYAN): {len(frames)} frames")
                return frames, durs
        print("[AVISO] No 'nave.gif'. Placeholder.")
        surf = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (30,120,240),
                            [(PLAYER_W//2,4),(10,PLAYER_H-6),(PLAYER_W-10,PLAYER_H-6)])
        return [surf], [120]
    elif skin == "FERNANDA":
        return _frames_from_image("assets/extra/nave-f.jpg", (PLAYER_W, PLAYER_H))
    elif skin == "MARLIN":
        return _frames_from_image("assets/extra/nave-m.png", (PLAYER_W, PLAYER_H))
    elif skin == "TETE":
        return _frames_from_image("assets/extra/nave-t.png", (PLAYER_W, PLAYER_H))
    else:
        return _frames_from_image("assets/extra/nave-m.png", (PLAYER_W, PLAYER_H))

def _cargar_boss_frames():
    for ruta in ("assets/personajes/jefe.gif",):
        frames, durs = load_gif_frames(ruta, size=(BOSS_W, BOSS_H))
        if frames:
            print(f"[INFO] Jefe: {len(frames)} frames")
            return frames, durs
    print("[AVISO] No 'jefe.gif'. Placeholder.")
    surf = pygame.Surface((BOSS_W, BOSS_H), pygame.SRCALPHA)
    pygame.draw.rect(surf, (140,25,25), (0,0,BOSS_W,BOSS_H), border_radius=16)
    return [surf], [120]

def _cargar_imagen_bala():
    try:
        img = pygame.image.load("assets/extra/bala.png").convert_alpha()
        img = pygame.transform.smoothscale(img, (14, 30))
        return img
    except Exception as e:
        print(f"[AVISO] No 'assets/extra/bala.png': {e}")
        ph = pygame.Surface((14, 30), pygame.SRCALPHA)
        pygame.draw.rect(ph, (255,255,255), ph.get_rect(), border_radius=3)
        return ph

def _cargar_imagen_bala2():
    # bala ancha para Fernanda
    try:
        img = pygame.image.load("assets/extra/bala-2.png").convert_alpha()
        # Ligeramente más ancha (antes 20x32)
        img = pygame.transform.smoothscale(img, (24, 32))
        return img
    except Exception as e:
        print(f"[AVISO] No 'assets/extra/bala-2.png': {e}")
        ph = pygame.Surface((44, 52), pygame.SRCALPHA)
        pygame.draw.rect(ph, (255,255,255), ph.get_rect(), border_radius=3)
        return ph

def set_player_skin(skin):
    """Cambiar el skin del jugador y recargar frames tras set_mode."""
    global PLAYER_FRAMES, PLAYER_DURS, PLAYER_SKIN
    PLAYER_SKIN = skin
    PLAYER_FRAMES, PLAYER_DURS = _cargar_player_frames_for_skin(skin)

def init_after_display():
    global ASTEROID_FRAMES, ASTEROID_DURS, PLAYER_FRAMES, PLAYER_DURS
    global BOSS_FRAMES, BOSS_DURS, BALA_IMG, BALA2_IMG
    ASTEROID_FRAMES, ASTEROID_DURS = _cargar_asteroid_frames()
    # Default: BRAYAN
    PLAYER_FRAMES,   PLAYER_DURS   = _cargar_player_frames_for_skin("BRAYAN")
    BOSS_FRAMES,     BOSS_DURS     = _cargar_boss_frames()
    BALA_IMG = _cargar_imagen_bala()
    BALA2_IMG = _cargar_imagen_bala2()

def cargar_boss_por_planeta(planet_id):
    """
    Carga los frames del jefe asociado al planeta actual.
    Busca versiones animadas y estáticas; si no encuentra, usa un placeholder.
    """
    candidatos = [
        f"assets/personajes/jefe-{planet_id}.png",
        f"assets/personajes/jefe-{planet_id}.jpg",
        "assets/personajes/jefe.gif",
        "assets/personajes/jefe.png",
    ]

    for ruta in candidatos:
        try:
            frames, durs = load_gif_frames(ruta, size=(BOSS_W, BOSS_H))
            if frames:
                print(f"[INFO] Jefe del planeta {planet_id} cargado desde {ruta}")
                return frames, durs
        except Exception:
            pass

        try:
            frames, durs = _frames_from_image(ruta, (BOSS_W, BOSS_H))
            if frames:
                print(f"[INFO] Jefe del planeta {planet_id} (imagen estática) {ruta}")
                return frames, durs
        except Exception:
            pass

    print(f"[AVISO] No se encontró jefe para planeta {planet_id}. Se usa placeholder.")
    surf = pygame.Surface((BOSS_W, BOSS_H), pygame.SRCALPHA)
    pygame.draw.rect(surf, (160, 30, 30), (0, 0, BOSS_W, BOSS_H), border_radius=16)
    return [surf], [120]
