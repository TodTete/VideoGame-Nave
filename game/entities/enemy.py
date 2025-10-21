from .. import assets as Assets
from ..constants import ASTEROID_W, ASTEROID_H, ALTO, ANCHO
import pygame

class FallingEnemy:
    def __init__(self, x, y, w=ASTEROID_W, h=ASTEROID_H):
        self.rect = pygame.Rect(x, y, w, h)
        self.anim_idx = 0; self.anim_accum = 0

    def update(self, dt_ms, vel_y):
        self.rect.y += vel_y
        self.anim_accum += dt_ms
        if self.anim_accum >= Assets.ASTEROID_DURS[self.anim_idx]:
            self.anim_accum = 0
            self.anim_idx = (self.anim_idx + 1) % len(Assets.ASTEROID_FRAMES)

    def draw(self, surface, cam_apply_rect):
        drect = cam_apply_rect(self.rect)
        surface.blit(Assets.ASTEROID_FRAMES[self.anim_idx], drect.topleft)

def crear_enemigos(cantidad):
    import random
    enemigos=[]
    for _ in range(cantidad):
        x = random.randint(0, ANCHO - ASTEROID_W)
        y = random.randint(-250, -ASTEROID_H)
        enemigos.append(FallingEnemy(x,y))
    return enemigos

def respawnear_enemigo(enemigo: 'FallingEnemy'):
    import random
    enemigo.rect.x = random.randint(0, ANCHO - enemigo.rect.width)
    enemigo.rect.y = random.randint(-200, -enemigo.rect.height)
    enemigo.anim_idx = 0; enemigo.anim_accum=0
