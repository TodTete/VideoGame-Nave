import pygame
from .gif import load_gif_frames
from .constants import ANCHO, ALTO

class MenuBG:
    def __init__(self, path):
        self.frames, self.durs = load_gif_frames(path, size=(ANCHO, ALTO))
        self.idx = 0
        self.tacc = 0

    def update(self, dt_ms):
        if not self.frames: return
        self.tacc += dt_ms
        if self.tacc >= self.durs[self.idx]:
            self.tacc = 0
            self.idx = (self.idx + 1) % len(self.frames)

    def draw(self, surface):
        if self.frames:
            surface.blit(self.frames[self.idx], (0, 0))
        else:
            surface.fill((0, 0, 0))
