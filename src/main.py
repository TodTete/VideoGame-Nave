import pygame, sys
from .config import ANCHO, ALTO, FPS
from .game import Game

def main():
    pygame.init()
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Game Nave")
    game = Game(ventana)

    running = True
    try:
        while running:
            dt = game.clock.tick(FPS)
            running = game.handle_events()
            game.update(dt)
            game.draw()
            pygame.display.flip()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
