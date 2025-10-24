import pygame
from . import assets as Assets
from .constants import ANCHO, ALTO, SHIP_ORDER, SHIP_DISPLAY, MENU_CHARACTER, BLANCO, AMARILLO, AZUL, MORADO

class CharacterSelect:
    def __init__(self):
        self.selected_ship = "BRAYAN"
        self.ship_index = 0
        self.spacing = 180

        def _load_ship_preview(path, size=(100,100)):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.smoothscale(img, size)
            except Exception:
                s = pygame.Surface(size, pygame.SRCALPHA)
                pygame.draw.polygon(s, (200,200,255),
                                    [(size[0]//2,6),(10,size[1]-8),(size[0]-10,size[1]-8)])
                return s

        self.previews = {
            "BRAYAN":   _load_ship_preview("assets/extra/nave.gif", (100,100)),
            "FERNANDA": _load_ship_preview("assets/extra/nave-f.jpg", (100,100)),
            "MARLIN":   _load_ship_preview("assets/extra/nave-m.png", (100,100)),
            "TETE":     _load_ship_preview("assets/extra/nave-t.png", (100,100)),
        }

        # aplicar por defecto
        self.apply_selected_skin()

    def apply_selected_skin(self):
        Assets.set_player_skin(self.selected_ship)

    def handle_input(self, evento):
        if evento.key in (pygame.K_LEFT, pygame.K_a):
            self.ship_index = (self.ship_index - 1) % len(SHIP_ORDER)
        if evento.key in (pygame.K_RIGHT, pygame.K_d):
            self.ship_index = (self.ship_index + 1) % len(SHIP_ORDER)
        if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.selected_ship = SHIP_ORDER[self.ship_index]
            return "APPLY"
        return None

    def draw(self, surface, fuente_titulo, fuente):
        from .constants import BLANCO
        # Título
        import pygame
        from .utils import dibujar_texto
        dibujar_texto(surface, "SELECCIONA PERSONAJE", fuente_titulo, MORADO, ANCHO//2, 80, centrado=True)
        # carrusel
        cx = ANCHO//2; cy = ALTO//2 + 10
        spacing = self.spacing
        for idx, key in enumerate(SHIP_ORDER):
            px = cx + (idx - self.ship_index) * spacing
            rect = pygame.Rect(0, 0, 150, 180)
            rect.center = (px, cy)
            pygame.draw.rect(surface, (55, 55, 70), rect, border_radius=38)
            pygame.draw.rect(surface, (100, 100, 135), rect, 2, border_radius=38)

            prev = self.previews[key]
            pr = prev.get_rect(center=(rect.centerx, rect.top + 70))
            surface.blit(prev, pr)

            label = SHIP_DISPLAY[key]
            dibujar_texto(surface, label, fuente,
                          AMARILLO if idx == self.ship_index else BLANCO,
                          rect.centerx, rect.bottom - 18, centrado=True)

        dibujar_texto(surface, "←/→ para cambiar  |  ENTER para seleccionar  |  ESC volver",
                      fuente, AZUL, ANCHO//2, ALTO - 60, centrado=True)
