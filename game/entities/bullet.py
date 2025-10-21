from .. import assets as Assets
from ..constants import ALTO, ANCHO
import pygame

class Bala:
    def __init__(self, x, y, vy=-9):
        self.image = Assets.BALA_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = 0
        self.vy = vy

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        return self.rect.bottom > 0 and self.rect.top < ALTO and self.rect.right > 0 and self.rect.left < ANCHO

    def draw(self, surface, cam_apply_rect):
        drect = cam_apply_rect(self.rect)
        surface.blit(self.image, drect.topleft)
