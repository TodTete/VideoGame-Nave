import pygame, random, math
from .. import assets as Assets
from ..constants import ANCHO, ALTO, BOSS_W, BOSS_H

class Boss:
    """
    Ataques:
      0 = aimed shot (dirigidas)
      1 = spread (abanico)
      2 = wave (sinusoidal)
      3 = burst (ráfagas)
      4 = laser (telegrafiado)
    """
    def __init__(self, level, difficulty_hp_mul=1.0):
        self.level = level
        planet_id = getattr(level, "planet_id", level if isinstance(level, int) else 1)
        try:
            frames, durs = Assets.cargar_boss_por_planeta(planet_id)
            self.frames = frames
            self.frame_durations = durs
            self.image = self.frames[0]
            self.current_frame = 0
            print(f"[INFO] Boss actualizado para planeta {planet_id}")
        except Exception as e:
            print(f"[ERROR] No se pudo cargar el boss para planeta {planet_id}: {e}")
        self.w, self.h = BOSS_W, BOSS_H
        self.rect = pygame.Rect(ANCHO//2 - self.w//2, 60, self.w, self.h)
        base_hp = 160 + (level-1)*80
        self.hp_max = int(base_hp * difficulty_hp_mul)
        self.hp = self.hp_max
        self.move_speed = 2.2 + (level-1)*0.6
        self.dir = 1

        self.anim_idx = 0; self.anim_accum = 0

        self.fire_cd_ms = max(350, 900 - (level-1)*120)
        self.last_pattern_change = 0
        self.pattern_duration = 2400
        self.attack_mode = 0
        self.last_shot = 0
        self.cannons = [0.2, 0.5, 0.8]

        self.laser_active=False
        self.laser_rect=None
        self.laser_warn_ms=700
        self.laser_fire_ms=600
        self.laser_start_t=0
        self.laser_x = ANCHO//2

    def _shoot(self, boss_bullets, x, y, vx, vy, tipo="normal", w=10, h=18):
        boss_bullets.append({"rect": pygame.Rect(int(x-w/2), int(y), w, h),
                             "vx": vx, "vy": vy, "type": tipo})

    def _aim_to_player(self, player_rect, speed):
        px, py = player_rect.centerx, player_rect.centery
        bx, by = self.rect.centerx, self.rect.bottom
        dx, dy = (px - bx), (py - by)
        mag = math.hypot(dx, dy) or 1.0
        return (dx/mag)*speed, (dy/mag)*speed

    def _pattern_aimed(self, ahora, player_rect, boss_bullets):
        if ahora - self.last_shot >= self.fire_cd_ms:
            self.last_shot = ahora
            vx, vy = self._aim_to_player(player_rect, 5.5 + self.level*0.3)
            for rel in self.cannons:
                cx = int(self.rect.left + self.w * rel)
                cy = self.rect.bottom - 6
                self._shoot(boss_bullets, cx, cy, vx, vy, "aim")

    def _pattern_spread(self, ahora, boss_bullets):
        if ahora - self.last_shot >= self.fire_cd_ms + 150:
            self.last_shot = ahora
            base_speed = 5.2 + self.level*0.2
            angles = [-25, -12, 0, 12, 25]
            rad = math.pi/180
            for rel in self.cannons:
                cx = int(self.rect.left + self.w * rel)
                cy = self.rect.bottom - 6
                for ang in angles:
                    vx = base_speed * math.sin(ang*rad)
                    vy = base_speed * math.cos(ang*rad)
                    self._shoot(boss_bullets, cx, cy, vx, vy, "spread")

    def _pattern_wave(self, ahora, boss_bullets):
        if ahora - self.last_shot >= self.fire_cd_ms + 200:
            self.last_shot = ahora
            base_vy = 3.8 + self.level*0.25
            for i in range(6):
                cx = self.rect.left + 20 + i*(self.w-40)/5
                cy = self.rect.bottom - 8
                phase = random.uniform(0, math.pi*2)
                boss_bullets.append({
                    "rect": pygame.Rect(int(cx-5), int(cy), 10, 18),
                    "vx": 0.0, "vy": base_vy,
                    "type": "wave", "phase": phase, "phase_speed": 0.11 + random.random()*0.09
                })

    def _pattern_burst(self, ahora, boss_bullets):
        if ahora - self.last_shot >= 110:
            self.last_shot = ahora
            base_speed = 6.2 + self.level*0.25
            for rel in self.cannons:
                cx = int(self.rect.left + self.w * rel)
                cy = self.rect.bottom - 6
                ang = random.uniform(-10,10) * math.pi/180
                vx = base_speed * math.sin(ang); vy = base_speed * math.cos(ang)
                self._shoot(boss_bullets, cx, cy, vx, vy, "burst")

    def _pattern_laser(self, ahora, boss_bullets):
        if not self.laser_active:
            self.laser_active=True; self.laser_start_t=ahora
            self.laser_x = random.randint(60, ANCHO-60)
            self.laser_rect = pygame.Rect(self.laser_x-8, self.rect.bottom, 16, ALTO - self.rect.bottom)
        else:
            elapsed = ahora - self.laser_start_t
            if elapsed >= self.laser_warn_ms + self.laser_fire_ms:
                self.laser_active=False; self.laser_rect=None

    def update(self, dt, ahora, player_rect, boss_bullets):
        self.rect.x += int(self.move_speed) * self.dir
        if self.rect.right >= ANCHO - 10: self.rect.right = ANCHO - 10; self.dir = -1
        elif self.rect.left <= 10: self.rect.left = 10; self.dir = 1

        if ahora - self.last_pattern_change >= self.pattern_duration:
            self.last_pattern_change = ahora
            self.attack_mode = (self.attack_mode + 1) % 5
            self.laser_active=False; self.laser_rect=None

        if   self.attack_mode == 0: self._pattern_aimed(ahora, player_rect, boss_bullets)
        elif self.attack_mode == 1: self._pattern_spread(ahora, boss_bullets)
        elif self.attack_mode == 2: self._pattern_wave(ahora, boss_bullets)
        elif self.attack_mode == 3: self._pattern_burst(ahora, boss_bullets)
        elif self.attack_mode == 4: self._pattern_laser(ahora, boss_bullets)

        self.anim_accum += dt
        if self.anim_accum >= self.frame_durations[self.anim_idx]:
            self.anim_accum = 0
            self.anim_idx = (self.anim_idx + 1) % len(self.frames)


    def draw(self, surface, cam_apply_rect, ahora):
        frame = self.frames[self.anim_idx]
        drect = cam_apply_rect(self.rect)
        surface.blit(frame, drect.topleft)

        # Vida
        bar_w, bar_h = self.w, 10
        bar_x, bar_y = drect.left, drect.top - 16
        pygame.draw.rect(surface, (90,90,90), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        pct = max(0.0, self.hp / self.hp_max)
        pygame.draw.rect(surface, (255,60,60), (bar_x, bar_y, int(bar_w*pct), bar_h), border_radius=6)

        # Láser
        if self.attack_mode == 4 and self.laser_active and self.laser_rect:
            elapsed = pygame.time.get_ticks() - self.laser_start_t
            draw_rect = cam_apply_rect(self.laser_rect)
            if elapsed < self.laser_warn_ms:
                alpha = 120 if (elapsed // 100) % 2 == 0 else 60
                s = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
                s.fill((255,50,50,alpha)); surface.blit(s, draw_rect.topleft)
            else:
                s = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
                s.fill((255,0,0,200)); surface.blit(s, draw_rect.topleft)
