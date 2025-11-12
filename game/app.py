# game/app.py
import pygame, random, math
from .constants import *
from .utils import cargar_sonido, reproducir, dibujar_texto, leer_hiscore, guardar_hiscore, load_font
from .background import AnimatedBackground
from .camera import Camera
from .assets import init_after_display
from .state import reset_juego, activar_pantalla_nivel
from .entities.enemy import respawnear_enemigo, crear_enemigos
from .entities.powerups import PowerUp, BombPickup, BombProjectile
from .entities.boss import Boss
from .audio import play_music, Volumes
from .menu_bg import MenuBG
from .ui_helpers import draw_letterbox, draw_focus_ring, draw_slider
from .character import CharacterSelect
from .shooting import shoot_pattern
from .gif import load_gif_frames

# Estado adicional sin tocar constants.py
LEVEL_SELECT = "LEVEL_SELECT"

class GameApp:
    def __init__(self):
        # Ventana y fuentes
        self.ventana = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()

        self.fuente = load_font(24)
        self.fuente_grande = load_font(48)
        self.fuente_titulo = load_font(56)

        # Carga de imágenes/GIFs tras set_mode
        init_after_display()

        # Sonidos SFX
        self.s_gameover = cargar_sonido("assets/music/game-over.mp3", 0.6)
        self.s_disparo  = cargar_sonido("assets/music/laser-shot-ingame-230500.mp3", 0.4)
        self.s_explosion= cargar_sonido("assets/music/break.mp3", 0.5)
        self.s_power    = cargar_sonido("assets/music/powerup.mp3", 0.6)

        # Módulos auxiliares
        # NOTA: el fondo de juego (self.bg) se re-crea cuando eliges planeta
        self.bg = AnimatedBackground("assets/scenes/fondo.gif", "assets/scenes/fondo-gf.gif")
        self.menu_bg = MenuBG("assets/scenes/space.gif")
        self.cam = Camera()
        self.vol = Volumes(self.s_gameover, self.s_disparo, self.s_explosion, self.s_power)

        # Música
        play_music("assets/music/game.mp3", volume=0.5, loop=True, fade_ms=800)

        # Hiscore & Estado
        self.hiscore = leer_hiscore()
        self.juego = reset_juego()
        # Reiniciar cualquier referencia al jefe anterior
        self.juego["boss"] = None
        self.juego["boss_active"] = False
        self.juego["boss_threshold_cleared"].clear()

        # Menús
        self.estado = MENU_MAIN
        self.menu_main_items = ["INICIO", "PERSONAJE", "DIFICULTAD", "OPCIONES"]
        self.menu_main_index = 0

        # Dificultad
        self.difficulty_name = "MEDIA"

        # Opciones
        self.options_items = ["Volumen Maestro", "Efectos (SFX)", "Música"]
        self.options_index = 0

        # Personajes
        self.character = CharacterSelect()  # maneja selected_ship, previews, UI

        # Selección de nivel (planetas)
        self.level_selected = 1
        self._init_planet_select()

        # Varios
        self.fullscreen = False

    # -----------------
    # Inicializar mini-menú de planetas
    # -----------------
    def _init_planet_select(self):
        # Fondo del selector
        try:
            img = pygame.image.load("assets/scenes/plants/espacio.png").convert()
            self.planet_bg = pygame.transform.smoothscale(img, (ANCHO, ALTO))
        except Exception:
            self.planet_bg = None

        # Carga de iconos de planetas 1..8 (png)
        self.planets = []
        self.planet_rects = []
        for i in range(1, 9):
            path = f"assets/scenes/plants/{i}.png"
            try:
                img = pygame.image.load(path).convert_alpha()
            except Exception:
                # placeholder
                img = pygame.Surface((88, 88), pygame.SRCALPHA)
                pygame.draw.circle(img, (120, 180, 255), (44, 44), 44)
                dibujar_texto(img, str(i), self.fuente_grande, (0,0,40), 44, 44, centrado=True)
            # tamaño uniforme (sin perder proporción)
            img = pygame.transform.smoothscale(img, (88, 88))
            self.planets.append(img)

        # Disposición: 2 filas x 4 columnas
        self.planet_rects.clear()
        margin_x = 80
        spacing_x = (ANCHO - margin_x*2) // 3  # 4 columnas => 3 espacios
        row_y_top = ALTO//2 - 110
        row_y_bottom = ALTO//2 + 40
        positions = []
        for col in range(4):
            x = margin_x + col * spacing_x
            positions.append((x, row_y_top))
        for col in range(4):
            x = margin_x + col * spacing_x
            positions.append((x, row_y_bottom))
        # centrar iconos y crear rects
        for i, (x, y) in enumerate(positions[:8]):
            rect = self.planets[i].get_rect(center=(x, y))
            self.planet_rects.append(rect)

        self.planet_index = 0  # resaltado actual
        # Flecha (triángulo) encima del planeta seleccionado
        self.arrow_offset = -70  # distancia vertical sobre el centro del planeta

    # -----------------
    # Helpers de juego
    # -----------------
    def get_diff_mul(self):
        d = DIFFICULTY_PRESETS.get(self.difficulty_name, DIFFICULTY_PRESETS["MEDIA"])
        return d["enemy_speed"], d["boss_hp"]

    def _apply_level_background(self, level_n: int):
        """Crea el AnimatedBackground del nivel elegido."""
        # fondo principal del nivel N
        # soporta .png/.gif indistintamente (load_gif_frames debe manejar 1 frame si es png)
        main_path_candidates = [f"assets/scenes/fondo-{level_n}.gif",
                                f"assets/scenes/fondo-{level_n}.png"]
        # el boss usa 'fondo-gf.gif' como antes
        boss_path = "assets/scenes/fondo-gf.gif"
        # escoger el primero existente
        chosen = None
        for p in main_path_candidates:
            try:
                with open(p, "rb"):
                    chosen = p; break
            except Exception:
                continue
        if not chosen:
            chosen = "assets/scenes/fondo.gif"  # fallback
        self.bg = AnimatedBackground(chosen, boss_path)

    # -----------------
    # Loop principal
    # -----------------
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            ahora = pygame.time.get_ticks()

            # Cámara suave
            if self.juego.get("player"):
                tx, ty = self.cam.target_from_player(self.juego["player"].rect, ANCHO, ALTO)
                self.cam.update(tx, ty)

            # Fondos
            if self.estado in (MENU_MAIN, MENU_OPTIONS, MENU_DIFFICULTY, MENU_CHARACTER):
                self.menu_bg.update(dt)  # Actualiza animación + zoom del fondo
                self.menu_bg.draw(self.ventana)  # Dibuja el fondo con zoom
            elif self.estado == LEVEL_SELECT:
                self.menu_bg.update(dt)  # Mantiene la animación + zoom
                self.menu_bg.draw(self.ventana)  # Dibuja el fondo con zoom y movimiento
            elif self.estado in (LEVEL_INTRO, JUGANDO, BOSS_INTRO, PAUSA, GAME_OVER, STORY_INTRO):
                self.bg.update(dt)
                self.bg.draw(self.ventana)
            # Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    running = False
                elif evento.type == pygame.KEYDOWN:
                    running = self.handle_keydown(evento, ahora, running)
                elif evento.type == pygame.MOUSEBUTTONDOWN and self.estado == LEVEL_SELECT:
                    self.handle_level_click(evento.pos, ahora)

            # Lógica principal
            self.update_logic(dt, ahora)

            # Dibujo
            self.draw_scene(ahora)

            pygame.display.flip()


    def activar_pantalla_nivel(juego, ahora):
        juego["intro_end_time"] = ahora + 3000

    # -----------------
    # Eventos teclado
    # -----------------
    def handle_keydown(self, evento, ahora, running):
        if evento.key == pygame.K_F11:
            self.fullscreen = not self.fullscreen
            flags = pygame.FULLSCREEN if self.fullscreen else 0
            self.ventana = pygame.display.set_mode((ANCHO, ALTO), flags)

        if evento.key == pygame.K_m:
            self.vol.muted = not self.vol.muted
            self.vol.apply()

        if evento.key == pygame.K_ESCAPE:
            if self.estado in (JUGANDO, PAUSA):
                self.estado = PAUSA if self.estado == JUGANDO else JUGANDO
            elif self.estado in (MENU_OPTIONS, MENU_DIFFICULTY, MENU_CHARACTER, LEVEL_INTRO, BOSS_INTRO, GAME_OVER):
                self.estado = MENU_MAIN
            elif self.estado == LEVEL_SELECT:
                # volver al menú principal desde el selector
                self.estado = MENU_MAIN
            elif self.estado == MENU_MAIN:
                return False  # salir

        # MENÚ PRINCIPAL
        if self.estado == MENU_MAIN:
            if evento.key in (pygame.K_UP, pygame.K_w):
                self.menu_main_index = (self.menu_main_index - 1) % len(self.menu_main_items)
            if evento.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_main_index = (self.menu_main_index + 1) % len(self.menu_main_items)
            if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                sel = self.menu_main_items[self.menu_main_index]
                if sel == "INICIO":
                    # Ir al mini-menú de planetas
                    self.estado = LEVEL_SELECT
                    # reset de cursor por si acaso
                    self.planet_index = (self.juego["nivel"] - 1) % 8
                elif sel == "PERSONAJE":
                    self.estado = MENU_CHARACTER
                elif sel == "DIFICULTAD":
                    self.estado = MENU_DIFFICULTY
                elif sel == "OPCIONES":
                    self.estado = MENU_OPTIONS

        # MENÚ PERSONAJE
        elif self.estado == MENU_CHARACTER:
            decide = self.character.handle_input(evento)
            if decide == "APPLY":
                self.character.apply_selected_skin()
                self.estado = MENU_MAIN

        # MENÚ OPCIONES
        elif self.estado == MENU_OPTIONS:
            if evento.key in (pygame.K_UP, pygame.K_w):
                self.options_index = (self.options_index - 1) % len(self.options_items)
            if evento.key in (pygame.K_DOWN, pygame.K_s):
                self.options_index = (self.options_index + 1) % len(self.options_items)
            if evento.key in (pygame.K_LEFT, pygame.K_a):
                if self.options_index == 0: self.vol.master = max(0.0, self.vol.master - 0.05)
                elif self.options_index == 1: self.vol.sfx    = max(0.0, self.vol.sfx    - 0.05)
                elif self.options_index == 2: self.vol.music  = max(0.0, self.vol.music  - 0.05)
                self.vol.apply()
            if evento.key in (pygame.K_RIGHT, pygame.K_d):
                if self.options_index == 0: self.vol.master = min(1.0, self.vol.master + 0.05)
                elif self.options_index == 1: self.vol.sfx    = min(1.0, self.vol.sfx    + 0.05)
                elif self.options_index == 2: self.vol.music  = min(1.0, self.vol.music  + 0.05)
                self.vol.apply()
            if evento.key == pygame.K_RETURN:
                self.estado = MENU_MAIN

        # MENÚ DIFICULTAD
        elif self.estado == MENU_DIFFICULTY:
            if evento.key in (pygame.K_UP, pygame.K_w):
                i = DIFFICULTY_ORDER.index(self.difficulty_name)
                self.difficulty_name = DIFFICULTY_ORDER[(i - 1) % len(DIFFICULTY_ORDER)]
            if evento.key in (pygame.K_DOWN, pygame.K_s):
                i = DIFFICULTY_ORDER.index(self.difficulty_name)
                self.difficulty_name = DIFFICULTY_ORDER[(i + 1) % len(DIFFICULTY_ORDER)]
            if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.estado = MENU_MAIN

        # SELECTOR DE NIVEL (planetas)
        elif self.estado == LEVEL_SELECT:
            if evento.key in (pygame.K_LEFT, pygame.K_a):
                self.planet_index = (self.planet_index - 1) % 8
            if evento.key in (pygame.K_RIGHT, pygame.K_d):
                self.planet_index = (self.planet_index + 1) % 8
            if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._choose_level(self.planet_index + 1, ahora)

        # PAUSA
        elif self.estado == PAUSA:
            if evento.key == pygame.K_RETURN:
                self.estado = JUGANDO
            if evento.key == pygame.K_r:
                self.juego = reset_juego()
                if self.difficulty_name == "EXTREMA" and len(self.juego["enemigos"]) < 12:
                    self.juego["enemigos"] += crear_enemigos(2)
                self.estado = LEVEL_INTRO
                activar_pantalla_nivel(self.juego, ahora)
                self.juego["intro_text"] = "NIVEL 1"
                play_music("assets/music/game.mp3", volume=self.vol.music_effective(), loop=True, fade_ms=500)

        # GAME OVER
        elif self.estado == GAME_OVER:
            if evento.key == pygame.K_r:
                self.juego = reset_juego()
                if self.difficulty_name == "EXTREMA" and len(self.juego["enemigos"]) < 12:
                    self.juego["enemigos"] += crear_enemigos(2)
                self.estado = LEVEL_INTRO
                activar_pantalla_nivel(self.juego, ahora)
                self.juego["intro_text"] = "NIVEL 1"
                play_music("assets/music/game.mp3", volume=self.vol.music_effective(), loop=True, fade_ms=500)
            if evento.key == pygame.K_RETURN:
                self.estado = MENU_MAIN
                play_music("assets/music/game.mp3", volume=self.vol.music_effective(), loop=True, fade_ms=500)

        # JUGANDO
        elif self.estado == JUGANDO:
            if evento.key == pygame.K_RETURN:
                self.estado = PAUSA
            if evento.key == pygame.K_SPACE:
                if ahora - self.juego["ultimo_disparo"] >= self.juego["cadencia_ms"]:
                    shoot_pattern(self.juego, self.character.selected_ship)  # patrón por nave
                    self.juego["ultimo_disparo"] = ahora
                    reproducir(self.s_disparo)

        return running

    # -----------------
    # Click en planetas
    # -----------------
    def handle_level_click(self, mouse_pos, ahora):
        for i, rect in enumerate(self.planet_rects):
            if rect.collidepoint(mouse_pos):
                self.planet_index = i
                self._choose_level(i + 1, ahora)
                break

    def _choose_level(self, level_n: int, ahora):
        self.level_selected = level_n
        # Reinicia juego y aplica nivel
        self.juego = reset_juego()
        self.juego["nivel"] = level_n  # forzar que el nivel mostrado sea el elegido
        activar_pantalla_nivel(self.juego, ahora)
        self.juego["intro_text"] = f"NIVEL {level_n}"
        # Cargar fondo por nivel
        self._apply_level_background(level_n)
        # Música Main
        play_music("assets/music/game.mp3", volume=self.vol.music_effective(), loop=True, fade_ms=500)
        # Avanzar a pantalla de intro
        # Si es el primer planeta, mostrar historia
        if level_n == 1:
            self.estado = STORY_INTRO
            self.story_start_time = ahora
            self.story_duration = 7000  # duración de la narración en ms
        else:
            self.estado = LEVEL_INTRO

    # -----------------
    # Update lógica
    # -----------------
    def update_logic(self, dt, ahora):
        estado = self.estado                
        if estado == MENU_CHARACTER:
            self.character.update(dt)
        j = self.juego
        
        if estado == STORY_INTRO:
            # Esperar unos segundos antes de pasar al nivel
            if ahora - self.story_start_time >= self.story_duration:
                self.estado = LEVEL_INTRO
        
        if estado == LEVEL_INTRO:
            if ahora >= j["intro_end_time"]:
                self.estado = JUGANDO

        elif estado == BOSS_INTRO:
            if ahora >= j["boss_intro_end"]:
                self.estado = JUGANDO

        elif estado == JUGANDO:
            keys = pygame.key.get_pressed()

            # Buffs
            s_activo = ahora < j["s_active_until"]
            f_activo = ahora < j["f_active_until"]
            p_activo = ahora < j["p_active_until"]

            j["player"].vel = j["player"].vel_base + (3 if s_activo else 0)
            j["cadencia_ms"] = 100 if p_activo else 200
            j["player"].update(dt, keys)

            enemy_mul, boss_mul = self.get_diff_mul()

            # ¿Aparece jefe?
            needed_points = BOSS_POINTS_PER_LEVEL * j["nivel"]
            if (j["puntaje"] >= needed_points
                and j["nivel"] not in j["boss_threshold_cleared"]
                and not j["boss_active"]):
                j["boss"] = Boss(j["nivel"], difficulty_hp_mul=boss_mul)
                if self.difficulty_name == "EXTREMA":
                    j["boss"].fire_cd_ms = max(220, int(j["boss"].fire_cd_ms * 0.60))
                    j["boss"].pattern_duration = int(j["boss"].pattern_duration * 0.80)
                    j["boss"].move_speed *= 1.25
                j["boss_active"] = True
                self.bg.switch_to_boss()
                play_music("assets/music/boss.mp3", volume=self.vol.music_effective(), loop=True, fade_ms=700)
                self.estado = BOSS_INTRO
                j["boss_intro_end"] = ahora + BOSS_INTRO_MS
                j["next_bomb_spawn_time"] = ahora + BOSS_INTRO_MS + 200

            # --- SIN JEFE ---
            if not j["boss_active"]:
                # balas jugador
                for bala in j["balas"][:]:
                    if not bala.update():
                        j["balas"].remove(bala)

                # enemigos
                vel_enemigo = (j["vel_enemigo_base"] + (j["nivel"] - 1) * 0.9) * enemy_mul
                if f_activo and keys[pygame.K_f]:
                    vel_enemigo *= 0.45

                for enemigo in j["enemigos"]:
                    enemigo.update(dt, vel_enemigo)
                    if enemigo.rect.top > ALTO:
                        respawnear_enemigo(enemigo)

                # colisiones balas/enemigos
                for bala in j["balas"][:]:
                    impactado = None
                    for enemigo in j["enemigos"]:
                        if bala.rect.colliderect(enemigo.rect):
                            impactado = enemigo; break
                    if impactado:
                        try: j["balas"].remove(bala)
                        except ValueError: pass
                        drop_x, drop_y = impactado.rect.centerx, impactado.rect.centery
                        respawnear_enemigo(impactado)
                        j["puntaje"] += 10
                        reproducir(self.s_explosion)
                        if random.random() < 0.12:
                            tipo = random.choice(['S', 'F', 'P'])
                            j["powerups"].append(PowerUp(tipo, drop_x, drop_y))
                            reproducir(self.s_power)

                # daño al jugador por choque
                if ahora >= j["invulnerable_hasta"]:
                    for enemigo in j["enemigos"]:
                        if j["player"].rect.colliderect(enemigo.rect):
                            j["vidas"] -= 1
                            j["invulnerable_hasta"] = ahora + j["invulnerable_ms"]
                            respawnear_enemigo(enemigo)
                            reproducir(self.s_explosion)
                            j["player"].rect.centerx = ANCHO // 2
                            j["player"].rect.bottom = ALTO - 10
                            j["player"].angle = 0.0
                            j["player"].target_angle = 0.0
                            break

                # powerups
                for pu in j["powerups"][:]:
                    if not pu.update():
                        j["powerups"].remove(pu); continue
                    if pu.rect.colliderect(j["player"].rect):
                        if pu.tipo == 'S': j["s_active_until"] = ahora + 8000
                        elif pu.tipo == 'F': j["f_active_until"] = ahora + 8000
                        elif pu.tipo == 'P': j["p_active_until"] = ahora + 8000
                        try: j["powerups"].remove(pu)
                        except ValueError: pass
                        reproducir(self.s_power)

            # --- CON JEFE ---
            else:
                boss = j["boss"]
                boss_bullets = j["boss_bullets"]

                for bala in j["balas"][:]:
                    if not bala.update():
                        j["balas"].remove(bala)

                boss.update(dt, ahora, j["player"].rect, boss_bullets)

                # daño al jefe
                for bala in j["balas"][:]:
                    if boss.rect.colliderect(bala.rect):
                        try: j["balas"].remove(bala)
                        except ValueError: pass
                        boss.hp -= 10
                        reproducir(self.s_explosion)

                # balas del boss
                for b in boss_bullets[:]:
                    r = b["rect"]; t = b.get("type","normal")
                    if t == "wave":
                        b["phase"] = b.get("phase",0.0) + b.get("phase_speed",0.12)
                        r.x += int(3.2 * math.sin(b["phase"]))
                        r.y += int(b["vy"])
                    else:
                        r.x += int(b["vx"]); r.y += int(b["vy"])
                    if r.top > ALTO or r.right < 0 or r.left > ANCHO:
                        boss_bullets.remove(b)

                # === BOMB PICKUP ===
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
                    elif bp.rect.colliderect(j["player"].rect):
                        px, py = j["player"].rect.centerx, j["player"].rect.top
                        j["bombs"].append(BombProjectile(px, py, boss.rect, reproducir, self.s_explosion))
                        j["bomb_pickup"] = None
                        reproducir(self.s_power)

                for bomb in j["bombs"][:]:
                    bomb.update(ahora, boss)
                    if not bomb.active:
                        j["bombs"].remove(bomb)

                # daño al jugador
                if ahora >= j["invulnerable_hasta"]:
                    if boss.attack_mode == 4 and boss.laser_active and boss.laser_rect:
                        elapsed = ahora - boss.laser_start_t
                        if elapsed >= boss.laser_warn_ms:
                            if boss.laser_rect.colliderect(j["player"].rect):
                                j["vidas"] -= 1
                                j["invulnerable_hasta"] = ahora + j["invulnerable_ms"]
                                reproducir(self.s_explosion)
                                j["player"].rect.centerx = ANCHO // 2
                                j["player"].rect.bottom = ALTO - 10
                                j["player"].angle = 0.0
                                j["player"].target_angle = 0.0
                    for b in boss_bullets[:]:
                        if b["rect"].colliderect(j["player"].rect):
                            boss_bullets.remove(b)
                            j["vidas"] -= 1
                            j["invulnerable_hasta"] = ahora + j["invulnerable_ms"]
                            reproducir(self.s_explosion)
                            j["player"].rect.centerx = ANCHO // 2
                            j["player"].rect.bottom = ALTO - 10
                            j["player"].angle = 0.0
                            j["player"].target_angle = 0.0

                # derrota del boss
                if boss.hp <= 0:
                    j["boss_active"] = False
                    j["boss_threshold_cleared"].add(j["nivel"])
                    j["boss"] = None; j["boss_bullets"].clear()
                    j["bombs"].clear(); j["bomb_pickup"] = None
                    j["puntaje"] += 100
                    j["nivel"] += 1
                    j["vel_enemigo_base"] += 0.8
                    if len(j["enemigos"]) < 12:
                        j["enemigos"] += crear_enemigos(1)
                    self.bg.switch_to_main()
                    play_music("assets/music/game.mp3", volume=self.vol.music_effective(), loop=True, fade_ms=700)
                    self.estado = LEVEL_INTRO
                    activar_pantalla_nivel(j, ahora)

            # ¿Sin vidas?
            if j["vidas"] <= 0 and self.estado in (JUGANDO, BOSS_INTRO):
                self.estado = GAME_OVER
                if self.s_gameover:
                    reproducir(self.s_gameover)
                play_music("assets/music/game.mp3", volume=self.vol.music_effective(), loop=True, fade_ms=600)
                if j["puntaje"] > self.hiscore:
                    self.hiscore = j["puntaje"]; guardar_hiscore(self.hiscore)

    # -----------------
    # Draw
    # -----------------
    def draw_scene(self, ahora):
        # Fondo
        if self.estado in (MENU_MAIN, MENU_OPTIONS, MENU_DIFFICULTY, MENU_CHARACTER):
            self.menu_bg.draw(self.ventana)
        elif self.estado == LEVEL_SELECT:
            if self.planet_bg:
                self.ventana.blit(self.planet_bg, (0, 0))
            else:
                self.ventana.fill((0,0,0))
        else:
            if self.estado in (JUGANDO, BOSS_INTRO, GAME_OVER, LEVEL_INTRO, PAUSA):
                self.bg.draw(self.ventana)

        # Capas por estado
        if self.estado == MENU_MAIN:
            card = pygame.Rect(0, 0, 560, 420); card.center = (ANCHO//2, ALTO//2 - 20)
            pygame.draw.rect(self.ventana, GRIS, card, border_radius=18)
            pygame.draw.rect(self.ventana, (70,70,85), card.inflate(8,8), 4, border_radius=22)
            dibujar_texto(self.ventana, GAME_TITLE.upper(), self.fuente_titulo, ORO, ANCHO//2, card.top + 65, centrado=True)
            for i, label in enumerate(self.menu_main_items):
                color = AMARILLO if i == self.menu_main_index else BLANCO
                dibujar_texto(self.ventana, label, self.fuente_grande, color, ANCHO//2, card.top + 140 + i*55, centrado=True)
            from .constants import SHIP_DISPLAY
            dibujar_texto(self.ventana, f"Personaje: {SHIP_DISPLAY[self.character.selected_ship]}", self.fuente, AMARILLO, ANCHO//2, card.bottom - 60, centrado=True)
            dibujar_texto(self.ventana, "Créditos: created by TodTete", self.fuente, BLANCO, ANCHO//2, card.bottom - 20, centrado=True)

        elif self.estado == MENU_CHARACTER:
            self.character.draw(self.ventana, self.fuente_titulo, self.fuente)

        elif self.estado == MENU_OPTIONS:
            dibujar_texto(self.ventana, "OPCIONES", self.fuente_titulo, MORADO, ANCHO//2, 80, centrado=True)
            labels = [
                f"{self.options_items[0]}: {int(self.vol.master*100)}%",
                f"{self.options_items[1]}: {int(self.vol.sfx*100)}%",
                f"{self.options_items[2]}: {int(self.vol.music*100)}%",
            ]
            start_y = 180; spacing = 70; slider_w = 360
            for i, text in enumerate(labels):
                y = start_y + i*spacing
                color = AMARILLO if i == self.options_index else BLANCO
                dibujar_texto(self.ventana, text, self.fuente_grande, color, ANCHO//2, y - 28, centrado=True)
                val = [self.vol.master, self.vol.sfx, self.vol.music][i]
                draw_slider(self.ventana, ANCHO//2 - slider_w//2, y, slider_w, val, i==self.options_index)
            dibujar_texto(self.ventana, "←/→ ajusta, ↑/↓ selecciona, ENTER volver", self.fuente, AZUL, ANCHO//2, ALTO - 60, centrado=True)

        elif self.estado == MENU_DIFFICULTY:
            dibujar_texto(self.ventana, "DIFICULTAD", self.fuente_titulo, MORADO, ANCHO//2, 90, centrado=True)
            for i, name in enumerate(DIFFICULTY_ORDER):
                color = AMARILLO if name == self.difficulty_name else BLANCO
                dibujar_texto(self.ventana, name, self.fuente_grande, color, ANCHO//2, 180 + i*60, centrado=True)
            dibujar_texto(self.ventana, "↑/↓ selecciona, ENTER volver", self.fuente, AZUL, ANCHO//2, ALTO - 60, centrado=True)

        elif self.estado == LEVEL_SELECT:
            # Título
            dibujar_texto(self.ventana, "ELIGE TU PLANETA", self.fuente_titulo, ORO, ANCHO//2, 70, centrado=True)
            # Render de planetas + flecha
            for i, img in enumerate(self.planets):
                self.ventana.blit(img, self.planet_rects[i])

            # Flecha sobre el seleccionado (triángulo)
            sel_rect = self.planet_rects[self.planet_index]
            arrow_x = sel_rect.centerx
            arrow_y = sel_rect.top + self.arrow_offset
            pts = [(arrow_x, arrow_y),
                   (arrow_x - 16, arrow_y + 24),
                   (arrow_x + 16, arrow_y + 24)]
            pygame.draw.polygon(self.ventana, AMARILLO, pts)
            pygame.draw.polygon(self.ventana, (90, 70, 0), pts, 2)

            # Bordes sutiles en todos, más fuerte en el seleccionado
            for i, r in enumerate(self.planet_rects):
                pygame.draw.rect(self.ventana, (120,120,150), r.inflate(10,10), 2, border_radius=18)
            pygame.draw.rect(self.ventana, AMARILLO, sel_rect.inflate(14,14), 3, border_radius=20)

            # Leyenda
            dibujar_texto(self.ventana, "←/→ para mover  |  ENTER o clic para seleccionar  |  ESC volver",
                          self.fuente, BLANCO, ANCHO//2, ALTO - 50, centrado=True)

        #33333333
        elif self.estado == STORY_INTRO:
            self.ventana.fill((0,0,0))
            personaje = self.character.selected_ship
            ruta_img = {
                "BRAYAN": "assets/personajes/personaje-b.png",
                "MARLIN": "assets/personajes/personaje-m.png",
                "FERNANDA": "assets/personajes/personaje-f.png",
                "TETE": "assets/personajes/personaje-t.png",
            }.get(personaje, "assets/personajes/personaje-b.png")

            try:
                img = pygame.image.load(ruta_img).convert_alpha()
                img = pygame.transform.smoothscale(img, (300, 300))
                rect = img.get_rect(center=(ANCHO//2, ALTO//2 - 80))
                self.ventana.blit(img, rect)
            except Exception as e:
                print(f"[AVISO] No se pudo cargar la imagen del personaje: {e}")

        # Texto narrativo
            historia = [
                "Un ser oscuro llamado DOOM ha surgido...",
                "Su objetivo: conquistar el sistema solar.",
                "Con tu ayuda, deberás enfrentar a sus androides",
                "y liberar los planetas de la lluvia de asteroides",
            ]
            y = ALTO//2 + 100
            for linea in historia:
                dibujar_texto(self.ventana, linea, self.fuente, BLANCO, ANCHO//2, y, centrado=True)
                y += 35

            dibujar_texto(self.ventana, "Presiona cualquier tecla para continuar...", self.fuente, AMARILLO, ANCHO//2, ALTO - 60, centrado=True)

        elif self.estado == LEVEL_INTRO:
            self.ventana.fill(NEGRO)
            dibujar_texto(self.ventana, self.juego["intro_text"], self.fuente_grande, BLANCO, ANCHO//2, ALTO//2 - 10, centrado=True)
            dibujar_texto(self.ventana, f"¡Vidas reiniciadas!  Dificultad: {self.difficulty_name}", self.fuente, AMARILLO, ANCHO//2, ALTO//2 + 40, centrado=True)

        elif self.estado in (JUGANDO, PAUSA, BOSS_INTRO):
            visible = True
            if self.estado != PAUSA and pygame.time.get_ticks() < self.juego["invulnerable_hasta"]:
                visible = ((ahora // 100) % 2 == 0)
            self.juego["player"].draw(self.ventana, self.cam.apply_point, visible=visible)

            for bala in self.juego["balas"]:
                bala.draw(self.ventana, self.cam.apply_rect)

            if not self.juego["boss_active"]:
                for enemigo in self.juego["enemigos"]:
                    enemigo.draw(self.ventana, self.cam.apply_rect)
                for pu in self.juego["powerups"]:
                    pu.draw(self.ventana, self.fuente, self.cam.apply_rect, self.cam.apply_point, dibujar_texto, NEGRO)
            else:
                self.juego["boss"].draw(self.ventana, self.cam.apply_rect, ahora)
                for b in self.juego["boss_bullets"]:
                    color = (255,140,0)
                    t = b.get("type","normal")
                    if t == "wave": color = (255,200,0)
                    elif t == "aim": color = (255,80,80)
                    elif t == "spread": color = (255,160,60)
                    elif t == "burst": color = (255,100,0)
                    pygame.draw.rect(self.ventana, color, self.cam.apply_rect(b["rect"]))
                if self.juego["bomb_pickup"]:
                    self.juego["bomb_pickup"].draw(self.ventana, self.cam.apply_rect)

            for bomb in self.juego["bombs"]:
                bomb.draw(self.ventana, self.cam.apply_rect, self.cam.apply_point)

            # HUD
            dibujar_texto(self.ventana, f"Puntaje: {self.juego['puntaje']}", self.fuente, BLANCO, 10, 10)
            dibujar_texto(self.ventana, f"Nivel: {self.juego['nivel']}", self.fuente, BLANCO, 10, 40)
            dibujar_texto(self.ventana, f"Vidas: {self.juego['vidas']}", self.fuente, BLANCO, 10, 70)
            if self.vol.muted: dibujar_texto(self.ventana, "MUTED", self.fuente, ROJO, ANCHO - 90, 10)
            if not self.juego["boss_active"]:
                need = BOSS_POINTS_PER_LEVEL * self.juego["nivel"]
                dibujar_texto(self.ventana, f"Jefe a los {need} pts", self.fuente, AMARILLO, ANCHO - 240, 10)

            now = ahora
            if now < self.juego["s_active_until"]:
                secs = (self.juego["s_active_until"] - now) // 1000
                dibujar_texto(self.ventana, f"S({secs}s)", self.fuente, VERDE, ANCHO - 120, 40)
            if now < self.juego["f_active_until"]:
                secs = (self.juego["f_active_until"] - now) // 1000
                dibujar_texto(self.ventana, f"F({secs}s)", self.fuente, AMARILLO, ANCHO - 60, 40)
            if now < self.juego["p_active_until"]:
                secs = (self.juego["p_active_until"] - now) // 1000
                dibujar_texto(self.ventana, f"P({secs}s)", self.fuente, MORADO, ANCHO - 120, 70)

            if self.estado == PAUSA:
                self.ventana.fill(NEGRO)
                dibujar_texto(self.ventana, "PAUSA", self.fuente_grande, AMARILLO, ANCHO//2, ALTO//2 - 40, centrado=True)
                dibujar_texto(self.ventana, "ENTER reanudar | R reiniciar | ESC menú", self.fuente, BLANCO, ANCHO//2, ALTO//2 + 20, centrado=True)

            if self.estado == BOSS_INTRO and self.juego["boss_active"] and self.juego["boss"]:
                draw_letterbox(self.ventana, alpha=200, size=90)
                t_left = max(0, self.juego["boss_intro_end"] - ahora)
                k = 1.0 - max(0.0, min(1.0, t_left / BOSS_INTRO_MS))
                bx, by, bw, bh = self.juego["boss"].rect
                pad = int(40 + 40 * (1.0 - k))
                focus = pygame.Rect(bx - pad, by - pad, bw + pad*2, bh + pad*2)
                focus = self.cam.apply_rect(focus)
                draw_focus_ring(self.ventana, focus, color=(255,255,255), width=3)
                dibujar_texto(self.ventana, "¡ALERTA JEFE!", self.fuente_grande, ROJO, ANCHO//2, 130, centrado=True)

        elif self.estado == GAME_OVER:
            self.ventana.fill(NEGRO)
            dibujar_texto(self.ventana, "GAME OVER", self.fuente_grande, ROJO, ANCHO//2, ALTO//2 - 80, centrado=True)
            dibujar_texto(self.ventana, f"Puntaje: {self.juego['puntaje']}", self.fuente, BLANCO, ANCHO//2, ALTO//2 - 10, centrado=True)
            dibujar_texto(self.ventana, f"Mejor puntaje: {self.hiscore}", self.fuente, AZUL, ANCHO//2, ALTO//2 + 20, centrado=True)
            dibujar_texto(self.ventana, "R para reiniciar", self.fuente, BLANCO, ANCHO//2, ALTO//2 + 70, centrado=True)
            dibujar_texto(self.ventana, "ENTER menú | ESC salir", self.fuente, BLANCO, ANCHO//2, ALTO//2 + 100, centrado=True)
