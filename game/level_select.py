import pygame, os
from .constants import ANCHO, ALTO, LEVEL_COUNT, LEVEL_PLANET_DIR, LEVEL_MENU_BG, BLANCO, AMARILLO
from .utils import dibujar_texto

class LevelSelect:
    def __init__(self):
        self.selected = 1
        self.cols = 4
        self.rows = 2
        self.cell_w = 140
        self.cell_h = 140
        self.grid_top = 180
        self.grid_left = (ANCHO - self.cols * self.cell_w) // 2
        self.spacing_x = self.cell_w
        self.spacing_y = self.cell_h + 20

        # Cargar fondo del selector
        self.bg = None
        try:
            self.bg = pygame.image.load(LEVEL_MENU_BG).convert()
            self.bg = pygame.transform.scale(self.bg, (ANCHO, ALTO))
        except Exception as e:
            print(f"[AVISO] No se pudo cargar '{LEVEL_MENU_BG}': {e}")

        # Cargar planetas
        self.planets = {}
        for i in range(1, LEVEL_COUNT+1):
            path = os.path.join(LEVEL_PLANET_DIR, f"{i}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (100, 100))
            except Exception as e:
                print(f"[AVISO] No planeta '{path}': {e}")
                img = pygame.Surface((100,100), pygame.SRCALPHA)
                pygame.draw.circle(img, (120,140,255), (50,50), 48)
            self.planets[i] = img

        # Flechita (triángulo)
        self.arrow = self._make_arrow()

    def _make_arrow(self):
        surf = pygame.Surface((30, 22), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (255, 220, 90), [(0,11),(24,0),(24,22)])
        pygame.draw.polygon(surf, (110, 90, 20), [(0,11),(24,0),(24,22)], 2)
        return surf

    def _index_to_pos(self, idx):
        # idx 1..8 → col/row
        i = idx - 1
        r = i // self.cols
        c = i % self.cols
        x = self.grid_left + c * self.spacing_x + self.cell_w//2
        y = self.grid_top  + r * self.spacing_y + self.cell_h//2
        return x, y

    def handle_input(self, evento):
        if evento.key in (pygame.K_LEFT, pygame.K_a):
            self.selected = self.selected - 1 if self.selected > 1 else LEVEL_COUNT
        if evento.key in (pygame.K_RIGHT, pygame.K_d):
            self.selected = self.selected + 1 if self.selected < LEVEL_COUNT else 1
        if evento.key in (pygame.K_UP, pygame.K_w):
            self.selected -= self.cols
            if self.selected < 1:
                self.selected += self.cols * ((LEVEL_COUNT + self.cols - 1)//self.cols)
                if self.selected > LEVEL_COUNT:
                    self.selected = LEVEL_COUNT
        if evento.key in (pygame.K_DOWN, pygame.K_s):
            self.selected += self.cols
            if self.selected > LEVEL_COUNT:
                self.selected -= self.cols * ((LEVEL_COUNT + self.cols - 1)//self.cols)
                if self.selected < 1:
                    self.selected = 1
        if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
            return "SELECTED", self.selected
        return None, None

    def draw(self, surface, fuente_titulo, fuente):
        # Fondo
        if self.bg: surface.blit(self.bg, (0,0))
        else: surface.fill((0,0,0))

        dibujar_texto(surface, "SELECCIONA PLANETA (NIVEL)", fuente_titulo, AMARILLO, ANCHO//2, 90, centrado=True)

        # Dibuja grilla
        for i in range(1, LEVEL_COUNT+1):
            cx, cy = self._index_to_pos(i)
            rect = pygame.Rect(0,0, self.cell_w-20, self.cell_h-20)
            rect.center = (cx, cy)
            pygame.draw.rect(surface, (50,55,70), rect, border_radius=18)
            pygame.draw.rect(surface, (105,110,140), rect, 2, border_radius=18)

            # planeta
            img = self.planets[i]
            pr = img.get_rect(center=(cx, cy-6))
            surface.blit(img, pr)

            # etiqueta
            dibujar_texto(surface, f"Nivel {i}", fuente, BLANCO, cx, rect.bottom - 10, centrado=True)

        # Flecha sobre el seleccionado
        cx, cy = self._index_to_pos(self.selected)
        arr = self.arrow.get_rect(midright=(cx - (self.cell_w//2) + 8, cy))
        surface.blit(self.arrow, arr)
