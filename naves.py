import pygame
import random
import sys
import os
import math

# ======= GIF loader (Pillow) =======
try:
    from PIL import Image
    PIL_OK = True
except Exception as e:
    print("[AVISO] Pillow no disponible, los GIF se verán estáticos:", e)
    PIL_OK = False

# =========================
# Configuración / Constantes
# =========================
ANCHO, ALTO = 800, 600
FPS = 60

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO   = (255, 0, 0)
AZUL   = (0, 120, 255)
AMARILLO = (255, 215, 0)
VERDE = (0, 200, 120)
MORADO = (170, 120, 255)
GRIS = (40, 40, 50)

# Estados de juego
MENU = "MENU"
LEVEL_INTRO = "LEVEL_INTRO"
BOSS_INTRO = "BOSS_INTRO"
JUGANDO = "JUGANDO"
PAUSA = "PAUSA"
GAME_OVER = "GAME_OVER"

# Umbral para jefe por nivel
BOSS_POINTS_PER_LEVEL = 250

# Duraciones
LEVEL_INTRO_MS = 1500
BOSS_INTRO_MS = 1200

# =========================
# Utilidades
# =========================
def cargar_sonido(ruta, volumen=0.5):
    try:
        s = pygame.mixer.Sound(ruta)
        s.set_volume(volumen)
        return s
    except Exception as e:
        print(f"[AVISO] No se pudo cargar el sonido '{ruta}': {e}")
        return None

def reproducir(sonido):
    if sonido:
        sonido.play()

def dibujar_texto(superficie, texto, fuente, color, x, y, centrado=False):
    img = fuente.render(texto, True, color)
    rect = img.get_rect()
    if centrado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    superficie.blit(img, rect)

def leer_hiscore(ruta="hiscore.txt"):
    try:
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                return int(f.read().strip() or 0)
    except Exception:
        pass
    return 0

def guardar_hiscore(puntos, ruta="hiscore.txt"):
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(str(puntos))
    except Exception as e:
        print(f"[AVISO] No se pudo guardar hiscore: {e}")

# ======= GIF: carga compuesta (flatten) =======
def load_gif_frames(path, size=(ANCHO, ALTO)):
    """
    Carga un GIF animado como lista de Surfaces de Pygame (con alpha).
    Compone cada frame sobre un lienzo RGBA completo para evitar parches negros.
    Respeta duración por frame.
    """
    frames = []
    durations = []

    if not PIL_OK:
        # Sin Pillow: intenta imagen estática
        try:
            img = pygame.image.load(path).convert_alpha()
            if size is not None:
                img = pygame.transform.smoothscale(img, size)
            frames = [img]
            durations = [120]
        except Exception as e:
            print(f"[AVISO] No se pudo cargar '{path}': {e}")
            surf = pygame.Surface(size, pygame.SRCALPHA)
            surf.fill((5, 5, 15, 255))
            frames, durations = [surf], [120]
        return frames, durations

    try:
        im = Image.open(path)

        # Aseguramos RGBA para componer
        frame_count = getattr(im, "n_frames", 1)
        canvas_size = im.size
        prev = Image.new("RGBA", canvas_size, (0, 0, 0, 0))

        for i in range(frame_count):
            im.seek(i)
            # Duración (ms), mínimo razonable
            dur = max(20, int(im.info.get("duration", 100)))

            # Frame actual a RGBA
            curr = im.convert("RGBA")

            # Componer sobre acumulado
            composed = prev.copy()
            composed.alpha_composite(curr, dest=(0, 0))

            # Manejo simple de "disposal": 2 => restaurar a fondo (transparente)
            disposal = getattr(im, "disposal", im.info.get("disposal", 0))
            if disposal == 2:
                next_prev = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
                next_prev.alpha_composite(prev, dest=(0, 0))
            else:
                next_prev = composed

            # Escalar si procede
            out_img = composed
            if size is not None and size != canvas_size:
                out_img = composed.resize(size, Image.LANCZOS)

            data = out_img.tobytes()
            py_img = pygame.image.fromstring(data, out_img.size, "RGBA").convert_alpha()

            frames.append(py_img)
            durations.append(dur)

            prev = next_prev

        if not frames:
            raise ValueError("GIF sin frames")

        return frames, durations

    except Exception as e:
        print(f"[AVISO] Error cargando GIF '{path}': {e}")
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((5, 5, 15, 255))
        return [surf], [120]

# ======= Asteroide animado (enemigos que caen) =======
ASTEROID_W, ASTEROID_H = 40, 40
def _cargar_asteroid_frames():
    for ruta in ("assets/asteroides.gif",):
        frames, durs = load_gif_frames(ruta, size=(ASTEROID_W, ASTEROID_H))
        if frames and len(frames) >= 1:
            print(f"[INFO] Asteroides cargados desde: {ruta} ({len(frames)} frames)")
            return frames, durs
    print("[AVISO] No se encontró 'asteroides.gif'. Se usará un placeholder.")
    surf = pygame.Surface((ASTEROID_W, ASTEROID_H), pygame.SRCALPHA)
    surf.fill((200, 80, 80, 180))
    return [surf], [120]

# ======= Nave y Jefe: GIFs =======
PLAYER_W, PLAYER_H = 60, 60
BOSS_W, BOSS_H = 220, 100

def _cargar_player_frames():
    for ruta in ("assets/nave.gif",):
        frames, durs = load_gif_frames(ruta, size=(PLAYER_W, PLAYER_H))
        if frames:
            print(f"[INFO] Nave cargada desde: {ruta} ({len(frames)} frames)")
            return frames, durs
    print("[AVISO] No se encontró 'nave.gif'. Se usará un placeholder.")
    surf = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (30, 120, 240),
                        [(PLAYER_W//2, 4), (10, PLAYER_H-6), (PLAYER_W-10, PLAYER_H-6)])
    return [surf], [120]

def _cargar_boss_frames():
    for ruta in ("assets/jefe.gif",):
        frames, durs = load_gif_frames(ruta, size=(BOSS_W, BOSS_H))
        if frames:
            print(f"[INFO] Jefe cargado desde: {ruta} ({len(frames)} frames)")
            return frames, durs
    print("[AVISO] No se encontró 'jefe.gif'. Se usará un placeholder.")
    surf = pygame.Surface((BOSS_W, BOSS_H), pygame.SRCALPHA)
    pygame.draw.rect(surf, (140,25,25), (0,0,BOSS_W,BOSS_H), border_radius=16)
    return [surf], [120]

# ======= Bala (imagen) =======
def cargar_imagen_bala():
    try:
        img = pygame.image.load("assets/bala.png").convert_alpha()
        # tamaño recomendado para que encaje con el juego:
        img = pygame.transform.smoothscale(img, (8, 18))
        return img
    except Exception as e:
        print(f"[AVISO] No se pudo cargar 'assets/bala.png': {e}")
        ph = pygame.Surface((8, 18), pygame.SRCALPHA)
        pygame.draw.rect(ph, (255,255,255), ph.get_rect(), border_radius=3)
        return ph

# Deferimos la carga hasta después de set_mode
ASTEROID_FRAMES, ASTEROID_DURS = None, None
PLAYER_FRAMES, PLAYER_DURS = None, None
BOSS_FRAMES, BOSS_DURS = None, None
BALA_IMG = None

class AnimatedBackground:
    def __init__(self, path_main="assets/fondo.gif", path_boss="assets/fondo-gf.gif"):
        self.frames_a, self.durs_a = load_gif_frames(path_main, size=(ANCHO, ALTO))
        self.frames_b, self.durs_b = load_gif_frames(path_boss, size=(ANCHO, ALTO))
        self.use_b = False
        self.idx_a = 0
        self.idx_b = 0
        self.t_accum_a = 0
        self.t_accum_b = 0
        self.transition = False
        self.transition_time = 0.0
        self.transition_duration = 1200
        self.alpha = 0

    def switch_to_boss(self):
        if not self.transition and not self.use_b:
            self.transition = True
            self.transition_time = 0.0
            self.alpha = 0

    def switch_to_main(self):
        if not self.transition and self.use_b:
            self.transition = True
            self.transition_time = 0.0
            self.alpha = 0

    def update(self, dt):
        self.t_accum_a += dt
        if self.t_accum_a >= self.durs_a[self.idx_a]:
            self.t_accum_a = 0
            self.idx_a = (self.idx_a + 1) % len(self.frames_a)

        self.t_accum_b += dt
        if self.t_accum_b >= self.durs_b[self.idx_b]:
            self.t_accum_b = 0
            self.idx_b = (self.idx_b + 1) % len(self.frames_b)

        if self.transition:
            self.transition_time += dt
            self.alpha = int(255 * min(1.0, self.transition_time / self.transition_duration))
            if self.transition_time >= self.transition_duration:
                self.transition = False
                self.use_b = not self.use_b
                self.alpha = 255

    def draw(self, surface):
        if not self.transition:
            if self.use_b:
                surface.blit(self.frames_b[self.idx_b], (0, 0))
            else:
                surface.blit(self.frames_a[self.idx_a], (0, 0))
        else:
            if not self.use_b:
                img_a = self.frames_a[self.idx_a]
                img_b = self.frames_b[self.idx_b].copy()
                img_b.set_alpha(self.alpha)
                surface.blit(img_a, (0, 0))
                surface.blit(img_b, (0, 0))
            else:
                img_b = self.frames_b[self.idx_b]
                img_a = self.frames_a[self.idx_a].copy()
                img_a.set_alpha(self.alpha)
                surface.blit(img_b, (0, 0))
                surface.blit(img_a, (0, 0))

# =========================
# Inicialización
# =========================
pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("[AVISO] Audio deshabilitado:", e)

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Game Nave")
print(f"[INFO] PIL_OK={PIL_OK}")

clock = pygame.time.Clock()
fuente = pygame.font.SysFont("Arial", 24)
fuente_grande = pygame.font.SysFont("Arial", 48, bold=True)
fuente_titulo = pygame.font.SysFont("Arial", 56, bold=True)

# GIFs (tras set_mode)
if ASTEROID_FRAMES is None: ASTEROID_FRAMES, ASTEROID_DURS = _cargar_asteroid_frames()
if PLAYER_FRAMES is None:   PLAYER_FRAMES, PLAYER_DURS   = _cargar_player_frames()
if BOSS_FRAMES is None:     BOSS_FRAMES, BOSS_DURS       = _cargar_boss_frames()
if BALA_IMG is None:        BALA_IMG = cargar_imagen_bala()

# Sonidos (opcionales)
sonido_inicio   = cargar_sonido("assets/game-start-317318.mp3", 0.6)
sonido_gameover = cargar_sonido("assets/game-over-381772.mp3", 0.6)
sonido_disparo  = cargar_sonido("assets/laser-shot-ingame-230500.mp3", 0.4)
sonido_explosion= cargar_sonido("assets/wood-crate-destory-2-97263.mp3", 0.55)
sonido_boss     = cargar_sonido("assets/boss.mp3", 0.11)
sonido_power    = cargar_sonido("assets/powerup.mp3", 0.6)

reproducir(sonido_inicio)

# Fondo animado
bg = AnimatedBackground("assets/fondo.gif", "assets/fondo-gf.gif")

# =========================
# Cámara (paneo suave en X e Y)
# =========================
CAM_LERP   = 0.12
CAM_FACTOR = 0.35
CAM_MAX    = 120
cam_x, cam_y = 0.0, 0.0

def cam_target(player_rect):
    tx = (ANCHO/2 - player_rect.centerx) * CAM_FACTOR
    ty = (ALTO/2  - player_rect.centery) * CAM_FACTOR
    tx = max(-CAM_MAX, min(CAM_MAX, tx))
    ty = max(-CAM_MAX, min(CAM_MAX, ty))
    return tx, ty

def cam_apply_point(x, y):
    return int(x + cam_x), int(y + cam_y)

def cam_apply_rect(r):
    return pygame.Rect(r.left + int(cam_x), r.top + int(cam_y), r.width, r.height)

# =========================
# Clase Bala (usa imagen)
# =========================
class Bala:
    def __init__(self, x, y, vy=-9):
        self.image = BALA_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = 0
        self.vy = vy

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        # True si sigue en pantalla
        return self.rect.bottom > 0 and self.rect.top < ALTO and self.rect.right > 0 and self.rect.left < ANCHO

    def draw(self, surface):
        drect = cam_apply_rect(self.rect)
        surface.blit(self.image, drect.topleft)

# =========================
# Clase Jugador (usa GIF)
# =========================
class Jugador:
    def __init__(self, centerx, bottom):
        self.w = PLAYER_W
        self.h = PLAYER_H
        self.rect = pygame.Rect(0, 0, self.w, self.h)
        self.rect.centerx = centerx
        self.rect.bottom = bottom

        # Animación
        self.anim_idx = 0
        self.anim_accum = 0  # ms

        # Movimiento/tilt
        self.vel_base = 6
        self.vel = self.vel_base
        self.angle = 0.0
        self.target_angle = 0.0
        self.ANGLE_MAX = 22.0
        self.ANGLE_SPEED = 240.0

        # Punto de la “nariz” para disparo (parte superior central)
        self.nose_local = (self.w/2, 6)

    def get_muzzle_world(self):
        from pygame.math import Vector2
        base_center = Vector2(self.w/2, self.h/2)
        nose = Vector2(self.nose_local)
        offset = nose - base_center
        spawn = Vector2(self.rect.center) + offset.rotate(-self.angle)
        return int(spawn.x), int(spawn.y)

    def update(self, dt_ms, keys, bounds_rect):
        # Movimiento
        dx = 0; dy = 0
        if keys[pygame.K_LEFT]:  dx -= self.vel
        if keys[pygame.K_RIGHT]: dx += self.vel
        if keys[pygame.K_UP]:    dy -= self.vel
        if keys[pygame.K_DOWN]:  dy += self.vel
        self.rect.move_ip(dx, dy)
        self.rect.clamp_ip(bounds_rect)

        # Tilt objetivo
        if dx > 0:   self.target_angle = +self.ANGLE_MAX
        elif dx < 0: self.target_angle = -self.ANGLE_MAX
        else:        self.target_angle = 0.0

        # Interpolar ángulo
        max_delta = self.ANGLE_SPEED * (dt_ms / 1000.0)
        if self.angle < self.target_angle:
            self.angle = min(self.angle + max_delta, self.target_angle)
        elif self.angle > self.target_angle:
            self.angle = max(self.angle - max_delta, self.target_angle)

        # Animación
        self.anim_accum += dt_ms
        if self.anim_accum >= PLAYER_DURS[self.anim_idx]:
            self.anim_accum = 0
            self.anim_idx = (self.anim_idx + 1) % len(PLAYER_FRAMES)

    def draw(self, surface, visible=True):
        if not visible: return
        frame = PLAYER_FRAMES[self.anim_idx]
        # Rotación suave del frame actual
        rotated = pygame.transform.rotozoom(frame, -self.angle, 1.0)
        rrect = rotated.get_rect(center=self.rect.center)
        rrect.center = cam_apply_point(rrect.centerx, rrect.centery)
        surface.blit(rotated, rrect)

# =========================
# Boss y balas (jefe con GIF)
# =========================
class Boss:
    """
    Ataques:
      0 = aimed shot (dirigidas)
      1 = spread (abanico)
      2 = wave (sinusoidal)
      3 = burst (ráfagas rápidas)
      4 = laser (telegráfiado)
    """
    def __init__(self, level):
        self.level = level
        self.w = BOSS_W
        self.h = BOSS_H
        self.rect = pygame.Rect(ANCHO//2 - self.w//2, 60, self.w, self.h)
        self.hp_max = 160 + (level-1)*80
        self.hp = self.hp_max
        self.move_speed = 2.2 + (level-1)*0.6
        self.dir = 1

        # Animación
        self.anim_idx = 0
        self.anim_accum = 0

        # Disparo/patrones
        self.fire_cd_ms = max(350, 900 - (level-1)*120)
        self.last_pattern_change = 0
        self.pattern_duration = 2400
        self.attack_mode = 0
        self.last_shot = 0
        self.cannons = [0.2, 0.5, 0.8]

        # Laser
        self.laser_active = False
        self.laser_rect = None
        self.laser_warn_ms = 700
        self.laser_fire_ms = 600
        self.laser_start_t = 0
        self.laser_x = ANCHO//2

    def _shoot(self, boss_bullets, x, y, vx, vy, tipo="normal", w=10, h=18):
        boss_bullets.append({
            "rect": pygame.Rect(int(x-w/2), int(y), w, h),
            "vx": vx, "vy": vy, "type": tipo
        })

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
                cx = self.rect.left + 20 + i* (self.w-40)/5
                cy = self.rect.bottom - 8
                phase = random.uniform(0, math.pi*2)
                boss_bullets.append({
                    "rect": pygame.Rect(int(cx-5), int(cy), 10, 18),
                    "vx": 0.0, "vy": base_vy,
                    "type": "wave",
                    "phase": phase, "phase_speed": 0.11 + random.random()*0.09
                })

    def _pattern_burst(self, ahora, boss_bullets):
        if ahora - self.last_shot >= 110:
            self.last_shot = ahora
            base_speed = 6.2 + self.level*0.25
            for rel in self.cannons:
                cx = int(self.rect.left + self.w * rel)
                cy = self.rect.bottom - 6
                ang = random.uniform(-10, 10) * math.pi / 180
                vx = base_speed * math.sin(ang)
                vy = base_speed * math.cos(ang)
                self._shoot(boss_bullets, cx, cy, vx, vy, "burst")

    def _pattern_laser(self, ahora, boss_bullets):
        if not self.laser_active:
            self.laser_active = True
            self.laser_start_t = ahora
            self.laser_x = random.randint(60, ANCHO-60)
            self.laser_rect = pygame.Rect(self.laser_x-8, self.rect.bottom, 16, ALTO - self.rect.bottom)
        else:
            elapsed = ahora - self.laser_start_t
            if elapsed >= self.laser_warn_ms + self.laser_fire_ms:
                self.laser_active = False
                self.laser_rect = None

    def update(self, dt, ahora, player_rect, boss_bullets):
        # Movimiento lateral
        self.rect.x += int(self.move_speed) * self.dir
        if self.rect.right >= ANCHO - 10:
            self.rect.right = ANCHO - 10
            self.dir = -1
        elif self.rect.left <= 10:
            self.rect.left = 10
            self.dir = 1

        # Cambios de patrón
        if ahora - self.last_pattern_change >= self.pattern_duration:
            self.last_pattern_change = ahora
            self.attack_mode = (self.attack_mode + 1) % 5
            self.laser_active = False
            self.laser_rect = None

        # Disparos según patrón
        if self.attack_mode == 0:
            self._pattern_aimed(ahora, player_rect, boss_bullets)
        elif self.attack_mode == 1:
            self._pattern_spread(ahora, boss_bullets)
        elif self.attack_mode == 2:
            self._pattern_wave(ahora, boss_bullets)
        elif self.attack_mode == 3:
            self._pattern_burst(ahora, boss_bullets)
        elif self.attack_mode == 4:
            self._pattern_laser(ahora, boss_bullets)

        # Animación
        self.anim_accum += dt
        if self.anim_accum >= BOSS_DURS[self.anim_idx]:
            self.anim_accum = 0
            self.anim_idx = (self.anim_idx + 1) % len(BOSS_FRAMES)

    def draw(self, surface, ahora):
        # Sprite
        frame = BOSS_FRAMES[self.anim_idx]
        drect = cam_apply_rect(self.rect)
        surface.blit(frame, drect.topleft)

        # Vida
        bar_w = self.w
        bar_h = 10
        bar_x = drect.left
        bar_y = drect.top - 16
        pygame.draw.rect(surface, (90, 90, 90), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        pct = max(0.0, self.hp / self.hp_max)
        pygame.draw.rect(surface, (255, 60, 60), (bar_x, bar_y, int(bar_w * pct), bar_h), border_radius=6)

        # Láser
        if self.attack_mode == 4 and self.laser_active and self.laser_rect:
            elapsed = pygame.time.get_ticks() - self.laser_start_t
            draw_rect = cam_apply_rect(self.laser_rect)
            if elapsed < self.laser_warn_ms:
                alpha = 120 if (elapsed // 100) % 2 == 0 else 60
                s = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
                s.fill((255, 50, 50, alpha))
                surface.blit(s, draw_rect.topleft)
            else:
                s = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
                s.fill((255, 0, 0, 200))
                surface.blit(s, draw_rect.topleft)

# =========================
# PowerUps comunes
# =========================
class PowerUp:
    def __init__(self, tipo, x, y):
        self.tipo = tipo  # 'S', 'F', 'P'
        self.rect = pygame.Rect(x-12, y-12, 24, 24)
        self.speed = 3.0

    def update(self):
        self.rect.y += self.speed
        return self.rect.top <= ALTO

    def draw(self, surface, fuente):
        color = VERDE if self.tipo == 'S' else AMARILLO if self.tipo == 'F' else MORADO
        pygame.draw.rect(surface, color, cam_apply_rect(self.rect), border_radius=6)
        cx, cy = cam_apply_point(self.rect.centerx, self.rect.centery-10)
        dibujar_texto(surface, self.tipo, fuente, NEGRO, cx, cy, centrado=True)

# =========================
# Bomba PowerUp
# =========================
class BombPickup:
    LIFETIME_MS = 7000
    def __init__(self, x, y, now_ms):
        self.rect = pygame.Rect(x-14, y-14, 28, 28)
        self.vy = 1.6
        self.phase = random.uniform(0, math.pi*2)
        self.active = True
        self.spawn_time = now_ms

    def update(self, ahora):
        if not self.active: return
        self.phase += 0.06
        self.rect.y += self.vy
        self.rect.x += int(2.0 * math.sin(self.phase))
        if self.rect.top > ALTO or (ahora - self.spawn_time) > self.LIFETIME_MS:
            self.active = False

    def draw(self, surface):
        if not self.active: return
        r = cam_apply_rect(self.rect)
        pygame.draw.circle(surface, (255, 230, 60), r.center, r.width//2)
        pygame.draw.circle(surface, (150, 120, 0), r.center, r.width//2, 2)
        pygame.draw.circle(surface, (255,255,255), r.center, 3)

# =========================
# Bomba proyectil
# =========================
class BombProjectile:
    EXPLOSION_MS = 700
    def __init__(self, x, y, target_rect):
        self.rect = pygame.Rect(x-12, y-12, 24, 24)
        tx, ty = target_rect.centerx, target_rect.centery
        dx, dy = (tx - x), (ty - y)
        mag = math.hypot(dx, dy) or 1.0
        speed = 6.0
        self.vx = dx / mag * speed
        self.vy = dy / mag * speed
        self.active = True
        self.exploded = False
        self.explosion_start = 0
        self.radius = 18

    def update(self, ahora, boss):
        if not self.active: return
        if not self.exploded:
            self.rect.x += int(self.vx)
            self.rect.y += int(self.vy)
            if self.rect.bottom < 0 or self.rect.top > ALTO or self.rect.right < 0 or self.rect.left > ANCHO:
                self.active = False
            elif boss and self.rect.colliderect(boss.rect):
                self.trigger(ahora)
                boss.hp -= int(boss.hp_max * 0.45)
        else:
            t = ahora - self.explosion_start
            self.radius = 18 + int(180 * min(1.0, t / self.EXPLOSION_MS))
            if t >= self.EXPLOSION_MS:
                self.active = False

    def trigger(self, ahora):
        if not self.exploded:
            self.exploded = True
            self.explosion_start = ahora
            reproducir(sonido_explosion)

    def draw(self, surface):
        if not self.active: return
        if not self.exploded:
            r = cam_apply_rect(self.rect)
            pygame.draw.circle(surface, (255,160,0), r.center, r.width//2)
            pygame.draw.circle(surface, (100,60,0), r.center, r.width//2, 2)
            pygame.draw.circle(surface, (255,255,255), r.center, 4)
        else:
            cx, cy = cam_apply_point(self.rect.centerx, self.rect.centery)
            pygame.draw.circle(surface, (255,120,0), (cx, cy), self.radius, 6)

# =========================
# Enemigos (asteroides animados)
# =========================
class FallingEnemy:
    def __init__(self, x, y, w=ASTEROID_W, h=ASTEROID_H):
        self.rect = pygame.Rect(x, y, w, h)
        self.anim_idx = 0
        self.anim_accum = 0  # ms

    def update(self, dt_ms, vel_y):
        self.rect.y += vel_y
        self.anim_accum += dt_ms
        if self.anim_accum >= ASTEROID_DURS[self.anim_idx]:
            self.anim_accum = 0
            self.anim_idx = (self.anim_idx + 1) % len(ASTEROID_FRAMES)

    def draw(self, surface):
        drect = cam_apply_rect(self.rect)
        surface.blit(ASTEROID_FRAMES[self.anim_idx], drect.topleft)

def crear_enemigos(cantidad):
    enemigos = []
    for _ in range(cantidad):
        x = random.randint(0, ANCHO - ASTEROID_W)
        y = random.randint(-250, -ASTEROID_H)
        enemigos.append(FallingEnemy(x, y))
    return enemigos

def respawnear_enemigo(enemigo: 'FallingEnemy'):
    enemigo.rect.x = random.randint(0, ANCHO - enemigo.rect.width)
    enemigo.rect.y = random.randint(-200, -enemigo.rect.height)
    enemigo.anim_idx = 0
    enemigo.anim_accum = 0

# =========================
# Variables de juego / reset
# =========================
def reset_juego():
    player = Jugador(ANCHO//2, ALTO - 10)
    balas = []  # Lista de objetos Bala
    vel_bala = -9  # se sigue usando para consistencia (Bala usa -9 por defecto)
    cadencia_ms = 200
    ultimo_disparo = 0

    enemigos = crear_enemigos(6)
    vel_enemigo_base = 2.0

    nivel = 1
    puntaje = 0
    vidas = 3
    invulnerable_hasta = 0
    invulnerable_ms = 1200

    boss = None
    boss_active = False
    boss_bullets = []
    boss_threshold_cleared = set()

    powerups = []
    s_active_until = 0
    f_active_until = 0
    p_active_until = 0

    estado = JUGANDO
    return {
        "player": player,
        "balas": balas,
        "vel_bala": vel_bala,
        "cadencia_ms": cadencia_ms,
        "ultimo_disparo": ultimo_disparo,
        "enemigos": enemigos,
        "vel_enemigo_base": vel_enemigo_base,
        "nivel": nivel,
        "puntaje": puntaje,
        "vidas": vidas,
        "invulnerable_hasta": invulnerable_hasta,
        "invulnerable_ms": invulnerable_ms,
        "estado": estado,
        "game_over_sonido_reproducido": False,
        "boss": boss,
        "boss_active": boss_active,
        "boss_bullets": boss_bullets,
        "boss_threshold_cleared": boss_threshold_cleared,
        "powerups": powerups,
        "s_active_until": s_active_until,
        "f_active_until": f_active_until,
        "p_active_until": p_active_until,
        "intro_end_time": 0,
        "intro_text": "",
        "boss_intro_end": 0,
        # Bomba
        "bomb_pickup": None,
        "bombs": [],
        "next_bomb_spawn_time": 0,
        "bomb_spawn_interval_ms": 9000
    }

def activar_pantalla_nivel(juego, ahora):
    juego["vidas"] = 3
    juego["player"].rect.centerx = ANCHO // 2
    juego["player"].rect.bottom = ALTO - 10
    juego["player"].angle = 0.0
    juego["player"].target_angle = 0.0
    juego["balas"].clear()
    juego["boss_bullets"].clear()
    juego["powerups"].clear()
    juego["bombs"].clear()
    juego["bomb_pickup"] = None
    juego["invulnerable_hasta"] = 0
    juego["intro_end_time"] = ahora + LEVEL_INTRO_MS
    juego["intro_text"] = f"NIVEL {juego['nivel']}"

# Hiscore
hiscore = leer_hiscore()

# Estado global
juego = reset_juego()
estado = MENU
muted = False
fullscreen = False

overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
bounds_rect = pygame.Rect(0, 0, ANCHO, ALTO)

# =========================
# Helpers de dibujo UI
# =========================
def draw_letterbox(surface, alpha=200, size=90):
    s = pygame.Surface((ANCHO, size), pygame.SRCALPHA)
    s.fill((0,0,0,alpha))
    surface.blit(s, (0,0))
    surface.blit(s, (0,ALTO-size))

def draw_focus_ring(surface, rect, color=(255,255,255), width=3):
    pygame.draw.rect(surface, color, rect, width, border_radius=12)

# =========================
# Bucle principal con salida limpia
# =========================
running = True
try:
    while running:
        dt = clock.tick(FPS)
        ahora = pygame.time.get_ticks()

        # Cámara
        tx, ty = cam_target(juego["player"].rect)
        cam_x += (tx - cam_x) * CAM_LERP
        cam_y += (ty - cam_y) * CAM_LERP

        # Fondo
        if estado not in (LEVEL_INTRO, PAUSA):
            bg.update(dt)

        # -------------------------
        # Eventos
        # -------------------------
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False

            if evento.type == pygame.KEYDOWN:
                # Salir
                if evento.key == pygame.K_ESCAPE:
                    if estado == JUGANDO:
                        estado = PAUSA
                    elif estado == PAUSA:
                        estado = JUGANDO
                    elif estado in (MENU, GAME_OVER):
                        running = False

                # Pantalla completa
                if evento.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    flags = pygame.FULLSCREEN if fullscreen else 0
                    ventana = pygame.display.set_mode((ANCHO, ALTO), flags)

                # Mute
                if evento.key == pygame.K_m:
                    muted = not muted
                    vol_master = 0.0 if muted else 0.6
                    if sonido_inicio:    sonido_inicio.set_volume(vol_master)
                    if sonido_gameover:  sonido_gameover.set_volume(vol_master)
                    if sonido_disparo:   sonido_disparo.set_volume(0.4 if not muted else 0.0)
                    if sonido_explosion: sonido_explosion.set_volume(0.55 if not muted else 0.0)
                    if sonido_boss:      sonido_boss.set_volume(vol_master)
                    if sonido_power:     sonido_power.set_volume(vol_master)

                # ---- MENU ----
                if estado == MENU:
                    if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        juego = reset_juego()
                        estado = LEVEL_INTRO
                        activar_pantalla_nivel(juego, ahora)
                        juego["intro_text"] = "NIVEL 1"

                # ---- JUGANDO ----
                elif estado == JUGANDO:
                    if evento.key == pygame.K_RETURN:
                        estado = PAUSA

                    if evento.key == pygame.K_SPACE:
                        if ahora - juego["ultimo_disparo"] >= juego["cadencia_ms"]:
                            mx, my = juego["player"].get_muzzle_world()
                            juego["balas"].append(Bala(mx, my, vy=juego["vel_bala"]))
                            juego["ultimo_disparo"] = ahora
                            reproducir(sonido_disparo)

                # ---- PAUSA ----
                elif estado == PAUSA:
                    if evento.key == pygame.K_RETURN:
                        estado = JUGANDO
                    if evento.key == pygame.K_r:
                        juego = reset_juego()
                        estado = LEVEL_INTRO
                        activar_pantalla_nivel(juego, ahora)
                        juego["intro_text"] = "NIVEL 1"

                # ---- GAME_OVER ----
                elif estado == GAME_OVER:
                    if evento.key == pygame.K_r:
                        juego = reset_juego()
                        estado = LEVEL_INTRO
                        activar_pantalla_nivel(juego, ahora)
                        juego["intro_text"] = "NIVEL 1"
                    if evento.key == pygame.K_RETURN:
                        estado = MENU

        # -------------------------
        # Lógica
        # -------------------------
        if estado == LEVEL_INTRO:
            if ahora >= juego["intro_end_time"]:
                estado = JUGANDO

        elif estado == BOSS_INTRO:
            if ahora >= juego["boss_intro_end"]:
                estado = JUGANDO

        elif estado == JUGANDO:
            keys = pygame.key.get_pressed()

            # Buffs
            s_activo = ahora < juego["s_active_until"]
            f_activo = ahora < juego["f_active_until"]
            p_activo = ahora < juego["p_active_until"]

            juego["player"].vel = juego["player"].vel_base + (3 if s_activo else 0)
            juego["cadencia_ms"] = 100 if p_activo else 200
            juego["player"].update(dt, keys, bounds_rect)

            # ¿Aparece jefe?
            needed_points = BOSS_POINTS_PER_LEVEL * juego["nivel"]
            if (juego["puntaje"] >= needed_points
                and juego["nivel"] not in juego["boss_threshold_cleared"]
                and not juego["boss_active"]):
                juego["boss"] = Boss(juego["nivel"])
                juego["boss_active"] = True
                bg.switch_to_boss()
                reproducir(sonido_boss)
                estado = BOSS_INTRO
                juego["boss_intro_end"] = ahora + BOSS_INTRO_MS
                juego["next_bomb_spawn_time"] = ahora + BOSS_INTRO_MS + 200

            # --- SIN JEFE ---
            if not juego["boss_active"]:
                # balas jugador
                for bala in juego["balas"][:]:
                    if not bala.update():
                        juego["balas"].remove(bala)

                # enemigos (asteroides animados)
                vel_enemigo = juego["vel_enemigo_base"] + (juego["nivel"] - 1) * 0.9
                if f_activo and keys[pygame.K_f]:
                    vel_enemigo *= 0.45

                for enemigo in juego["enemigos"]:
                    enemigo.update(dt, vel_enemigo)
                    if enemigo.rect.top > ALTO:
                        respawnear_enemigo(enemigo)

                # colisiones balas/enemigos
                for bala in juego["balas"][:]:
                    impactado = None
                    for enemigo in juego["enemigos"]:
                        if bala.rect.colliderect(enemigo.rect):
                            impactado = enemigo
                            break
                    if impactado:
                        try: juego["balas"].remove(bala)
                        except ValueError: pass
                        drop_x, drop_y = impactado.rect.centerx, impactado.rect.centery
                        respawnear_enemigo(impactado)
                        juego["puntaje"] += 10
                        reproducir(sonido_explosion)
                        if random.random() < 0.12:
                            tipo = random.choice(['S', 'F', 'P'])
                            juego["powerups"].append(PowerUp(tipo, drop_x, drop_y))
                            reproducir(sonido_power)

                # daño a la nave por choque
                if ahora >= juego["invulnerable_hasta"]:
                    for enemigo in juego["enemigos"]:
                        if juego["player"].rect.colliderect(enemigo.rect):
                            juego["vidas"] -= 1
                            juego["invulnerable_hasta"] = ahora + juego["invulnerable_ms"]
                            respawnear_enemigo(enemigo)
                            reproducir(sonido_explosion)
                            juego["player"].rect.centerx = ANCHO // 2
                            juego["player"].rect.bottom = ALTO - 10
                            juego["player"].angle = 0.0
                            juego["player"].target_angle = 0.0
                            break

                # powerups comunes
                for pu in juego["powerups"][:]:
                    if not pu.update():
                        juego["powerups"].remove(pu)
                        continue
                    if pu.rect.colliderect(juego["player"].rect):
                        if pu.tipo == 'S':
                            juego["s_active_until"] = ahora + 8000
                        elif pu.tipo == 'F':
                            juego["f_active_until"] = ahora + 8000
                        elif pu.tipo == 'P':
                            juego["p_active_until"] = ahora + 8000
                        try: juego["powerups"].remove(pu)
                        except ValueError: pass
                        reproducir(sonido_power)

            # --- CON JEFE ---
            else:
                boss = juego["boss"]
                boss_bullets = juego["boss_bullets"]

                # balas jugador
                for bala in juego["balas"][:]:
                    if not bala.update():
                        juego["balas"].remove(bala)

                # jefe
                boss.update(dt, ahora, juego["player"].rect, boss_bullets)

                # daño al jefe por balas
                for bala in juego["balas"][:]:
                    if boss.rect.colliderect(bala.rect):
                        try: juego["balas"].remove(bala)
                        except ValueError: pass
                        boss.hp -= 10
                        reproducir(sonido_explosion)

                # balas del boss
                for b in boss_bullets[:]:
                    r = b["rect"]
                    t = b.get("type", "normal")
                    if t == "wave":
                        b["phase"] += b.get("phase_speed", 0.12)
                        r.x += int(3.2 * math.sin(b["phase"]))
                        r.y += int(b["vy"])
                    else:
                        r.x += int(b["vx"])
                        r.y += int(b["vy"])
                    if r.top > ALTO or r.right < 0 or r.left > ANCHO:
                        boss_bullets.remove(b)

                # === BOMB PICKUP ===
                if juego["bomb_pickup"] is None and ahora >= juego["next_bomb_spawn_time"]:
                    bx = boss.rect.centerx + random.randint(-80, 80)
                    by = boss.rect.bottom + random.randint(20, 60)
                    juego["bomb_pickup"] = BombPickup(bx, by, ahora)
                    juego["next_bomb_spawn_time"] = ahora + juego["bomb_spawn_interval_ms"]

                bp = juego["bomb_pickup"]
                if bp:
                    bp.update(ahora)
                    if not bp.active:
                        juego["bomb_pickup"] = None
                        juego["next_bomb_spawn_time"] = min(juego["next_bomb_spawn_time"], ahora + 1200)
                    elif bp.rect.colliderect(juego["player"].rect):
                        px, py = juego["player"].rect.centerx, juego["player"].rect.top
                        juego["bombs"].append(BombProjectile(px, py, boss.rect))
                        juego["bomb_pickup"] = None
                        reproducir(sonido_power)

                for bomb in juego["bombs"][:]:
                    bomb.update(ahora, boss)
                    if not bomb.active:
                        juego["bombs"].remove(bomb)

                # daño al jugador
                if ahora >= juego["invulnerable_hasta"]:
                    if boss.attack_mode == 4 and boss.laser_active and boss.laser_rect:
                        elapsed = ahora - boss.laser_start_t
                        if elapsed >= boss.laser_warn_ms:
                            if boss.laser_rect.colliderect(juego["player"].rect):
                                juego["vidas"] -= 1
                                juego["invulnerable_hasta"] = ahora + juego["invulnerable_ms"]
                                reproducir(sonido_explosion)
                                juego["player"].rect.centerx = ANCHO // 2
                                juego["player"].rect.bottom = ALTO - 10
                                juego["player"].angle = 0.0
                                juego["player"].target_angle = 0.0

                    for b in boss_bullets[:]:
                        if b["rect"].colliderect(juego["player"].rect):
                            boss_bullets.remove(b)
                            juego["vidas"] -= 1
                            juego["invulnerable_hasta"] = ahora + juego["invulnerable_ms"]
                            reproducir(sonido_explosion)
                            juego["player"].rect.centerx = ANCHO // 2
                            juego["player"].rect.bottom = ALTO - 10
                            juego["player"].angle = 0.0
                            juego["player"].target_angle = 0.0
                            break

                # muerte del boss
                if boss.hp <= 0:
                    juego["boss_active"] = False
                    juego["boss_threshold_cleared"].add(juego["nivel"])
                    juego["boss"] = None
                    juego["boss_bullets"].clear()
                    juego["bombs"].clear()
                    juego["bomb_pickup"] = None
                    juego["puntaje"] += 100
                    juego["nivel"] += 1
                    juego["vel_enemigo_base"] += 0.8
                    if len(juego["enemigos"]) < 12:
                        juego["enemigos"] += crear_enemigos(1)
                    bg.switch_to_main()
                    estado = LEVEL_INTRO
                    activar_pantalla_nivel(juego, ahora)

            # ¿Sin vidas?
            if juego["vidas"] <= 0 and estado in (JUGANDO, BOSS_INTRO):
                estado = GAME_OVER
                if not juego["game_over_sonido_reproducido"]:
                    reproducir(sonido_gameover)
                    juego["game_over_sonido_reproducido"] = True
                if juego["puntaje"] > hiscore:
                    hiscore = juego["puntaje"]
                    guardar_hiscore(hiscore)

        # -------------------------
        # Dibujo
        # -------------------------
        if estado in (JUGANDO, BOSS_INTRO, GAME_OVER, MENU):
            bg.draw(ventana)

        if estado == MENU:
            ventana.fill(NEGRO)
            card = pygame.Rect(0, 0, 560, 360)
            card.center = (ANCHO//2, ALTO//2)
            pygame.draw.rect(ventana, GRIS, card, border_radius=18)
            pygame.draw.rect(ventana, (70,70,85), card.inflate(8,8), 4, border_radius=22)

            dibujar_texto(ventana, "GAME NAVE", fuente_titulo, BLANCO, ANCHO//2, card.top + 70, centrado=True)
            dibujar_texto(ventana, "ENTER o SPACE para jugar", fuente, AMARILLO, ANCHO//2, card.top + 140, centrado=True)
            dibujar_texto(ventana, "Controles: Flechas, SPACE disparo, ENTER pausa", fuente, BLANCO, ANCHO//2, card.top + 185, centrado=True)
            dibujar_texto(ventana, "Bomba: recoge el ítem durante el jefe para dispararla automáticamente", fuente, AMARILLO, ANCHO//2, card.top + 215, centrado=True)
            dibujar_texto(ventana, "F11 pantalla completa | M silenciar", fuente, BLANCO, ANCHO//2, card.top + 245, centrado=True)
            dibujar_texto(ventana, f"Mejor puntaje: {hiscore}", fuente, AZUL, ANCHO//2, card.top + 285, centrado=True)
            dibujar_texto(ventana, "created by: TodTete", fuente, BLANCO, ANCHO//2, ALTO-40, centrado=True)

        elif estado == LEVEL_INTRO:
            ventana.fill(NEGRO)
            dibujar_texto(ventana, juego["intro_text"], fuente_grande, BLANCO, ANCHO//2, ALTO//2 - 10, centrado=True)
            dibujar_texto(ventana, "¡Vidas reiniciadas!", fuente, AMARILLO, ANCHO//2, ALTO//2 + 40, centrado=True)

        elif estado in (JUGANDO, PAUSA, BOSS_INTRO):
            # Nave
            visible = True
            if estado != PAUSA and pygame.time.get_ticks() < juego["invulnerable_hasta"]:
                visible = ((ahora // 100) % 2 == 0)
            juego["player"].draw(ventana, visible=visible)

            # Balas jugador (con imagen)
            for bala in juego["balas"]:
                bala.draw(ventana)

            if not juego["boss_active"]:
                for enemigo in juego["enemigos"]:
                    enemigo.draw(ventana)
                for pu in juego["powerups"]:
                    pu.draw(ventana, fuente)
            else:
                juego["boss"].draw(ventana, ahora)
                for b in juego["boss_bullets"]:
                    color = (255,140,0)
                    t = b.get("type","normal")
                    if t == "wave": color = (255,200,0)
                    elif t == "aim": color = (255,80,80)
                    elif t == "spread": color = (255,160,60)
                    elif t == "burst": color = (255,100,0)
                    pygame.draw.rect(ventana, color, cam_apply_rect(b["rect"]))
                if juego["bomb_pickup"]:
                    juego["bomb_pickup"].draw(ventana)

            # Bombas proyectil
            for bomb in juego["bombs"]:
                bomb.draw(ventana)

            # HUD
            dibujar_texto(ventana, f"Puntaje: {juego['puntaje']}", fuente, BLANCO, 10, 10)
            dibujar_texto(ventana, f"Nivel: {juego['nivel']}", fuente, BLANCO, 10, 40)
            dibujar_texto(ventana, f"Vidas: {juego['vidas']}", fuente, BLANCO, 10, 70)
            if muted:
                dibujar_texto(ventana, "MUTED", fuente, ROJO, ANCHO - 90, 10)
            if not juego["boss_active"]:
                need = BOSS_POINTS_PER_LEVEL * juego["nivel"]
                dibujar_texto(ventana, f"Jefe a los {need} pts", fuente, AMARILLO, ANCHO - 240, 10)

            # Buffs
            now = ahora
            if now < juego["s_active_until"]:
                secs = (juego["s_active_until"] - now) // 1000
                dibujar_texto(ventana, f"S({secs}s)", fuente, VERDE, ANCHO - 120, 40)
            if now < juego["f_active_until"]:
                secs = (juego["f_active_until"] - now) // 1000
                dibujar_texto(ventana, f"F({secs}s)", fuente, AMARILLO, ANCHO - 60, 40)
            if now < juego["p_active_until"]:
                secs = (juego["p_active_until"] - now) // 1000
                dibujar_texto(ventana, f"P({secs}s)", fuente, MORADO, ANCHO - 120, 70)

            # Pausa
            if estado == PAUSA:
                ventana.fill(NEGRO)
                dibujar_texto(ventana, "PAUSA", fuente_grande, AMARILLO, ANCHO//2, ALTO//2 - 40, centrado=True)
                dibujar_texto(ventana, "ENTER reanudar | R reiniciar | ESC salir", fuente, BLANCO, ANCHO//2, ALTO//2 + 20, centrado=True)

            # Cinemática
            if estado == BOSS_INTRO and juego["boss_active"] and juego["boss"]:
                draw_letterbox(ventana, alpha=200, size=90)
                t_left = max(0, juego["boss_intro_end"] - ahora)
                k = 1.0 - max(0.0, min(1.0, t_left / BOSS_INTRO_MS))
                bx, by, bw, bh = juego["boss"].rect
                pad = int(40 + 40 * (1.0 - k))
                focus = pygame.Rect(bx - pad, by - pad, bw + pad*2, bh + pad*2)
                focus = cam_apply_rect(focus)
                draw_focus_ring(ventana, focus, color=(255,255,255), width=3)
                dibujar_texto(ventana, "¡ALERTA JEFE!", fuente_grande, ROJO, ANCHO//2, 130, centrado=True)

        elif estado == GAME_OVER:
            ventana.fill(NEGRO)
            dibujar_texto(ventana, "GAME OVER", fuente_grande, ROJO, ANCHO//2, ALTO//2 - 80, centrado=True)
            dibujar_texto(ventana, f"Puntaje: {juego['puntaje']}", fuente, BLANCO, ANCHO//2, ALTO//2 - 10, centrado=True)
            dibujar_texto(ventana, f"Mejor puntaje: {hiscore}", fuente, AZUL, ANCHO//2, ALTO//2 + 20, centrado=True)
            dibujar_texto(ventana, "R para reiniciar", fuente, BLANCO, ANCHO//2, ALTO//2 + 70, centrado=True)
            dibujar_texto(ventana, "ENTER para volver al menú | ESC salir", fuente, BLANCO, ANCHO//2, ALTO//2 + 100, centrado=True)

        pygame.display.flip()

except KeyboardInterrupt:
    pass
finally:
    pygame.quit()
