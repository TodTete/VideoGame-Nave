import pygame, random
from .config import *
from .assets import cargar_sonido, reproducir, leer_hiscore, guardar_hiscore, dibujar_texto
from .background import AnimatedBackground
from .camera import Camera
from .entities import Jugador
from .boss import Boss
from .enemies import crear_enemigos, respawnear_enemigo
from .powerups import PowerUp, BombPickup, BombProjectile
from .ui import draw_letterbox, draw_focus_ring, draw_menu, draw_hud, StarField

class Game:
    def __init__(self, ventana):
        self.win = ventana
        self.clock = pygame.time.Clock()
        self.fuente = pygame.font.SysFont("Arial", 24)
        self.fuente_grande = pygame.font.SysFont("Arial", 48, bold=True)
        self.fuente_titulo = pygame.font.SysFont("Arial", 56, bold=True)

        # Audio
        try:
            pygame.mixer.init()
        except Exception as e:
            print("[AVISO] Audio deshabilitado:", e)

        self.snd_start   = cargar_sonido(f"{ASSETS_DIR}/game-start-317318.mp3", 0.6)
        self.snd_over    = cargar_sonido(f"{ASSETS_DIR}/game-over-381772.mp3", 0.6)
        self.snd_shoot   = cargar_sonido(f"{ASSETS_DIR}/laser-shot-ingame-230500.mp3", 0.4)
        self.snd_expl    = cargar_sonido(f"{ASSETS_DIR}/wood-crate-destory-2-97263.mp3", 0.55)
        self.snd_boss    = cargar_sonido(f"{ASSETS_DIR}/boss.mp3", 0.11)
        self.snd_power   = cargar_sonido(f"{ASSETS_DIR}/powerup.mp3", 0.6)

        reproducir(self.snd_start)

        self.bg = AnimatedBackground(f"{ASSETS_DIR}/fondo.gif", f"{ASSETS_DIR}/fondo-gf.gif")

        self.camera = Camera()
        self.bounds_rect = pygame.Rect(0, 0, ANCHO, ALTO)

        self.hiscore = leer_hiscore()
        self.starfield = StarField(140)

        self.reset()
        self.estado = MENU
        self.muted = False
        self.fullscreen = False

    def reset(self):
        player = Jugador(ANCHO//2, ALTO - 10)
        self.juego = {
            "player": player,
            "balas": [],
            "vel_bala": -9,
            "cadencia_ms": 200,
            "ultimo_disparo": 0,
            "enemigos": crear_enemigos(6),
            "vel_enemigo_base": 2.0,
            "nivel": 1,
            "puntaje": 0,
            "vidas": 3,
            "invulnerable_hasta": 0,
            "invulnerable_ms": 1200,
            "estado": JUGANDO,
            "game_over_sonido_reproducido": False,
            "boss": None, "boss_active": False,
            "boss_bullets": [],
            "boss_threshold_cleared": set(),
            "powerups": [],
            "s_active_until": 0,
            "f_active_until": 0,
            "p_active_until": 0,
            "intro_end_time": 0, "intro_text": "",
            "boss_intro_end": 0,
            "bomb_pickup": None,
            "bombs": [],
            "next_bomb_spawn_time": 0,
            "bomb_spawn_interval_ms": 9000
        }

    def activar_pantalla_nivel(self, ahora):
        juego = self.juego
        juego["vidas"] = 3
        p = juego["player"]
        p.rect.centerx = ANCHO // 2; p.rect.bottom = ALTO - 10
        p.angle = 0.0; p.target_angle = 0.0
        juego["balas"].clear(); juego["boss_bullets"].clear()
        juego["powerups"].clear(); juego["bombs"].clear()
        juego["bomb_pickup"] = None
        juego["invulnerable_hasta"] = 0
        juego["intro_end_time"] = ahora + LEVEL_INTRO_MS
        juego["intro_text"] = f"NIVEL {juego['nivel']}"

    # -------------------------
    # EVENTOS
    # -------------------------
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if self.estado == JUGANDO: self.estado = PAUSA
                    elif self.estado == PAUSA: self.estado = JUGANDO
                    elif self.estado in (MENU, GAME_OVER): return False

                if e.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    flags = pygame.FULLSCREEN if self.fullscreen else 0
                    self.win = pygame.display.set_mode((ANCHO, ALTO), flags)

                if e.key == pygame.K_m:
                    self.muted = not self.muted
                    vol_master = 0.0 if self.muted else 0.6
                    if self.snd_start: self.snd_start.set_volume(vol_master)
                    if self.snd_over:  self.snd_over.set_volume(vol_master)
                    if self.snd_shoot: self.snd_shoot.set_volume(0.4 if not self.muted else 0.0)
                    if self.snd_expl:  self.snd_expl.set_volume(0.55 if not self.muted else 0.0)
                    if self.snd_boss:  self.snd_boss.set_volume(vol_master)
                    if self.snd_power: self.snd_power.set_volume(vol_master)

                if self.estado == MENU:
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset()
                        self.estado = LEVEL_INTRO
                        self.activar_pantalla_nivel(pygame.time.get_ticks())
                        self.juego["intro_text"] = "NIVEL 1"

                elif self.estado == JUGANDO:
                    if e.key == pygame.K_RETURN:
                        self.estado = PAUSA
                    if e.key == pygame.K_SPACE:
                        ahora = pygame.time.get_ticks()
                        if ahora - self.juego["ultimo_disparo"] >= self.juego["cadencia_ms"]:
                            mx, my = self.juego["player"].get_muzzle_world()
                            self.juego["balas"].append(pygame.Rect(mx-4, my-20, 8, 18))
                            self.juego["ultimo_disparo"] = ahora
                            reproducir(self.snd_shoot)

                elif self.estado == PAUSA:
                    if e.key == pygame.K_RETURN:
                        self.estado = JUGANDO
                    if e.key == pygame.K_r:
                        self.reset()
                        self.estado = LEVEL_INTRO
                        self.activar_pantalla_nivel(pygame.time.get_ticks())
                        self.juego["intro_text"] = "NIVEL 1"

                elif self.estado == GAME_OVER:
                    if e.key == pygame.K_r:
                        self.reset()
                        self.estado = LEVEL_INTRO
                        self.activar_pantalla_nivel(pygame.time.get_ticks())
                        self.juego["intro_text"] = "NIVEL 1"
                    if e.key == pygame.K_RETURN:
                        self.estado = MENU

        return True

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, dt):
        ahora = pygame.time.get_ticks()
        if self.estado not in (LEVEL_INTRO, PAUSA):
            self.bg.update(dt)

        # cámara
        self.camera.update(dt, self.juego["player"].rect)

        if self.estado == LEVEL_INTRO:
            if ahora >= self.juego["intro_end_time"]:
                self.estado = JUGANDO

        elif self.estado == BOSS_INTRO:
            if ahora >= self.juego["boss_intro_end"]:
                self.estado = JUGANDO

        elif self.estado == JUGANDO:
            keys = pygame.key.get_pressed()
            j = self.juego
            p = j["player"]

            # buffs
            s_activo = ahora < j["s_active_until"]
            f_activo = ahora < j["f_active_until"]
            p_activo = ahora < j["p_active_until"]
            p.vel = p.vel_base + (3 if s_activo else 0)
            j["cadencia_ms"] = 100 if p_activo else 200

            p.update(dt, keys, self.bounds_rect)

            # ¿aparece jefe?
            needed_points = BOSS_POINTS_PER_LEVEL * j["nivel"]
            if (j["puntaje"] >= needed_points 
                and j["nivel"] not in j["boss_threshold_cleared"]
                and not j["boss_active"]):
                j["boss"] = Boss(j["nivel"])
                j["boss_active"] = True
                self.bg.switch_to_boss()
                reproducir(self.snd_boss)
                self.estado = BOSS_INTRO
                j["boss_intro_end"] = ahora + BOSS_INTRO_MS
                j["next_bomb_spawn_time"] = ahora + BOSS_INTRO_MS + 200

            # sin jefe
            if not j["boss_active"]:
                for bala in j["balas"][:]:
                    bala.y += j["vel_bala"]
                    if bala.bottom < 0: j["balas"].remove(bala)

                vel_enemigo = j["vel_enemigo_base"] + (j["nivel"] - 1) * 0.9
                if f_activo and keys[pygame.K_f]: vel_enemigo *= 0.45

                for en in j["enemigos"]:
                    en.y += vel_enemigo
                    if en.top > ALTO: respawnear_enemigo(en)

                for bala in j["balas"][:]:
                    hit = None
                    for en in j["enemigos"]:
                        if bala.colliderect(en):
                            hit = en; break
                    if hit:
                        try: j["balas"].remove(bala)
                        except ValueError: pass
                        drop_x, drop_y = hit.centerx, hit.centery
                        respawnear_enemigo(hit)
                        j["puntaje"] += 10
                        reproducir(self.snd_expl)
                        if random.random() < 0.12:
                            tipo = random.choice(['S','F','P'])
                            j["powerups"].append(PowerUp(tipo, drop_x, drop_y))
                            reproducir(self.snd_power)

                if ahora >= j["invulnerable_hasta"]:
                    for en in j["enemigos"]:
                        if p.rect.colliderect(en):
                            j["vidas"] -= 1
                            j["invulnerable_hasta"] = ahora + j["invulnerable_ms"]
                            respawnear_enemigo(en)
                            reproducir(self.snd_expl)
                            p.rect.centerx = ANCHO//2; p.rect.bottom = ALTO-10
                            p.angle = p.target_angle = 0.0
                            break

                for pu in j["powerups"][:]:
                    pu.update()
                    if not pu.active:
                        j["powerups"].remove(pu); continue
                    if pu.rect.colliderect(p.rect):
                        if pu.tipo == 'S': j["s_active_until"] = ahora + 8000
                        elif pu.tipo == 'F': j["f_active_until"] = ahora + 8000
                        elif pu.tipo == 'P': j["p_active_until"] = ahora + 8000
                        try: j["powerups"].remove(pu)
                        except ValueError: pass
                        reproducir(self.snd_power)

            # con jefe
            else:
                boss = j["boss"]
                bb = j["boss_bullets"]

                for bala in j["balas"][:]:
                    bala.y += j["vel_bala"]
                    if bala.bottom < 0: j["balas"].remove(bala)

                boss.update(dt, ahora, p.rect, bb)

                for bala in j["balas"][:]:
                    if boss.rect.colliderect(bala):
                        try: j["balas"].remove(bala)
                        except ValueError: pass
                        boss.hp -= 10
                        reproducir(self.snd_expl)

                for b in bb[:]:
                    r = b["rect"]; t = b.get("type","normal")
                    if t == "wave":
                        b["phase"] += b.get("phase_speed", 0.12)
                        r.x += int(3.2 * __import__("math").sin(b["phase"]))
                        r.y += int(b["vy"])
                    else:
                        r.x += int(b["vx"]); r.y += int(b["vy"])
                    if r.top > ALTO or r.right < 0 or r.left > ANCHO:
                        bb.remove(b)

                # spawn periódico del pickup
                if j["bomb_pickup"] is None and ahora >= j["next_bomb_spawn_time"]:
                    bx = boss.rect.centerx + random.randint(-80, 80)
                    by = boss.rect.bottom + random.randint(20, 60)
                    j["bomb_pickup"] = BombPickup(bx, by, ahora)
                    j["next_bomb_spawn_time"] = ahora + j["bomb_spawn_interval_ms"]

                bp = j["bomb_pickup"]
                if bp:
                    bp.update(ahora)
                    if not bp.active:
                        j["bomb_pickup"] = None
                        j["next_bomb_spawn_time"] = min(j["next_bomb_spawn_time"], ahora + 1200)
                    elif bp.rect.colliderect(p.rect):
                        # disparo automático
                        px, py = p.rect.centerx, p.rect.top
                        j["bombs"].append(BombProjectile(px, py, boss.rect))
                        reproducir(self.snd_power)
                        j["bomb_pickup"] = None

                # bombas activas
                for bomb in j["bombs"][:]:
                    before_hp = boss.hp
                    bomb.update(ahora, boss, self.camera)
                    if bomb.exploded and before_hp > boss.hp:
                        reproducir(self.snd_expl)  # suena solo al impactar
                    if not bomb.active:
                        j["bombs"].remove(bomb)

                # daño al jugador (láser + balas)
                if ahora >= j["invulnerable_hasta"]:
                    if boss.attack_mode == 4 and boss.laser_active and boss.laser_rect:
                        elapsed = ahora - boss.laser_start_t
                        if elapsed >= boss.laser_warn_ms:
                            if boss.laser_rect.colliderect(p.rect):
                                j["vidas"] -= 1
                                j["invulnerable_hasta"] = ahora + j["invulnerable_ms"]
                                reproducir(self.snd_expl)
                                self.camera.trigger_shake(220, 10)
                                p.rect.centerx = ANCHO//2; p.rect.bottom = ALTO-10
                                p.angle = p.target_angle = 0.0

                    for b in bb[:]:
                        if b["rect"].colliderect(p.rect):
                            bb.remove(b)
                            j["vidas"] -= 1
                            j["invulnerable_hasta"] = ahora + j["invulnerable_ms"]
                            reproducir(self.snd_expl)
                            self.camera.trigger_shake(220, 10)
                            p.rect.centerx = ANCHO//2; p.rect.bottom = ALTO-10
                            p.angle = p.target_angle = 0.0
                            break

                # muerte del boss
                if boss.hp <= 0:
                    j["boss_active"] = False
                    j["boss_threshold_cleared"].add(j["nivel"])
                    j["boss"] = None
                    j["boss_bullets"].clear()
                    j["bombs"].clear()
                    j["bomb_pickup"] = None
                    j["puntaje"] += 100
                    j["nivel"] += 1
                    j["vel_enemigo_base"] += 0.8
                    if len(j["enemigos"]) < 12:
                        j["enemigos"] += crear_enemigos(1)
                    self.bg.switch_to_main()
                    self.estado = LEVEL_INTRO
                    self.activar_pantalla_nivel(ahora)

            # fin de juego
            if j["vidas"] <= 0 and self.estado in (JUGANDO, BOSS_INTRO):
                self.estado = GAME_OVER
                if not j["game_over_sonido_reproducido"]:
                    reproducir(self.snd_over)
                    j["game_over_sonido_reproducido"] = True
                if j["puntaje"] > self.hiscore:
                    self.hiscore = j["puntaje"]
                    guardar_hiscore(self.hiscore)

        # menú estrellas
        if self.estado == MENU:
            self.starfield.update(dt)

    # -------------------------
    # DRAW
    # -------------------------
    def draw(self):
        if self.estado in (JUGANDO, BOSS_INTRO, GAME_OVER, MENU):
            self.bg.draw(self.win)

        if self.estado == MENU:
            draw_menu(self.win, self.fuente_titulo, self.fuente, self.hiscore, self.starfield, pygame.time.get_ticks())
            return

        if self.estado == LEVEL_INTRO:
            self.win.fill((0,0,0))
            dibujar_texto(self.win, self.juego["intro_text"], self.fuente_grande, (255,255,255), ANCHO//2, ALTO//2 - 10, centrado=True)
            dibujar_texto(self.win, "¡Vidas reiniciadas!", self.fuente, (255,215,0), ANCHO//2, ALTO//2 + 40, centrado=True)
            return

        if self.estado in (JUGANDO, PAUSA, BOSS_INTRO):
            j = self.juego
            p = j["player"]

            # Nave
            visible = True
            if self.estado != PAUSA and pygame.time.get_ticks() < j["invulnerable_hasta"]:
                visible = ((pygame.time.get_ticks() // 100) % 2 == 0)
            p.draw(self.win, self.camera, visible=visible)

            # Balas jugador
            for bala in j["balas"]:
                pygame.draw.rect(self.win, (255,255,255), self.camera.apply_rect(bala))

            if not j["boss_active"]:
                for en in j["enemigos"]:
                    pygame.draw.rect(self.win, (255,0,0), self.camera.apply_rect(en))
                for pu in j["powerups"]:
                    pu.draw(self.win, self.fuente, self.camera)
            else:
                j["boss"].draw(self.win, pygame.time.get_ticks(), self.camera)
                for b in j["boss_bullets"]:
                    color = (255,140,0)
                    t = b.get("type","normal")
                    if t == "wave": color = (255,200,0)
                    elif t == "aim": color = (255,80,80)
                    elif t == "spread": color = (255,160,60)
                    elif t == "burst": color = (255,100,0)
                    pygame.draw.rect(self.win, color, self.camera.apply_rect(b["rect"]))
                if j["bomb_pickup"]:
                    j["bomb_pickup"].draw(self.win, self.camera)

            for bomb in j["bombs"]:
                bomb.draw(self.win, self.camera)

            # HUD
            draw_hud(self.win, self.fuente, j, self.muted)

            if self.estado == PAUSA:
                self.win.fill((0,0,0))
                dibujar_texto(self.win, "PAUSA", self.fuente_grande, (255,215,0), ANCHO//2, ALTO//2 - 40, centrado=True)
                dibujar_texto(self.win, "ENTER reanudar | R reiniciar | ESC salir", self.fuente, (255,255,255), ANCHO//2, ALTO//2 + 20, centrado=True)

            if self.estado == BOSS_INTRO and j["boss_active"] and j["boss"]:
                draw_letterbox(self.win, alpha=200, size=90)
                t_left = max(0, j["boss_intro_end"] - pygame.time.get_ticks())
                k = 1.0 - max(0.0, min(1.0, t_left / BOSS_INTRO_MS))
                bx, by, bw, bh = j["boss"].rect
                pad = int(40 + 40 * (1.0 - k))
                focus = pygame.Rect(bx - pad, by - pad, bw + pad*2, bh + pad*2)
                focus = self.camera.apply_rect(focus)
                draw_focus_ring(self.win, focus, color=(255,255,255), width=3)
                dibujar_texto(self.win, "¡ALERTA JEFE!", self.fuente_grande, (255,0,0), ANCHO//2, 130, centrado=True)

        if self.estado == GAME_OVER:
            self.win.fill((0,0,0))
            dibujar_texto(self.win, "GAME OVER", self.fuente_grande, (255,0,0), ANCHO//2, ALTO//2 - 80, centrado=True)
            dibujar_texto(self.win, f"Puntaje: {self.juego['puntaje']}", self.fuente, (255,255,255), ANCHO//2, ALTO//2 - 10, centrado=True)
            dibujar_texto(self.win, f"Mejor puntaje: {self.hiscore}", self.fuente, (0,120,255), ANCHO//2, ALTO//2 + 20, centrado=True)
            dibujar_texto(self.win, "R para reiniciar", self.fuente, (255,255,255), ANCHO//2, ALTO//2 + 70, centrado=True)
            dibujar_texto(self.win, "ENTER para volver al menú | ESC salir", self.fuente, (255,255,255), ANCHO//2, ALTO//2 + 100, centrado=True)
