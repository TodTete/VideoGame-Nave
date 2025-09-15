import pygame 
import random
import sys
import os

# ======= GIF loader (Pillow) =======
try:
    from PIL import Image, ImageSequence
    PIL_OK = True
except Exception as e:
    print("[AVISO] Pillow no disponible, los fondos GIF serán estáticos:", e)
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
JUGANDO = "JUGANDO"
PAUSA = "PAUSA"
GAME_OVER = "GAME_OVER"

# Umbral para jefe por nivel: puntos >= 250 * nivel
BOSS_POINTS_PER_LEVEL = 250

# Duración de pantallas de nivel y pausa
LEVEL_INTRO_MS = 1500

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

# ======= GIF Animado como fondo =======
def load_gif_frames(path, size=(ANCHO, ALTO)):
    """Carga frames de un GIF a Surfaces de Pygame, con duración por frame."""
    frames = []
    durations = []
    if not PIL_OK:
        # Fallback: cargar como imagen normal si se puede
        try:
            img = pygame.image.load(path).convert()
            img = pygame.transform.smoothscale(img, size)
            frames = [img]
            durations = [120]
        except Exception as e:
            print(f"[AVISO] No se pudo cargar fondo '{path}': {e}")
            surf = pygame.Surface(size)
            surf.fill((5, 5, 15))
            frames = [surf]
            durations = [120]
        return frames, durations

    try:
        im = Image.open(path)
        # Forzamos conversión a RGBA
        base_frames = []
        base_durations = []
        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            dur = frame.info.get("duration", 100)
            base_durations.append(max(20, int(dur)))
            if size is not None:
                frame = frame.resize(size, Image.LANCZOS)
            mode = frame.mode
            data = frame.tobytes()
            py_img = pygame.image.fromstring(data, frame.size, mode)
            base_frames.append(py_img.convert_alpha())
        if not base_frames:
            raise ValueError("GIF sin frames")
        return base_frames, base_durations
    except Exception as e:
        print(f"[AVISO] Error cargando GIF '{path}': {e}")
        surf = pygame.Surface(size)
        surf.fill((5, 5, 15))
        return [surf], [120]

class AnimatedBackground:
    def __init__(self, path_main="fondo.gif", path_boss="fondo-gf.gif"):
        self.frames_a, self.durs_a = load_gif_frames(path_main)
        self.frames_b, self.durs_b = load_gif_frames(path_boss)
        self.use_b = False
        self.idx_a = 0
        self.idx_b = 0
        self.t_accum_a = 0
        self.t_accum_b = 0

        # Transición cruzada
        self.transition = False
        self.transition_time = 0.0
        self.transition_duration = 1200  # ms
        self.alpha = 0  # 0..255

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
pygame.mixer.init()

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Game Nave")

clock = pygame.time.Clock()
fuente = pygame.font.SysFont("Arial", 24)
fuente_grande = pygame.font.SysFont("Arial", 48, bold=True)
fuente_titulo = pygame.font.SysFont("Arial", 56, bold=True)

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
# Clase Jugador (Nave con forma y tilt)
# =========================
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
        pygame.draw.polygon(surf, (18,70,160), left_wing)
        pygame.draw.polygon(surf, (18,70,160), right_wing)
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

    def draw(self, surface, visible=True):
        if not visible: return
        img, r = self._rotated_image_and_rect()
        surface.blit(img, r)

# =========================
# Boss (Jefe)
# =========================
class Boss:
    def __init__(self, level):
        self.level = level
        self.w = 220
        self.h = 100
        self.rect = pygame.Rect(ANCHO//2 - self.w//2, 60, self.w, self.h)
        self.hp_max = 160 + (level-1)*80
        self.hp = self.hp_max
        self.move_speed = 2.2 + (level-1)*0.6
        self.bullet_speed = 5 + (level-1)*1.0
        self.fire_cd_ms = max(350, 900 - (level-1)*120)
        self.last_shot = 0
        self.dir = 1
        self.color = (140, 25, 25)
        self.cannons = [0.2, 0.5, 0.8]
        self.alive = True

    def update(self, dt, ahora, player_rect, boss_bullets):
        self.rect.x += int(self.move_speed) * self.dir
        if self.rect.right >= ANCHO - 10:
            self.rect.right = ANCHO - 10
            self.dir = -1
        elif self.rect.left <= 10:
            self.rect.left = 10
            self.dir = 1

        if ahora - self.last_shot >= self.fire_cd_ms:
            self.last_shot = ahora
            for rel in self.cannons:
                cx = int(self.rect.left + self.w * rel)
                cy = self.rect.bottom - 8
                boss_bullets.append(pygame.Rect(cx-5, cy, 10, 18))

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=16)
        pygame.draw.rect(surface, (200, 60, 60), self.rect.inflate(-20, -30), border_radius=12)
        slit_h = 10
        for i in range(4):
            r = pygame.Rect(self.rect.left + 20 + i*45, self.rect.top + 20, 35, slit_h)
            pygame.draw.rect(surface, (255, 180, 180), r, border_radius=6)
        bar_w = self.w
        bar_h = 10
        bar_x = self.rect.left
        bar_y = self.rect.top - 16
        pygame.draw.rect(surface, (90, 90, 90), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        pct = max(0.0, self.hp / self.hp_max)
        pygame.draw.rect(surface, (255, 60, 60), (bar_x, bar_y, int(bar_w * pct), bar_h), border_radius=6)

# =========================
# PowerUps
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
        # color y letra
        if self.tipo == 'S':
            color = VERDE
        elif self.tipo == 'F':
            color = AMARILLO
        else:
            color = MORADO
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        dibujar_texto(surface, self.tipo, fuente, NEGRO, self.rect.centerx, self.rect.centery-10, centrado=True)

# =========================
# Juego: helpers para enemigos
# =========================
def crear_enemigos(cantidad):
    lista = []
    for _ in range(cantidad):
        x = random.randint(0, ANCHO - 40)
        y = random.randint(-250, -40)
        lista.append(pygame.Rect(x, y, 40, 40))
    return lista

def respawnear_enemigo(enemigo):
    enemigo.x = random.randint(0, ANCHO - enemigo.width)
    enemigo.y = random.randint(-200, -40)

# =========================
# Variables de juego / reset
# =========================
def reset_juego():
    player = Jugador(ANCHO//2, ALTO - 10)
    balas = []
    vel_bala = -9
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
        "intro_text": ""
    }

def activar_pantalla_nivel(juego, ahora):
    # Reinicia vidas y muestra pantalla de nivel
    juego["vidas"] = 3
    juego["player"].rect.centerx = ANCHO // 2
    juego["player"].rect.bottom = ALTO - 10
    juego["player"].angle = 0.0
    juego["player"].target_angle = 0.0
    juego["balas"].clear()
    juego["boss_bullets"].clear()
    juego["powerups"].clear()
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
# Bucle principal
# =========================
running = True
while running:
    dt = clock.tick(FPS)
    ahora = pygame.time.get_ticks()

    # Fondo (solo animamos si no estamos en pantallas negras absolutas)
    if estado not in (LEVEL_INTRO, PAUSA):
        bg.update(dt)

    # -------------------------
    # Eventos
    # -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False

        if evento.type == pygame.KEYDOWN:
            # Salir general
            if evento.key == pygame.K_ESCAPE:
                if estado == JUGANDO:
                    estado = PAUSA
                elif estado == PAUSA:
                    estado = JUGANDO
                elif estado in (MENU, GAME_OVER):
                    running = False

            # Pantalla completa con F11 (no 'F' para no chocar con poder F)
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
                    activar_pantalla_nivel(juego, ahora)  # NIVEL 1
                    juego["intro_text"] = "NIVEL 1"

            # ---- JUGANDO ----
            elif estado == JUGANDO:
                # Pausa con ENTER
                if evento.key == pygame.K_RETURN:
                    estado = PAUSA

                if evento.key == pygame.K_SPACE:
                    if ahora - juego["ultimo_disparo"] >= juego["cadencia_ms"]:
                        mx, my = juego["player"].get_muzzle_world()
                        bala = pygame.Rect(mx - 4, my - 20, 8, 18)
                        juego["balas"].append(bala)
                        juego["ultimo_disparo"] = ahora
                        reproducir(sonido_disparo)

            # ---- PAUSA ----
            elif estado == PAUSA:
                # ENTER reanudar, R reiniciar
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
        # Espera fija y pasa a jugar
        if ahora >= juego["intro_end_time"]:
            estado = JUGANDO

    elif estado == JUGANDO:
        keys = pygame.key.get_pressed()

        # Buffs activos
        s_activo = ahora < juego["s_active_until"]
        f_activo = ahora < juego["f_active_until"]
        p_activo = ahora < juego["p_active_until"]

        # Aplicar efectos de buffs
        juego["player"].vel = juego["player"].vel_base + (3 if s_activo else 0)
        juego["cadencia_ms"] = 100 if p_activo else 200  # disparo rápido cuando P activa

        # Actualizar jugador
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

        # --- Sin jefe activo: enemigos y powerups ---
        if not juego["boss_active"]:
            # Mover balas del jugador
            for bala in juego["balas"][:]:
                bala.y += juego["vel_bala"]
                if bala.bottom < 0:
                    juego["balas"].remove(bala)

            # Velocidad de enemigos escala con nivel + efecto F si se mantiene presionada la tecla F
            vel_enemigo = juego["vel_enemigo_base"] + (juego["nivel"] - 1) * 0.9
            if f_activo and keys[pygame.K_f]:
                vel_enemigo *= 0.45  # ralentiza mientras se presiona F y el poder está activo

            for enemigo in juego["enemigos"]:
                enemigo.y += vel_enemigo
                if enemigo.top > ALTO:
                    respawnear_enemigo(enemigo)

            # Colisiones bala-enemigo
            for bala in juego["balas"][:]:
                impactado = None
                for enemigo in juego["enemigos"]:
                    if bala.colliderect(enemigo):
                        impactado = enemigo
                        break
                if impactado:
                    try:
                        juego["balas"].remove(bala)
                    except ValueError:
                        pass

                    # Guardar posición antes del respawn para soltar powerup ahí
                    drop_x, drop_y = impactado.centerx, impactado.centery
                    respawnear_enemigo(impactado)
                    juego["puntaje"] += 10
                    reproducir(sonido_explosion)

                    # Probabilidad de soltar un powerup
                    if random.random() < 0.12:
                        tipo = random.choice(['S', 'F', 'P'])
                        juego["powerups"].append(PowerUp(tipo, drop_x, drop_y))
                        reproducir(sonido_power)

            # Colisión nave-enemigo con invulnerabilidad
            if ahora >= juego["invulnerable_hasta"]:
                for enemigo in juego["enemigos"]:
                    if juego["player"].rect.colliderect(enemigo):
                        juego["vidas"] -= 1
                        juego["invulnerable_hasta"] = ahora + juego["invulnerable_ms"]
                        respawnear_enemigo(enemigo)
                        reproducir(sonido_explosion)
                        juego["player"].rect.centerx = ANCHO // 2
                        juego["player"].rect.bottom = ALTO - 10
                        juego["player"].angle = 0.0
                        juego["player"].target_angle = 0.0
                        break

            # PowerUps: movimiento y recogida
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
                    try:
                        juego["powerups"].remove(pu)
                    except ValueError:
                        pass
                    reproducir(sonido_power)

        else:
            # ======= Lógica del Boss =======
            boss = juego["boss"]
            boss_bullets = juego["boss_bullets"]

            for bala in juego["balas"][:]:
                bala.y += juego["vel_bala"]
                if bala.bottom < 0:
                    juego["balas"].remove(bala)

            boss.update(dt, ahora, juego["player"].rect, boss_bullets)

            for bala in juego["balas"][:]:
                if boss.rect.colliderect(bala):
                    try:
                        juego["balas"].remove(bala)
                    except ValueError:
                        pass
                    boss.hp -= 10
                    reproducir(sonido_explosion)

            for b in boss_bullets[:]:
                b.y += int(boss.bullet_speed)
                if b.top > ALTO:
                    boss_bullets.remove(b)

            if ahora >= juego["invulnerable_hasta"]:
                for b in boss_bullets[:]:
                    if b.colliderect(juego["player"].rect):
                        boss_bullets.remove(b)
                        juego["vidas"] -= 1
                        juego["invulnerable_hasta"] = ahora + juego["invulnerable_ms"]
                        reproducir(sonido_explosion)
                        juego["player"].rect.centerx = ANCHO // 2
                        juego["player"].rect.bottom = ALTO - 10
                        juego["player"].angle = 0.0
                        juego["player"].target_angle = 0.0
                        break

            # Chequear muerte del boss
            if boss.hp <= 0:
                juego["boss_active"] = False
                juego["boss_threshold_cleared"].add(juego["nivel"])
                juego["boss"] = None
                juego["boss_bullets"].clear()
                juego["puntaje"] += 100
                # Subir de nivel
                juego["nivel"] += 1
                # Aumenta dificultad de cubos
                juego["vel_enemigo_base"] += 0.8
                if len(juego["enemigos"]) < 12:
                    juego["enemigos"] += crear_enemigos(1)
                # Fondo de vuelta
                bg.switch_to_main()
                # Mostrar pantalla negra del nuevo nivel y REINICIAR VIDAS
                estado = LEVEL_INTRO
                activar_pantalla_nivel(juego, ahora)

        # ¿Sin vidas?
        if juego["vidas"] <= 0 and estado == JUGANDO:
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
    if estado in (JUGANDO, GAME_OVER, MENU):
        bg.draw(ventana)

    if estado == MENU:
        # Menú minimalista
        ventana.fill(NEGRO)
        # Tarjeta central
        card = pygame.Rect(0, 0, 560, 360)
        card.center = (ANCHO//2, ALTO//2)
        pygame.draw.rect(ventana, GRIS, card, border_radius=18)
        pygame.draw.rect(ventana, (70,70,85), card.inflate(8,8), 4, border_radius=22)

        dibujar_texto(ventana, "GAME NAVE", fuente_titulo, BLANCO, ANCHO//2, card.top + 70, centrado=True)
        dibujar_texto(ventana, "ENTER o SPACE para jugar", fuente, AMARILLO, ANCHO//2, card.top + 140, centrado=True)
        dibujar_texto(ventana, "Controles: Flechas, SPACE disparo, ENTER pausa", fuente, BLANCO, ANCHO//2, card.top + 185, centrado=True)
        dibujar_texto(ventana, "Powerups: S velocidad | F ralentiza (mantén F) | P cadencia", fuente, BLANCO, ANCHO//2, card.top + 215, centrado=True)
        dibujar_texto(ventana, "F11 pantalla completa | M silenciar", fuente, BLANCO, ANCHO//2, card.top + 245, centrado=True)
        dibujar_texto(ventana, f"Mejor puntaje: {hiscore}", fuente, AZUL, ANCHO//2, card.top + 285, centrado=True)
        dibujar_texto(ventana, "created by: TodTete", fuente, BLANCO, ANCHO//2, ALTO-40, centrado=True)

    elif estado == LEVEL_INTRO:
        # Pantalla negra con texto de nivel
        ventana.fill(NEGRO)
        dibujar_texto(ventana, juego["intro_text"], fuente_grande, BLANCO, ANCHO//2, ALTO//2 - 10, centrado=True)
        dibujar_texto(ventana, "¡Vidas reiniciadas!", fuente, AMARILLO, ANCHO//2, ALTO//2 + 40, centrado=True)

    elif estado in (JUGANDO, PAUSA):
        # Nave (parpadeo si invulnerable)
        visible = True
        if estado == JUGANDO and pygame.time.get_ticks() < juego["invulnerable_hasta"]:
            visible = ((ahora // 100) % 2 == 0)
        juego["player"].draw(ventana, visible=visible)

        # Balas del jugador
        for bala in juego["balas"]:
            pygame.draw.rect(ventana, BLANCO, bala)

        # Enemigos o Boss
        if not juego["boss_active"]:
            for enemigo in juego["enemigos"]:
                pygame.draw.rect(ventana, ROJO, enemigo)
            # Powerups
            for pu in juego["powerups"]:
                pu.draw(ventana, fuente)
        else:
            juego["boss"].draw(ventana)
            for b in juego["boss_bullets"]:
                pygame.draw.rect(ventana, (255, 140, 0), b)

        # HUD
        dibujar_texto(ventana, f"Puntaje: {juego['puntaje']}", fuente, BLANCO, 10, 10)
        dibujar_texto(ventana, f"Nivel: {juego['nivel']}", fuente, BLANCO, 10, 40)
        dibujar_texto(ventana, f"Vidas: {juego['vidas']}", fuente, BLANCO, 10, 70)
        if muted:
            dibujar_texto(ventana, "MUTED", fuente, ROJO, ANCHO - 90, 10)
        if not juego["boss_active"]:
            need = BOSS_POINTS_PER_LEVEL * juego["nivel"]
            dibujar_texto(ventana, f"Jefe a los {need} pts", fuente, AMARILLO, ANCHO - 240, 10)

        # Indicadores de buffs
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

        # Pantalla de PAUSA en NEGRO
        if estado == PAUSA:
            ventana.fill(NEGRO)
            dibujar_texto(ventana, "PAUSA", fuente_grande, AMARILLO, ANCHO//2, ALTO//2 - 40, centrado=True)
            dibujar_texto(ventana, "ENTER reanudar | R reiniciar | ESC salir", fuente, BLANCO, ANCHO//2, ALTO//2 + 20, centrado=True)

    elif estado == GAME_OVER:
        ventana.fill(NEGRO)
        dibujar_texto(ventana, "GAME OVER", fuente_grande, ROJO, ANCHO//2, ALTO//2 - 80, centrado=True)
        dibujar_texto(ventana, f"Puntaje: {juego['puntaje']}", fuente, BLANCO, ANCHO//2, ALTO//2 - 10, centrado=True)
        dibujar_texto(ventana, f"Mejor puntaje: {hiscore}", fuente, AZUL, ANCHO//2, ALTO//2 + 20, centrado=True)
        dibujar_texto(ventana, "R para reiniciar", fuente, BLANCO, ANCHO//2, ALTO//2 + 70, centrado=True)
        dibujar_texto(ventana, "ENTER para volver al menú | ESC salir", fuente, BLANCO, ANCHO//2, ALTO//2 + 100, centrado=True)

    pygame.display.flip()

pygame.quit()
sys.exit()
