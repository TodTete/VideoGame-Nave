import random, pygame
from .constants import *
from .entities.player import Jugador
from .entities.enemy import crear_enemigos, respawnear_enemigo
from .entities.boss import Boss
from .entities.bullet import Bala
from .entities.powerups import PowerUp, BombPickup, BombProjectile
from .utils import reproducir
from .assets import BALA_IMG  # (asegura carga)

def activar_pantalla_nivel(juego, ahora):
    juego["vidas"] = 3
    juego["player"].rect.centerx = ANCHO // 2
    juego["player"].rect.bottom = ALTO - 10
    juego["player"].angle = 0.0
    juego["player"].target_angle = 0.0
    juego["balas"].clear()
    juego["boss_bullets"].clear()
    juego["powerups"].clear()
    juego["bombs"].clear()
    juego["bomb_pickup"] = None
    juego["invulnerable_hasta"] = 0
    juego["intro_end_time"] = ahora + LEVEL_INTRO_MS
    juego["intro_text"] = f"NIVEL {juego['nivel']}"

def reset_juego():
    player = Jugador(ANCHO//2, ALTO - 10)
    balas = []
    vel_bala = -9
    cadencia_ms = 200
    ultimo_disparo = 0

    enemigos = crear_enemigos(6)
    vel_enemigo_base = 2.0

    nivel = 1; puntaje = 0; vidas = 3
    invulnerable_hasta = 0; invulnerable_ms = 1200

    boss = None; boss_active=False; boss_bullets=[]
    boss_threshold_cleared=set()

    powerups=[]; s_active_until=0; f_active_until=0; p_active_until=0

    estado = JUGANDO
    return {
        "player": player, "balas": balas, "vel_bala": vel_bala,
        "cadencia_ms": cadencia_ms, "ultimo_disparo": ultimo_disparo,
        "enemigos": enemigos, "vel_enemigo_base": vel_enemigo_base,
        "nivel": nivel, "puntaje": puntaje, "vidas": vidas,
        "invulnerable_hasta": invulnerable_hasta, "invulnerable_ms": invulnerable_ms,
        "estado": estado, "game_over_sonido_reproducido": False,
        "boss": boss, "boss_active": boss_active, "boss_bullets": boss_bullets,
        "boss_threshold_cleared": boss_threshold_cleared,
        "powerups": powerups, "s_active_until": s_active_until,
        "f_active_until": f_active_until, "p_active_until": p_active_until,
        "intro_end_time": 0, "intro_text": "", "boss_intro_end": 0,
        "bomb_pickup": None, "bombs": [], "next_bomb_spawn_time": 0,
        "bomb_spawn_interval_ms": 9000
    }
