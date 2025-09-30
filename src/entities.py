import pygame
from .config import ANCHO, ALTO

class Jugador:
    def __init__(self, centerx, bottom):
        self.base_w = 60
        self.base_h = 60
        self.base_image = self._crear_superficie_nave(self.base_w, self.base_h)
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.rect.centerx = centerx
        self.rect.bottom = bottom
        self.vel_base = 6
        self.vel = self.vel_base
        self.angle = 0.0
        self.target_angle = 0.0
        self.ANGLE_MAX = 22.0
        self.ANGLE_SPEED = 240.0
        self.nose_local = (self.base_w/2, 6)

    def _crear_superficie_nave(self, w, h):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        def P(x, y): return (int(x), int(y))
        col_body_dark = (20, 85, 190)
        col_body      = (30, 120, 240)
        col_wing      = (18, 70, 160)
        col_trim      = (220, 240, 255)
        col_cockpit   = (175, 230, 255)
        nose = P(w*0.5, 4); lw1=P(w*0.18,h*0.52); rw1=P(w*0.82,h*0.52); tl=P(w*0.36,h-6); tr=P(w*0.64,h-6)
        hull=[tl,lw1,nose,rw1,tr]
        pygame.draw.polygon(surf, col_body_dark, hull)
        lw1i=P(w*0.22,h*0.53); rw1i=P(w*0.78,h*0.53); tli=P(w*0.40,h-8); tri=P(w*0.60,h-8)
        hull_inner=[tli,lw1i,P(w*0.5,8),rw1i,tri]
        pygame.draw.polygon(surf, col_body, hull_inner)
        left_wing=[lw1,P(w*0.02,h*0.70),P(w*0.30,h*0.74)]
        right_wing=[rw1,P(w-2,h*0.70),P(w*0.70,h*0.74)]
        pygame.draw.polygon(surf, col_wing, left_wing)
        pygame.draw.polygon(surf, col_wing, right_wing)
        cockpit_rect = pygame.Rect(0,0,int(w*0.24), int(h*0.16)); cockpit_rect.center = P(w*0.5, h*0.28)
        pygame.draw.ellipse(surf, col_cockpit, cockpit_rect); pygame.draw.ellipse(surf, col_trim, cockpit_rect, 2)
        pygame.draw.line(surf, col_trim, P(w*0.5,h*0.12), P(w*0.5,h*0.80), 2)
        pygame.draw.lines(surf, col_trim, True, hull, 2)
        return surf

    def _rotated_image_and_rect(self):
        rotated = pygame.transform.rotozoom(self.base_image, -self.angle, 1.0)
        rrect = rotated.get_rect(center=self.rect.center)
        return rotated, rrect

    def get_muzzle_world(self):
        from pygame.math import Vector2
        base_center = Vector2(self.base_w/2, self.base_h/2)
        nose = Vector2(self.nose_local)
        offset = nose - base_center
        spawn = Vector2(self.rect.center) + offset.rotate(-self.angle)
        return int(spawn.x), int(spawn.y)

    def update(self, dt_ms, keys, bounds_rect):
        dx = 0; dy = 0
        if keys[pygame.K_LEFT]:  dx -= self.vel
        if keys[pygame.K_RIGHT]: dx += self.vel
        if keys[pygame.K_UP]:    dy -= self.vel
        if keys[pygame.K_DOWN]:  dy += self.vel

        self.rect.move_ip(dx, dy)
        self.rect.clamp_ip(bounds_rect)

        if dx > 0:   self.target_angle = +self.ANGLE_MAX
        elif dx < 0: self.target_angle = -self.ANGLE_MAX
        else:        self.target_angle = 0.0

        max_delta = self.ANGLE_SPEED * (dt_ms / 1000.0)
        if self.angle < self.target_angle:
            self.angle = min(self.angle + max_delta, self.target_angle)
        elif self.angle > self.target_angle:
            self.angle = max(self.angle - max_delta, self.target_angle)

    def draw(self, surface, camera, visible=True):
        if not visible: return
        img, r = self._rotated_image_and_rect()
        r.center = camera.apply_point(r.centerx, r.centery)
        surface.blit(img, r)
