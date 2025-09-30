import random
from .config import ANCHO, ALTO, CAM_LERP, CAM_FACTOR, CAM_MAX

class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.shake_time_left = 0
        self.shake_amp = 0
        self.shake_x = 0
        self.shake_y = 0

    def target(self, player_rect):
        tx = (ANCHO/2 - player_rect.centerx) * CAM_FACTOR
        ty = (ALTO/2  - player_rect.centery) * CAM_FACTOR
        tx = max(-CAM_MAX, min(CAM_MAX, tx))
        ty = max(-CAM_MAX, min(CAM_MAX, ty))
        return tx, ty

    def trigger_shake(self, ms=280, amplitude=10):
        self.shake_time_left = ms
        self.shake_amp = amplitude

    def update(self, dt, player_rect):
        tx, ty = self.target(player_rect)
        self.x += (tx - self.x) * CAM_LERP
        self.y += (ty - self.y) * CAM_LERP

        # temblor (decay lineal)
        if self.shake_time_left > 0:
            self.shake_time_left = max(0, self.shake_time_left - dt)
            k = self.shake_time_left / 280.0
            amp = max(0, self.shake_amp * k)
            self.shake_x = random.randint(-int(amp), int(amp)) if amp > 1 else 0
            self.shake_y = random.randint(-int(amp), int(amp)) if amp > 1 else 0
        else:
            self.shake_x = self.shake_y = 0

    def apply_point(self, x, y):
        return int(x + self.x + self.shake_x), int(y + self.y + self.shake_y)

    def apply_rect(self, r):
        return r.move(int(self.x + self.shake_x), int(self.y + self.shake_y))
