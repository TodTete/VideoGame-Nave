import pygame
from game.app import GameApp

if __name__ == "__main__":
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception as e:
        print("[AVISO] Audio deshabilitado:", e)

    app = GameApp()
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
