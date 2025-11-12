import pygame
from . import assets as Assets
from .constants import ANCHO, ALTO, SHIP_ORDER, SHIP_DISPLAY, MENU_CHARACTER, BLANCO, AMARILLO, AZUL, MORADO

# --- util para GIFs (con fallback si no hay Pillow) ---
def _load_frames(path, size=(100, 100)):
    """
    Carga un GIF o imagen estática con compatibilidad total.
    """
    try:
        from PIL import Image, ImageSequence
        img = Image.open(path)
        frames, durations = [], []

        for frame in ImageSequence.Iterator(img):
            f = frame.convert("RGBA")
            surf = pygame.image.fromstring(f.tobytes(), f.size, "RGBA").convert_alpha()
            surf = pygame.transform.smoothscale(surf, size)
            frames.append(surf)
            durations.append(int(frame.info.get("duration", 100)))

        if not frames:
            raise ValueError("GIF vacío")

        durations = [d if d > 0 else 100 for d in durations]
        return frames, durations

    except Exception as e:
        # Carga imagen estática si no es GIF
        try:
            static = pygame.image.load(path).convert_alpha()
            static = pygame.transform.smoothscale(static, size)
        except Exception:
            static = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.polygon(static, (200, 200, 255),
                                [(size[0]//2, 6), (10, size[1]-8), (size[0]-10, size[1]-8)])
        return [static], [150]


class CharacterSelect:
    def __init__(self):
        self.selected_ship = "BRAYAN"
        self.ship_index = 0
        self.spacing = 180

        # Cargar frames (GIFs animados incluidos)
        self.previews = {
            "BRAYAN":   _load_frames("assets/extra/nave.gif",   (100, 100)),
            "FERNANDA": _load_frames("assets/extra/nave-f.jpg", (100, 100)),
            "MARLIN":   _load_frames("assets/extra/nave-m.gif", (100, 100)),
            "TETE":     _load_frames("assets/extra/nave-t.png", (100, 100)),
        }

        # Estado de animación por nave
        # { key: {"i": índice_frame, "t": acumulador_ms} }
        self._anim_state = {k: {"i": 0, "t": 0} for k in self.previews.keys()}

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

    def update(self, dt_ms: int):
        """
        Avanza la animación de todos los GIFs.
        Llama a este método en tu bucle principal con dt en milisegundos.
        Ej: character_select.update(clock.get_time())
        """
        for key, (frames, durations) in self.previews.items():
            if len(frames) <= 1:
                continue  # estático, nada que animar
            st = self._anim_state[key]
            st["t"] += dt_ms
            # avanzar cuadro respetando duración por frame
            while st["t"] >= durations[st["i"]]:
                st["t"] -= durations[st["i"]]
                st["i"] = (st["i"] + 1) % len(frames)

    def _current_frame(self, key):
        frames, _ = self.previews[key]
        idx = self._anim_state[key]["i"] if len(frames) > 1 else 0
        return frames[idx]

    def draw(self, surface, fuente_titulo, fuente):
        from .utils import dibujar_texto

        # Título
        dibujar_texto(surface, "SELECCIONA PERSONAJE", fuente_titulo, MORADO, ANCHO//2, 80, centrado=True)

        # Carrusel (SIN cuadros grises)
        cx = ANCHO//2; cy = ALTO//2 + 10
        spacing = self.spacing

        for idx, key in enumerate(SHIP_ORDER):
            px = cx + (idx - self.ship_index) * spacing

            # Dibujar solo el sprite animado centrado (sin rectángulos de fondo/borde)
            frame = self._current_frame(key)
            fr = frame.get_rect(center=(px, cy - 10))
            surface.blit(frame, fr)

            # Etiqueta
            label = SHIP_DISPLAY[key]
            dibujar_texto(surface, label, fuente,
                          AMARILLO if idx == self.ship_index else BLANCO,
                          px, cy + 90, centrado=True)

            # Opcional: un pequeño indicador bajo la nave seleccionada (no un cuadro)
            if idx == self.ship_index:
                pygame.draw.circle(surface, AMARILLO, (px, cy + 70), 4)

        # Instrucciones
        dibujar_texto(surface, "←/→ para cambiar  |  ENTER para seleccionar  |  ESC volver",
                      fuente, AZUL, ANCHO//2, ALTO - 60, centrado=True)
