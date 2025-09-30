import pygame
try:
    from PIL import Image, ImageSequence
    PIL_OK = True
except Exception as e:
    print("[AVISO] Pillow no disponible, fondos GIF estáticos:", e)
    PIL_OK = False

from .config import ANCHO, ALTO

def load_gif_frames(path, size=(ANCHO, ALTO)):
    frames, durations = [], []
    if not PIL_OK:
        try:
            img = pygame.image.load(path).convert()
            img = pygame.transform.smoothscale(img, size)
            return [img], [120]
        except Exception as e:
            print(f"[AVISO] No se pudo cargar fondo '{path}': {e}")
            surf = pygame.Surface(size); surf.fill((5,5,15))
            return [surf], [120]

    try:
        im = Image.open(path)
        base_frames, base_durations = [], []
        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            dur = frame.info.get("duration", 100)
            base_durations.append(max(20, int(dur)))
            if size:
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
        surf = pygame.Surface(size); surf.fill((5,5,15))
        return [surf], [120]

class AnimatedBackground:
    def __init__(self, path_main, path_boss):
        self.frames_a, self.durs_a = load_gif_frames(path_main)
        self.frames_b, self.durs_b = load_gif_frames(path_boss)
        self.use_b = False
        self.idx_a = self.idx_b = 0
        self.t_accum_a = self.t_accum_b = 0
        self.transition = False
        self.transition_time = 0.0
        self.transition_duration = 1200
        self.alpha = 0

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
            surface.blit(self.frames_b[self.idx_b] if self.use_b else self.frames_a[self.idx_a], (0,0))
        else:
            if not self.use_b:
                img_a = self.frames_a[self.idx_a]
                img_b = self.frames_b[self.idx_b].copy()
                img_b.set_alpha(self.alpha)
                surface.blit(img_a, (0,0)); surface.blit(img_b, (0,0))
            else:
                img_b = self.frames_b[self.idx_b]
                img_a = self.frames_a[self.idx_a].copy()
                img_a.set_alpha(self.alpha)
                surface.blit(img_b, (0,0)); surface.blit(img_a, (0,0))
