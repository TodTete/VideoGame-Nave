import pygame, random, math
from ..constants import ALTO, ANCHO, VERDE, AMARILLO, MORADO

class PowerUp:
    def __init__(self, tipo, x, y):
        self.tipo = tipo
        self.rect = pygame.Rect(x-12, y-12, 24, 24)
        self.speed = 3.0

    def update(self):
        self.rect.y += self.speed
        return self.rect.top <= ALTO

    def draw(self, surface, fuente, cam_apply_rect, cam_apply_point, dibujar_texto, NEGRO):
        color = VERDE if self.tipo=='S' else AMARILLO if self.tipo=='F' else MORADO
        pygame.draw.rect(surface, color, cam_apply_rect(self.rect), border_radius=6)
        cx, cy = cam_apply_point(self.rect.centerx, self.rect.centery-10)
        dibujar_texto(surface, self.tipo, fuente, NEGRO, cx, cy, centrado=True)

class BombPickup:
    LIFETIME_MS = 7000
    def __init__(self, x, y, now_ms):
        self.rect = pygame.Rect(x-14, y-14, 28, 28)
        self.vy=1.6; self.phase = random.uniform(0,math.pi*2)
        self.active=True; self.spawn_time = now_ms

    def update(self, ahora):
        if not self.active: return
        self.phase += 0.06
        self.rect.y += self.vy
        self.rect.x += int(2.0 * math.sin(self.phase))
        if self.rect.top > ALTO or (ahora - self.spawn_time) > self.LIFETIME_MS:
            self.active=False

    def draw(self, surface, cam_apply_rect):
        if not self.active: return
        r = cam_apply_rect(self.rect)
        pygame.draw.circle(surface, (255,230,60), r.center, r.width//2)
        pygame.draw.circle(surface, (150,120,0), r.center, r.width//2, 2)
        pygame.draw.circle(surface, (255,255,255), r.center, 3)

class BombProjectile:
    EXPLOSION_MS = 700
    def __init__(self, x, y, target_rect, reproducir, sonido_explosion):
        import math
        self.rect = pygame.Rect(x-12, y-12, 24, 24)
        tx, ty = target_rect.centerx, target_rect.centery
        dx, dy = (tx - x), (ty - y)
        mag = math.hypot(dx, dy) or 1.0; speed = 6.0
        self.vx = dx/mag*speed; self.vy = dy/mag*speed
        self.active=True; self.exploded=False; self.explosion_start=0; self.radius=18
        self._reproducir = reproducir; self._sonido_explosion = sonido_explosion

    def update(self, ahora, boss):
        import math
        if not self.active: return
        if not self.exploded:
            self.rect.x += int(self.vx); self.rect.y += int(self.vy)
            if (self.rect.bottom < 0 or self.rect.top > ALTO or 
                self.rect.right < 0 or self.rect.left > ANCHO):
                self.active=False
            elif boss and self.rect.colliderect(boss.rect):
                self.trigger(ahora)
                boss.hp -= int(boss.hp_max * 0.45)
        else:
            t = ahora - self.explosion_start
            self.radius = 18 + int(180 * min(1.0, t/self.EXPLOSION_MS))
            if t >= self.EXPLOSION_MS: self.active=False

    def trigger(self, ahora):
        if not self.exploded:
            self.exploded=True; self.explosion_start=ahora
            self._reproducir(self._sonido_explosion)

    def draw(self, surface, cam_apply_rect, cam_apply_point):
        if not self.active: return
        if not self.exploded:
            r = cam_apply_rect(self.rect)
            pygame.draw.circle(surface, (255,160,0), r.center, r.width//2)
            pygame.draw.circle(surface, (100,60,0), r.center, r.width//2, 2)
            pygame.draw.circle(surface, (255,255,255), r.center, 4)
        else:
            cx, cy = cam_apply_point(self.rect.centerx, self.rect.centery)
            pygame.draw.circle(surface, (255,120,0), (cx,cy), self.radius, 6)
