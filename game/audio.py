import pygame

MUSIC_MAIN = "assets/music/game.mp3"
MUSIC_BOSS = "assets/music/boss.mp3"

def play_music(path, volume=0.5, loop=True, fade_ms=600):
    try:
        pygame.mixer.music.fadeout(fade_ms)
    except Exception:
        pass
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0, 0.0, fade_ms)
    except Exception as e:
        print("[AVISO] No se pudo iniciar música:", e)

class Volumes:
    def __init__(self, s_gameover, s_shoot, s_explosion, s_power):
        self.master = 1.0
        self.sfx = 1.0
        self.music = 0.5
        self.muted = False
        self.s_gameover = s_gameover
        self.s_shoot = s_shoot
        self.s_explosion = s_explosion
        self.s_power = s_power
        self.apply()

    def music_effective(self):
        return (0.0 if self.muted else self.music) * self.master

    def apply(self):
        pygame.mixer.music.set_volume(self.music_effective())
        if self.s_gameover:  self.s_gameover.set_volume(0.6 * (0.0 if self.muted else self.sfx) * self.master)
        if self.s_shoot:     self.s_shoot.set_volume(0.4 * (0.0 if self.muted else self.sfx) * self.master)
        if self.s_explosion: self.s_explosion.set_volume(0.55* (0.0 if self.muted else self.sfx) * self.master)
        if self.s_power:     self.s_power.set_volume(0.6 * (0.0 if self.muted else self.sfx) * self.master)
