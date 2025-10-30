import pygame
from .gif import load_gif_frames
from .constants import ANCHO, ALTO

class MenuBG:
    def __init__(self, gif_path):
        self.frames, self.durations = load_gif_frames(gif_path, size=(ANCHO, ALTO))
        self.current_frame = 0
        self.time_accumulator = 0
        self.zoom_factor = 1.0  # Inicializamos el factor de zoom
        self.offset_x = 0  # Para mover el fondo horizontalmente
        self.offset_y = 0  # Para mover el fondo verticalmente
        self.zoom_speed = 0.001  # Velocidad de incremento del zoom
        self.offset_speed = 0.05  # Velocidad de desplazamiento del fondo

    def update(self, dt_ms):
        """Actualiza la animación del fondo y el zoom"""
        self.time_accumulator += dt_ms

        # Avanzamos la animación del gif
        if self.time_accumulator >= self.durations[self.current_frame]:
            self.time_accumulator = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Aplicamos zoom progresivo (se puede ajustar la velocidad)
        self.zoom_factor += self.zoom_speed  # Aumenta el zoom poco a poco
        if self.zoom_factor > 1.5:  # Limitamos el zoom máximo
            self.zoom_factor = 1.5

        # Movemos el fondo (desplazamiento)
        self.offset_x += self.offset_speed
        if self.offset_x > ANCHO * 0.1 or self.offset_x < -ANCHO * 0.1:  # Si el fondo se desplaza mucho, revertimos
            self.offset_speed *= -1

    def draw(self, surface):
        """Dibuja el fondo escalado sobre la superficie con desplazamiento"""
        frame = self.frames[self.current_frame]
        
        # Escalamos el fotograma actual del gif
        scaled_frame = pygame.transform.smoothscale(frame, 
                                                     (int(ANCHO * self.zoom_factor), int(ALTO * self.zoom_factor)))
        
        # Calculamos la posición para centrar la imagen escalada, desplazándola también
        offset_x = (scaled_frame.get_width() - ANCHO) // 2 + int(self.offset_x)
        offset_y = (scaled_frame.get_height() - ALTO) // 2 + int(self.offset_y)

        # Dibujamos el fondo escalado y desplazado
        surface.blit(scaled_frame, (-offset_x, -offset_y))