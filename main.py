import pygame, random, math, sys
from game.constants import *
from game.utils import cargar_sonido, reproducir, dibujar_texto, leer_hiscore, guardar_hiscore, load_font
from game.background import AnimatedBackground
from game.camera import Camera
from game.assets import init_after_display
from game.state import reset_juego, activar_pantalla_nivel
from game.entities.bullet import Bala
from game.entities.enemy import respawnear_enemigo, crear_enemigos
from game.entities.powerups import PowerUp, BombPickup, BombProjectile
from game.entities.boss import Boss
from game.gif import load_gif_frames  # para fondo animado del MENÚ
from game import assets as Assets      # << NUEVO (para set_player_skin y BALA2_IMG)

# =========================
# Inicialización
# =========================
pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("[AVISO] Audio deshabilitado:", e)

# ---- Música (helpers) ----
MUSIC_MAIN = "assets/music/game.mp3"
MUSIC_BOSS = "assets/music/boss.mp3"

def play_music(path, volume=0.5, loop=True, fade_ms=600):
    try:
        pygame.mixer.music.fadeout(fade_ms)
    except Exception:
        pass
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0, 0.0, fade_ms)
    except Exception as e:
        print("[AVISO] No se pudo iniciar música:", e)

# Ventana y fuentes
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(GAME_TITLE)

clock = pygame.time.Clock()
# Tipografías Retronoid
fuente = load_font(24)
fuente_grande = load_font(48)
fuente_titulo = load_font(56)

# Carga de imágenes/GIFs tras set_mode
init_after_display()

# Sonidos SFX
sonido_gameover = cargar_sonido("assets/music/game-over-381772.mp3", 0.6)
sonido_disparo  = cargar_sonido("assets/music/laser-shot-ingame-230500.mp3", 0.4)
sonido_explosion= cargar_sonido("assets/music/wood-crate-destory-2-97263.mp3", 0.55)
sonido_power    = cargar_sonido("assets/music/powerup.mp3", 0.6)

# Música de fondo inicial
play_music(MUSIC_MAIN, volume=0.5, loop=True, fade_ms=800)

# Fondo para juego (main/boss) y para MENÚ
bg = AnimatedBackground("assets/scenes/fondo.gif", "assets/scenes/fondo-gf.gif")
menu_frames, menu_durs = load_gif_frames("assets/scenes/space.gif", size=(ANCHO, ALTO))
menu_idx = 0
menu_tacc = 0

def update_menu_bg(dt_ms):
    global menu_idx, menu_tacc
    if not menu_frames: return
    menu_tacc += dt_ms
    if menu_tacc >= menu_durs[menu_idx]:
        menu_tacc = 0
        menu_idx = (menu_idx + 1) % len(menu_frames)

def draw_menu_bg(surface):
    if menu_frames:
        surface.blit(menu_frames[menu_idx], (0, 0))
    else:
        surface.fill((0, 0, 0))

# Cámara
cam = Camera()

# Helpers UI
def draw_letterbox(surface, alpha=200, size=90):
    s = pygame.Surface((ANCHO, size), pygame.SRCALPHA); s.fill((0,0,0,alpha))
    surface.blit(s, (0,0)); surface.blit(s, (0,ALTO-size))

def draw_focus_ring(surface, rect, color=(255,255,255), width=3):
    pygame.draw.rect(surface, color, rect, width, border_radius=12)

# Volúmenes (0.0 - 1.0)
vol_master = 1.0
vol_sfx = 1.0
vol_music = 0.5
muted = False

def apply_volumes():
    # Música
    pygame.mixer.music.set_volume((0.0 if muted else vol_music) * vol_master)
    # SFX
    if sonido_gameover:  sonido_gameover.set_volume(0.6 * (0.0 if muted else vol_sfx) * vol_master)
    if sonido_disparo:   sonido_disparo.set_volume(0.4 * (0.0 if muted else vol_sfx) * vol_master)
    if sonido_explosion: sonido_explosion.set_volume(0.55* (0.0 if muted else vol_sfx) * vol_master)
    if sonido_power:     sonido_power.set_volume(0.6 * (0.0 if muted else vol_sfx) * vol_master)

apply_volumes()

# Hiscore & Estado
hiscore = leer_hiscore()
juego = reset_juego()

# --- Personajes / selección ---
selected_ship = "BRAYAN"  # default
# Previews rápidos (cargan 1 vez)
def _load_ship_preview(path, size=(100,100)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except Exception:
        s = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.polygon(s, (200,200,255),
                            [(size[0]//2,6),(10,size[1]-8),(size[0]-10,size[1]-8)])
        return s

ship_previews = {
    "BRAYAN":   _load_ship_preview("assets/extra/nave.gif", (100,100)),
    "FERNANDA": _load_ship_preview("assets/extra/nave-f.jpg", (100,100)),
    "MARLIN":   _load_ship_preview("assets/extra/nave-m.png", (100,100)),
    "TETE":     _load_ship_preview("assets/extra/nave-t.png", (100,100)),
}
ship_index = 0  # índice en SHIP_ORDER

def apply_selected_ship():
    Assets.set_player_skin(selected_ship)

apply_selected_ship()  # al inicio

# Menús
estado = MENU_MAIN
menu_main_items = ["INICIO", "PERSONAJE", "DIFICULTAD", "OPCIONES"]  # << cambiado
menu_main_index = 0

# Dificultad
difficulty_name = "MEDIA"  # por defecto
def get_diff_mul():
    d = DIFFICULTY_PRESETS.get(difficulty_name, DIFFICULTY_PRESETS["MEDIA"])
    return d["enemy_speed"], d["boss_hp"]

# Menú Opciones
options_items = ["Volumen Maestro", "Efectos (SFX)", "Música"]
options_index = 0
# sliders visuales
def draw_slider(surface, x, y, w, value, selected):
    bg_rect = pygame.Rect(x, y, w, 10)
    pygame.draw.rect(surface, (80,80,95), bg_rect, border_radius=6)
    fill_w = int(w * max(0.0, min(1.0, value)))
    fill_rect = pygame.Rect(x, y, fill_w, 10)
    pygame.draw.rect(surface, (255,215,0) if selected else (120,160,255), fill_rect, border_radius=6)
    pygame.draw.rect(surface, (180,180,200), bg_rect, 2, border_radius=6)

fullscreen = False
bounds_rect = pygame.Rect(0,0,ANCHO,ALTO)

def shoot_pattern(juego, ahora):
    """Genera las balas según la nave elegida."""
    mx, my = juego["player"].get_muzzle_world()
    vy = juego["vel_bala"]

    if selected_ship == "FERNANDA":
        # una bala ancha
        juego["balas"].append(Bala(mx, my, vy=vy, image=Assets.BALA2_IMG))
    elif selected_ship == "MARLIN":
        # doble bala con separación lateral
        juego["balas"].append(Bala(mx - 12, my, vy=vy))
        juego["balas"].append(Bala(mx + 12, my, vy=vy))
    elif selected_ship == "TETE":
        # triple bala: centro + laterales
        juego["balas"].append(Bala(mx, my, vy=vy))
        juego["balas"].append(Bala(mx - 14, my, vy=vy))
        juego["balas"].append(Bala(mx + 14, my, vy=vy))
    else:
        # BRAYAN default
        juego["balas"].append(Bala(mx, my, vy=vy))

running = True
try:
    while running:
        dt = clock.tick(FPS)
        ahora = pygame.time.get_ticks()

        # Cámara suave (sólo cuando el player existe)
        if juego.get("player"):
            tx, ty = cam.target_from_player(juego["player"].rect, ANCHO, ALTO)
            cam.update(tx, ty)

        # Fondos
        if estado in (MENU_MAIN, MENU_OPTIONS, MENU_DIFFICULTY):
            update_menu_bg(dt)  # animación del fondo del MENÚ
        elif estado not in (LEVEL_INTRO, PAUSA):
            bg.update(dt)       # animación del fondo de juego

        # -------------------------
        # Eventos
        # -------------------------
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False

            if evento.type == pygame.KEYDOWN:
                # Globales: F11, m, ESC (igual)...
                if evento.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    flags = pygame.FULLSCREEN if fullscreen else 0
                    ventana = pygame.display.set_mode((ANCHO, ALTO), flags)

                if evento.key == pygame.K_m:
                    muted = not muted
                    apply_volumes()

                if evento.key == pygame.K_ESCAPE:
                    if estado in (JUGANDO, PAUSA):
                        estado = PAUSA if estado == JUGANDO else JUGANDO
                    elif estado in (MENU_OPTIONS, MENU_DIFFICULTY, MENU_CHARACTER, LEVEL_INTRO, BOSS_INTRO, GAME_OVER):
                        estado = MENU_MAIN
                    elif estado == MENU_MAIN:
                        running = False

                # ---- MENÚ PRINCIPAL ----
                if estado == MENU_MAIN:
                    if evento.key in (pygame.K_UP, pygame.K_w):
                        menu_main_index = (menu_main_index - 1) % len(menu_main_items)
                    if evento.key in (pygame.K_DOWN, pygame.K_s):
                        menu_main_index = (menu_main_index + 1) % len(menu_main_items)
                    if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        sel = menu_main_items[menu_main_index]
                        if sel == "INICIO":
                            juego = reset_juego()
                            if difficulty_name == "EXTREMA" and len(juego["enemigos"]) < 12:
                                juego["enemigos"] += crear_enemigos(2)
                            estado = LEVEL_INTRO
                            activar_pantalla_nivel(juego, ahora)
                            juego["intro_text"] = "NIVEL 1"
                            play_music(MUSIC_MAIN, volume=vol_music*vol_master if not muted else 0.0, loop=True, fade_ms=500)
                        elif sel == "PERSONAJE":  # << NUEVO
                            estado = MENU_CHARACTER
                        elif sel == "DIFICULTAD":
                            estado = MENU_DIFFICULTY
                        elif sel == "OPCIONES":
                            estado = MENU_OPTIONS

                # ---- MENÚ PERSONAJE ----
                elif estado == MENU_CHARACTER:  # << NUEVO
                    if evento.key in (pygame.K_LEFT, pygame.K_a):
                        ship_index = (ship_index - 1) % len(SHIP_ORDER)
                    if evento.key in (pygame.K_RIGHT, pygame.K_d):
                        ship_index = (ship_index + 1) % len(SHIP_ORDER)
                    if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        selected_ship = SHIP_ORDER[ship_index]
                        apply_selected_ship()
                        estado = MENU_MAIN

                # ---- MENÚ OPCIONES ----
                elif estado == MENU_OPTIONS:
                    if evento.key in (pygame.K_UP, pygame.K_w):
                        options_index = (options_index - 1) % len(options_items)
                    if evento.key in (pygame.K_DOWN, pygame.K_s):
                        options_index = (options_index + 1) % len(options_items)
                    if evento.key in (pygame.K_LEFT, pygame.K_a):
                        if options_index == 0: vol_master = max(0.0, vol_master - 0.05)
                        elif options_index == 1: vol_sfx = max(0.0, vol_sfx - 0.05)
                        elif options_index == 2: vol_music = max(0.0, vol_music - 0.05)
                        apply_volumes()
                    if evento.key in (pygame.K_RIGHT, pygame.K_d):
                        if options_index == 0: vol_master = min(1.0, vol_master + 0.05)
                        elif options_index == 1: vol_sfx = min(1.0, vol_sfx + 0.05)
                        elif options_index == 2: vol_music = min(1.0, vol_music + 0.05)
                        apply_volumes()
                    if evento.key == pygame.K_RETURN:
                        estado = MENU_MAIN

                # ---- MENÚ DIFICULTAD ----
                elif estado == MENU_DIFFICULTY:
                    if evento.key in (pygame.K_UP, pygame.K_w):
                        i = DIFFICULTY_ORDER.index(difficulty_name)
                        difficulty_name = DIFFICULTY_ORDER[(i - 1) % len(DIFFICULTY_ORDER)]
                    if evento.key in (pygame.K_DOWN, pygame.K_s):
                        i = DIFFICULTY_ORDER.index(difficulty_name)
                        difficulty_name = DIFFICULTY_ORDER[(i + 1) % len(DIFFICULTY_ORDER)]
                    if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                        estado = MENU_MAIN

                # ---- PAUSA ----
                elif estado == PAUSA:
                    if evento.key == pygame.K_RETURN:
                        estado = JUGANDO
                    if evento.key == pygame.K_r:
                        juego = reset_juego()
                        if difficulty_name == "EXTREMA" and len(juego["enemigos"]) < 12:
                            juego["enemigos"] += crear_enemigos(2)
                        estado = LEVEL_INTRO
                        activar_pantalla_nivel(juego, ahora)
                        juego["intro_text"] = "NIVEL 1"
                        play_music(MUSIC_MAIN, volume=vol_music*vol_master if not muted else 0.0, loop=True, fade_ms=500)

                # ---- GAME OVER ----
                elif estado == GAME_OVER:
                    if evento.key == pygame.K_r:
                        juego = reset_juego()
                        if difficulty_name == "EXTREMA" and len(juego["enemigos"]) < 12:
                            juego["enemigos"] += crear_enemigos(2)
                        estado = LEVEL_INTRO
                        activar_pantalla_nivel(juego, ahora)
                        juego["intro_text"] = "NIVEL 1"
                        play_music(MUSIC_MAIN, volume=vol_music*vol_master if not muted else 0.0, loop=True, fade_ms=500)
                    if evento.key == pygame.K_RETURN:
                        estado = MENU_MAIN
                        play_music(MUSIC_MAIN, volume=vol_music*vol_master if not muted else 0.0, loop=True, fade_ms=500)

                # ---- JUGANDO ---- 
                elif estado == JUGANDO:
                    if evento.key == pygame.K_RETURN:
                        estado = PAUSA
                    if evento.key == pygame.K_SPACE:
                        if ahora - juego["ultimo_disparo"] >= juego["cadencia_ms"]:
                            shoot_pattern(juego, ahora)  # << usa patrón por nave
                            juego["ultimo_disparo"] = ahora
                            reproducir(sonido_disparo)

        # -------------------------
        # Lógica principal
        # -------------------------
        if estado == LEVEL_INTRO:
            if ahora >= juego["intro_end_time"]:
                estado = JUGANDO

        elif estado == BOSS_INTRO:
            if ahora >= juego["boss_intro_end"]:
                estado = JUGANDO

        elif estado == JUGANDO:
            keys = pygame.key.get_pressed()

            # Buffs activos
            s_activo = ahora < juego["s_active_until"]
            f_activo = ahora < juego["f_active_until"]
            p_activo = ahora < juego["p_active_until"]

            juego["player"].vel = juego["player"].vel_base + (3 if s_activo else 0)
            juego["cadencia_ms"] = 100 if p_activo else 200
            juego["player"].update(dt, keys)

            # Dificultad
            enemy_mul, boss_mul = get_diff_mul()

            # ¿Aparece jefe?
            needed_points = BOSS_POINTS_PER_LEVEL * juego["nivel"]
            if (juego["puntaje"] >= needed_points
                and juego["nivel"] not in juego["boss_threshold_cleared"]
                and not juego["boss_active"]):
                juego["boss"] = Boss(juego["nivel"], difficulty_hp_mul=boss_mul)
                # EXTREMA: jefe más agresivo
                if difficulty_name == "EXTREMA":
                    juego["boss"].fire_cd_ms = max(220, int(juego["boss"].fire_cd_ms * 0.60))
                    juego["boss"].pattern_duration = int(juego["boss"].pattern_duration * 0.80)
                    juego["boss"].move_speed *= 1.25
                juego["boss_active"] = True
                bg.switch_to_boss()
                play_music(MUSIC_BOSS, volume=vol_music*vol_master if not muted else 0.0, loop=True, fade_ms=700)
                estado = BOSS_INTRO
                juego["boss_intro_end"] = ahora + BOSS_INTRO_MS
                juego["next_bomb_spawn_time"] = ahora + BOSS_INTRO_MS + 200

            # --- SIN JEFE ---
            if not juego["boss_active"]:
                # balas jugador
                for bala in juego["balas"][:]:
                    if not bala.update():
                        juego["balas"].remove(bala)

                # enemigos
                vel_enemigo = (juego["vel_enemigo_base"] + (juego["nivel"] - 1) * 0.9) * enemy_mul
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
                            impactado = enemigo; break
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

                # daño al jugador por choque
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

                # powerups
                for pu in juego["powerups"][:]:
                    if not pu.update():
                        juego["powerups"].remove(pu); continue
                    if pu.rect.colliderect(juego["player"].rect):
                        if pu.tipo == 'S': juego["s_active_until"] = ahora + 8000
                        elif pu.tipo == 'F': juego["f_active_until"] = ahora + 8000
                        elif pu.tipo == 'P': juego["p_active_until"] = ahora + 8000
                        try: juego["powerups"].remove(pu)
                        except ValueError: pass
                        reproducir(sonido_power)

            # --- CON JEFE ---
            else:
                boss = juego["boss"]
                boss_bullets = juego["boss_bullets"]

                for bala in juego["balas"][:]:
                    if not bala.update():
                        juego["balas"].remove(bala)

                boss.update(dt, ahora, juego["player"].rect, boss_bullets)

                # daño al jefe
                for bala in juego["balas"][:]:
                    if boss.rect.colliderect(bala.rect):
                        try: juego["balas"].remove(bala)
                        except ValueError: pass
                        boss.hp -= 10
                        reproducir(sonido_explosion)

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
                        juego["bombs"].append(BombProjectile(px, py, boss.rect, reproducir, sonido_explosion))
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
                    juego["boss"] = None; juego["boss_bullets"].clear()
                    juego["bombs"].clear(); juego["bomb_pickup"] = None
                    juego["puntaje"] += 100
                    juego["nivel"] += 1
                    juego["vel_enemigo_base"] += 0.8
                    if len(juego["enemigos"]) < 12:
                        juego["enemigos"] += crear_enemigos(1)
                    bg.switch_to_main()
                    play_music(MUSIC_MAIN, volume=vol_music*vol_master if not muted else 0.0, loop=True, fade_ms=700)
                    estado = LEVEL_INTRO
                    activar_pantalla_nivel(juego, ahora)

            # ¿Sin vidas?
            if juego["vidas"] <= 0 and estado in (JUGANDO, BOSS_INTRO):
                estado = GAME_OVER
                if sonido_gameover:
                    reproducir(sonido_gameover)
                play_music(MUSIC_MAIN, volume=vol_music*vol_master if not muted else 0.0, loop=True, fade_ms=600)
                if juego["puntaje"] > hiscore:
                    hiscore = juego["puntaje"]; guardar_hiscore(hiscore)

        # -------------------------
        # Dibujo
        # -------------------------
        # Fondo según estado:
        if estado in (MENU_MAIN, MENU_OPTIONS, MENU_DIFFICULTY, MENU_CHARACTER):
            draw_menu_bg(ventana)  # GIF space.gif
        else:
            if estado in (JUGANDO, BOSS_INTRO, GAME_OVER, LEVEL_INTRO, PAUSA):
                bg.draw(ventana)

        if estado == MENU_MAIN:
            card = pygame.Rect(0, 0, 560, 420); card.center = (ANCHO//2, ALTO//2 - 20)
            pygame.draw.rect(ventana, GRIS, card, border_radius=18)
            pygame.draw.rect(ventana, (70,70,85), card.inflate(8,8), 4, border_radius=22)
            dibujar_texto(ventana, GAME_TITLE.upper(), fuente_titulo, ORO, ANCHO//2, card.top + 65, centrado=True)
            for i, label in enumerate(menu_main_items):
                color = AMARILLO if i == menu_main_index else BLANCO
                dibujar_texto(ventana, label, fuente_grande, color, ANCHO//2, card.top + 140 + i*55, centrado=True)
            # Muestra selección actual de nave en el menú principal
            dibujar_texto(ventana, f"Personaje: {SHIP_DISPLAY[selected_ship]}", fuente, AMARILLO, ANCHO//2, card.bottom - 60, centrado=True)
            dibujar_texto(ventana, "Créditos: created by TodTete", fuente, BLANCO, ANCHO//2, card.bottom - 20, centrado=True)

        elif estado == MENU_CHARACTER:
            # Pantalla de selección de personaje
            dibujar_texto(ventana, "SELECCIONA PERSONAJE", fuente_titulo, MORADO, ANCHO//2, 80, centrado=True)
            # carrusel simple 4 opciones
            cx = ANCHO//2; cy = ALTO//2 + 10
            spacing = 180
            for idx, key in enumerate(SHIP_ORDER):
                px = cx + (idx - ship_index) * spacing
                rect = pygame.Rect(0, 0, 150, 180)  # un poco más grande
                rect.center = (px, cy)
                pygame.draw.rect(ventana, (55, 55, 70), rect, border_radius=38)
                pygame.draw.rect(ventana, (100, 100, 135), rect, 2, border_radius=38)

                prev = ship_previews[key]
                pr = prev.get_rect(center=(rect.centerx, rect.top + 70))
                ventana.blit(prev, pr)

                label = SHIP_DISPLAY[key]
                # Más espacio visual bajo la imagen
                dibujar_texto(ventana, label, fuente, 
                  AMARILLO if idx == ship_index else BLANCO, 
                  rect.centerx, rect.bottom - 18, centrado=True)
            dibujar_texto(ventana, "←/→ para cambiar  |  ENTER para seleccionar  |  ESC volver", fuente, AZUL, ANCHO//2, ALTO - 60, centrado=True)

        elif estado == LEVEL_INTRO:
            ventana.fill(NEGRO)
            dibujar_texto(ventana, juego["intro_text"], fuente_grande, BLANCO, ANCHO//2, ALTO//2 - 10, centrado=True)
            dibujar_texto(ventana, f"¡Vidas reiniciadas!  Dificultad: {difficulty_name}", fuente, AMARILLO, ANCHO//2, ALTO//2 + 40, centrado=True)

        elif estado in (JUGANDO, PAUSA, BOSS_INTRO):
            # Nave
            visible = True
            if estado != PAUSA and pygame.time.get_ticks() < juego["invulnerable_hasta"]:
                visible = ((ahora // 100) % 2 == 0)
            juego["player"].draw(ventana, cam.apply_point, visible=visible)

            # Balas
            for bala in juego["balas"]:
                bala.draw(ventana, cam.apply_rect)

            if not juego["boss_active"]:
                for enemigo in juego["enemigos"]:
                    enemigo.draw(ventana, cam.apply_rect)
                for pu in juego["powerups"]:
                    pu.draw(ventana, fuente, cam.apply_rect, cam.apply_point, dibujar_texto, NEGRO)
            else:
                juego["boss"].draw(ventana, cam.apply_rect, ahora)
                for b in juego["boss_bullets"]:
                    color = (255,140,0)
                    t = b.get("type","normal")
                    if t == "wave": color = (255,200,0)
                    elif t == "aim": color = (255,80,80)
                    elif t == "spread": color = (255,160,60)
                    elif t == "burst": color = (255,100,0)
                    pygame.draw.rect(ventana, color, cam.apply_rect(b["rect"]))
                if juego["bomb_pickup"]:
                    juego["bomb_pickup"].draw(ventana, cam.apply_rect)

            for bomb in juego["bombs"]:
                bomb.draw(ventana, cam.apply_rect, cam.apply_point)

            # HUD
            dibujar_texto(ventana, f"Puntaje: {juego['puntaje']}", fuente, BLANCO, 10, 10)
            dibujar_texto(ventana, f"Nivel: {juego['nivel']}", fuente, BLANCO, 10, 40)
            dibujar_texto(ventana, f"Vidas: {juego['vidas']}", fuente, BLANCO, 10, 70)
            if muted: dibujar_texto(ventana, "MUTED", fuente, ROJO, ANCHO - 90, 10)
            if not juego["boss_active"]:
                need = BOSS_POINTS_PER_LEVEL * juego["nivel"]
                dibujar_texto(ventana, f"Jefe a los {need} pts", fuente, AMARILLO, ANCHO - 240, 10)

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

            if estado == PAUSA:
                ventana.fill(NEGRO)
                dibujar_texto(ventana, "PAUSA", fuente_grande, AMARILLO, ANCHO//2, ALTO//2 - 40, centrado=True)
                dibujar_texto(ventana, "ENTER reanudar | R reiniciar | ESC menú", fuente, BLANCO, ANCHO//2, ALTO//2 + 20, centrado=True)

            if estado == BOSS_INTRO and juego["boss_active"] and juego["boss"]:
                draw_letterbox(ventana, alpha=200, size=90)
                t_left = max(0, juego["boss_intro_end"] - ahora)
                k = 1.0 - max(0.0, min(1.0, t_left / BOSS_INTRO_MS))
                bx, by, bw, bh = juego["boss"].rect
                pad = int(40 + 40 * (1.0 - k))
                focus = pygame.Rect(bx - pad, by - pad, bw + pad*2, bh + pad*2)
                focus = cam.apply_rect(focus)
                draw_focus_ring(ventana, focus, color=(255,255,255), width=3)
                dibujar_texto(ventana, "¡ALERTA JEFE!", fuente_grande, ROJO, ANCHO//2, 130, centrado=True)

        elif estado == GAME_OVER:
            ventana.fill(NEGRO)
            dibujar_texto(ventana, "GAME OVER", fuente_grande, ROJO, ANCHO//2, ALTO//2 - 80, centrado=True)
            dibujar_texto(ventana, f"Puntaje: {juego['puntaje']}", fuente, BLANCO, ANCHO//2, ALTO//2 - 10, centrado=True)
            dibujar_texto(ventana, f"Mejor puntaje: {hiscore}", fuente, AZUL, ANCHO//2, ALTO//2 + 20, centrado=True)
            dibujar_texto(ventana, "R para reiniciar", fuente, BLANCO, ANCHO//2, ALTO//2 + 70, centrado=True)
            dibujar_texto(ventana, "ENTER menú | ESC salir", fuente, BLANCO, ANCHO//2, ALTO//2 + 100, centrado=True)

        pygame.display.flip()

except KeyboardInterrupt:
    pass
finally:
    pygame.quit()
