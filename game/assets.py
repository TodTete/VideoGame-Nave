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

def _cargar_asteroid_frames():
    for ruta in ("assets/asteroides.gif",):
        frames, durs = load_gif_frames(ruta, size=(ASTEROID_W, ASTEROID_H))
        if frames:
            print(f"[INFO] Asteroides: {len(frames)} frames")
            return frames, durs
    print("[AVISO] No 'asteroides.gif'. Placeholder.")
    surf = pygame.Surface((ASTEROID_W, ASTEROID_H), pygame.SRCALPHA)
    surf.fill((200, 80, 80, 180))
    return [surf], [120]

def _cargar_player_frames():
    for ruta in ("assets/nave.gif",):
        frames, durs = load_gif_frames(ruta, size=(PLAYER_W, PLAYER_H))
        if frames:
            print(f"[INFO] Nave: {len(frames)} frames")
            return frames, durs
    print("[AVISO] No 'nave.gif'. Placeholder.")
    surf = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (30,120,240),
                        [(PLAYER_W//2,4),(10,PLAYER_H-6),(PLAYER_W-10,PLAYER_H-6)])
    return [surf], [120]

def _cargar_boss_frames():
    for ruta in ("assets/jefe.gif",):
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
        img = pygame.image.load("assets/bala.png").convert_alpha()
        # tamaño más grande (antes ~8x18)
        img = pygame.transform.smoothscale(img, (14, 30))
        return img
    except Exception as e:
        print(f"[AVISO] No 'assets/bala.png': {e}")
        ph = pygame.Surface((14, 30), pygame.SRCALPHA)
        pygame.draw.rect(ph, (255,255,255), ph.get_rect(), border_radius=3)
        return ph

def init_after_display():
    global ASTEROID_FRAMES, ASTEROID_DURS, PLAYER_FRAMES, PLAYER_DURS
    global BOSS_FRAMES, BOSS_DURS, BALA_IMG
    ASTEROID_FRAMES, ASTEROID_DURS = _cargar_asteroid_frames()
    PLAYER_FRAMES,   PLAYER_DURS   = _cargar_player_frames()
    BOSS_FRAMES,     BOSS_DURS     = _cargar_boss_frames()
    BALA_IMG = _cargar_imagen_bala()
