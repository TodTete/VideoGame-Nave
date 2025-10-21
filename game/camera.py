from .constants import CAM_LERP, CAM_FACTOR, CAM_MAX
import pygame

class Camera:
    def __init__(self):
        self.x, self.y = 0.0, 0.0

    def target_from_player(self, player_rect, ancho, alto):
        tx = (ancho/2 - player_rect.centerx) * CAM_FACTOR
        ty = (alto/2  - player_rect.centery) * CAM_FACTOR
        tx = max(-CAM_MAX, min(CAM_MAX, tx))
        ty = max(-CAM_MAX, min(CAM_MAX, ty))
        return tx, ty

    def update(self, tx, ty):
        self.x += (tx - self.x) * CAM_LERP
        self.y += (ty - self.y) * CAM_LERP

    def apply_point(self, x, y):
        return int(x + self.x), int(y + self.y)

    def apply_rect(self, r: pygame.Rect):
        return pygame.Rect(r.left + int(self.x), r.top + int(self.y), r.width, r.height)
