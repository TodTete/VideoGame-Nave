from .. import assets as Assets
from ..constants import PLAYER_W, PLAYER_H, ALTO, ANCHO
import pygame

class Jugador:
    def __init__(self, centerx, bottom):
        self.w, self.h = PLAYER_W, PLAYER_H
        self.rect = pygame.Rect(0,0,self.w,self.h)
        self.rect.centerx = centerx; self.rect.bottom = bottom

        self.anim_idx = 0; self.anim_accum = 0
        self.vel_base = 6; self.vel = self.vel_base
        self.angle = 0.0; self.target_angle = 0.0
        self.ANGLE_MAX = 22.0; self.ANGLE_SPEED = 240.0

        self.nose_local = (self.w/2, 6)        
        self.frames = Assets.PLAYER_FRAMES
        self.durations = Assets.PLAYER_DURS
        self.frame_index = 0
        self.frame_timer = 0

    def get_muzzle_world(self):
        from pygame.math import Vector2
        base_center = Vector2(self.w/2, self.h/2)
        nose = Vector2(self.nose_local)
        offset = nose - base_center
        spawn = Vector2(self.rect.center) + offset.rotate(-self.angle)
        return int(spawn.x), int(spawn.y)

    def update(self, dt_ms, keys):
        dx=dy=0
        if keys[pygame.K_LEFT]:  dx -= self.vel
        if keys[pygame.K_RIGHT]: dx += self.vel
        if keys[pygame.K_UP]:    dy -= self.vel
        if keys[pygame.K_DOWN]:  dy += self.vel
        self.rect.move_ip(dx,dy)
        self.rect.clamp_ip(pygame.Rect(0,0,ANCHO,ALTO))

        if dx>0: self.target_angle = +self.ANGLE_MAX
        elif dx<0: self.target_angle = -self.ANGLE_MAX
        else: self.target_angle = 0.0

        max_delta = self.ANGLE_SPEED * (dt_ms/1000.0)
        if self.angle < self.target_angle:
            self.angle = min(self.angle+max_delta, self.target_angle)
        elif self.angle > self.target_angle:
            self.angle = max(self.angle-max_delta, self.target_angle)

        self.anim_accum += dt_ms
        if self.anim_accum >= Assets.PLAYER_DURS[self.anim_idx]:
            self.anim_accum = 0
            self.anim_idx = (self.anim_idx + 1) % len(Assets.PLAYER_FRAMES)    # Animación de la nave
        if len(self.frames) > 1:
            self.frame_timer += dt
            if self.frame_timer >= self.durations[self.frame_index]:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, surface, cam_apply_point, visible=True):
        if not visible: return
        frame = Assets.PLAYER_FRAMES[self.anim_idx]
        rotated = pygame.transform.rotozoom(frame, -self.angle, 1.0)
        rrect = rotated.get_rect(center=self.rect.center)
        rrect.center = cam_apply_point(rrect.centerx, rrect.centery)
        surface.blit(rotated, rrect)