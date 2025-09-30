import random, pygame
from .config import ANCHO, ALTO

def crear_enemigos(cantidad):
    return [pygame.Rect(random.randint(0, ANCHO - 40),
                        random.randint(-250, -40), 40, 40) for _ in range(cantidad)]

def respawnear_enemigo(enemigo):
    enemigo.x = random.randint(0, ANCHO - enemigo.width)
    enemigo.y = random.randint(-200, -40)
