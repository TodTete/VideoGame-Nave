import pygame, random, math
from .assets import dibujar_texto
from .config import ANCHO, ALTO, BLANCO, AMARILLO, AZUL, GRIS, NEGRO

# Estrellas para menú (parallax)
class StarField:
    def __init__(self, n=120):
        self.stars = []
        for _ in range(n):
            x = random.randint(0, ANCHO)
            y = random.randint(0, ALTO)
            z = random.choice([1,2,3])  # capa
            self.stars.append([x, y, z])

    def update(self, dt):
        for s in self.stars:
            speed = 10 * s[2]
            s[1] += speed * dt/1000.0
            if s[1] > ALTO:
                s[0] = random.randint(0, ANCHO)
                s[1] = 0

    def draw(self, surface):
        for s in self.stars:
            size = s[2]
            color = (200, 200, 255) if s[2] == 3 else (150,150,200) if s[2]==2 else (110,110,160)
            pygame.draw.circle(surface, color, (int(s[0]), int(s[1])), size)

def draw_letterbox(surface, alpha=200, size=90):
    s = pygame.Surface((ANCHO, size), pygame.SRCALPHA)
    s.fill((0,0,0,alpha))
    surface.blit(s, (0,0))
    surface.blit(s, (0,ALTO-size))

def draw_focus_ring(surface, rect, color=(255,255,255), width=3):
    pygame.draw.rect(surface, color, rect, width, border_radius=12)

def draw_menu(surface, fuente_titulo, fuente, hiscore, starfield, t):
    surface.fill((8, 10, 20))
    starfield.draw(surface)

    # Logo animado
    title = "GAME NAVE"
    scale = 1.0 + 0.03 * math.sin(t*0.003)
    text_surface = fuente_titulo.render(title, True, BLANCO)
    w, h = text_surface.get_size()
    text_surface = pygame.transform.rotozoom(text_surface, 0, scale)
    rect = text_surface.get_rect(center=(ANCHO//2, 140))
    surface.blit(text_surface, rect)

    # Tarjeta infos
    card = pygame.Rect(0, 0, 600, 260)
    card.center = (ANCHO//2, 330)
    pygame.draw.rect(surface, GRIS, card, border_radius=18)
    pygame.draw.rect(surface, (70,70,85), card.inflate(8,8), 4, border_radius=22)

    dibujar_texto(surface, "ENTER o SPACE para jugar", fuente, AMARILLO, ANCHO//2, card.top + 60, centrado=True)
    dibujar_texto(surface, "Controles: Flechas, SPACE disparo", fuente, BLANCO, ANCHO//2, card.top + 105, centrado=True)
    dibujar_texto(surface, "Bomba: recoge el ítem durante el jefe para disparo automático", fuente, BLANCO, ANCHO//2, card.top + 135, centrado=True)
    dibujar_texto(surface, "ENTER pausa | F11 pantalla completa | M silenciar", fuente, BLANCO, ANCHO//2, card.top + 165, centrado=True)
    dibujar_texto(surface, f"Mejor puntaje: {hiscore}", fuente, AZUL, ANCHO//2, card.top + 205, centrado=True)

def draw_hud(surface, fuente, juego, muted):
    dibujar_texto(surface, f"Puntaje: {juego['puntaje']}", fuente, (255,255,255), 10, 10)
    dibujar_texto(surface, f"Nivel: {juego['nivel']}", fuente, (255,255,255), 10, 40)
    dibujar_texto(surface, f"Vidas: {juego['vidas']}", fuente, (255,255,255), 10, 70)
    if muted:
        dibujar_texto(surface, "MUTED", fuente, (255,0,0), 700, 10)
    if not juego["boss_active"]:
        from .config import BOSS_POINTS_PER_LEVEL
        need = BOSS_POINTS_PER_LEVEL * juego["nivel"]
        dibujar_texto(surface, f"Jefe a los {need} pts", fuente, (255,215,0), 560, 10)

    now = pygame.time.get_ticks()
    if now < juego["s_active_until"]:
        secs = (juego["s_active_until"] - now) // 1000
        dibujar_texto(surface, f"S({secs}s)", fuente, (0,200,120), 680, 40)
    if now < juego["f_active_until"]:
        secs = (juego["f_active_until"] - now) // 1000
        dibujar_texto(surface, f"F({secs}s)", fuente, (255,215,0), 740, 40)
    if now < juego["p_active_until"]:
        secs = (juego["p_active_until"] - now) // 1000
        dibujar_texto(surface, f"P({secs}s)", fuente, (170,120,255), 680, 70)
