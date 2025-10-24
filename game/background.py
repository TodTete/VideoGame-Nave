import pygame
from .gif import load_gif_frames
from .constants import ANCHO, ALTO

def _load_any_frames(path, size):
    """Carga frames desde GIF si aplica; si es PNG/JPG devuelve un frame."""
    frames, durs = [], []
    # Intento 1: como GIF
    try:
        frames, durs = load_gif_frames(path, size=size)
        if frames:
            return frames, durs
    except Exception:
        pass
    # Intento 2: imagen estática
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, size)
        return [img], [120]
    except Exception as e:
        print(f"[AVISO] No se pudo cargar fondo '{path}': {e}")
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((0,0,0,255))
        return [surf], [120]

class AnimatedBackground:
    def __init__(self, path_main="assets/scenes/fondo.gif", path_boss="assets/scenes/fondo-gf.gif"):
        self.frames_a, self.durs_a = _load_any_frames(path_main, size=(ANCHO, ALTO))
        self.frames_b, self.durs_b = _load_any_frames(path_boss, size=(ANCHO, ALTO))
        self.use_b = False
        self.idx_a = self.idx_b = 0
        self.t_accum_a = self.t_accum_b = 0
        self.transition = False
        self.transition_time = 0.0
        self.transition_duration = 1200
        self.alpha = 0

    def set_main_path(self, path_main):
        """Cambia el fondo principal (del nivel actual)."""
        self.frames_a, self.durs_a = _load_any_frames(path_main, size=(ANCHO, ALTO))
        self.idx_a = 0
        self.t_accum_a = 0

    def switch_to_boss(self):
        if not self.transition and not self.use_b:
            self.transition = True; self.transition_time = 0.0; self.alpha = 0

    def switch_to_main(self):
        if not self.transition and self.use_b:
            self.transition = True; self.transition_time = 0.0; self.alpha = 0

    def update(self, dt):
        self.t_accum_a += dt
        if self.t_accum_a >= self.durs_a[self.idx_a]:
            self.t_accum_a = 0; self.idx_a = (self.idx_a + 1) % len(self.frames_a)

        self.t_accum_b += dt
        if self.t_accum_b >= self.durs_b[self.idx_b]:
            self.t_accum_b = 0; self.idx_b = (self.idx_b + 1) % len(self.frames_b)

        if self.transition:
            self.transition_time += dt
            self.alpha = int(255 * min(1.0, self.transition_time / self.transition_duration))
            if self.transition_time >= self.transition_duration:
                self.transition = False
                self.use_b = not self.use_b
                self.alpha = 255

    def draw(self, surface):
        if not self.transition:
            surface.blit((self.frames_b if self.use_b else self.frames_a)[self.idx_b if self.use_b else self.idx_a], (0,0))
        else:
            if not self.use_b:
                img_a = self.frames_a[self.idx_a]
                img_b = self.frames_b[self.idx_b].copy(); img_b.set_alpha(self.alpha)
                surface.blit(img_a,(0,0)); surface.blit(img_b,(0,0))
            else:
                img_b = self.frames_b[self.idx_b]
                img_a = self.frames_a[self.idx_a].copy(); img_a.set_alpha(self.alpha)
                surface.blit(img_b,(0,0)); surface.blit(img_a,(0,0))
