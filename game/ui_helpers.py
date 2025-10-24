import pygame
from .constants import ANCHO, ALTO

def draw_letterbox(surface, alpha=200, size=90):
    s = pygame.Surface((ANCHO, size), pygame.SRCALPHA); s.fill((0,0,0,alpha))
    surface.blit(s, (0,0)); surface.blit(s, (0,ALTO-size))

def draw_focus_ring(surface, rect, color=(255,255,255), width=3):
    pygame.draw.rect(surface, color, rect, width, border_radius=12)

def draw_slider(surface, x, y, w, value, selected):
    bg_rect = pygame.Rect(x, y, w, 10)
    pygame.draw.rect(surface, (80,80,95), bg_rect, border_radius=6)
    fill_w = int(w * max(0.0, min(1.0, value)))
    fill_rect = pygame.Rect(x, y, fill_w, 10)
    pygame.draw.rect(surface, (255,215,0) if selected else (120,160,255), fill_rect, border_radius=6)
    pygame.draw.rect(surface, (180,180,200), bg_rect, 2, border_radius=6)
