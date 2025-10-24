from .entities.bullet import Bala
from . import assets as Assets

def shoot_pattern(juego, selected_ship):
    mx, my = juego["player"].get_muzzle_world()
    vy = juego["vel_bala"]

    if selected_ship == "FERNANDA":
        juego["balas"].append(Bala(mx, my, vy=vy, image=Assets.BALA2_IMG))
    elif selected_ship == "MARLIN":
        juego["balas"].append(Bala(mx - 12, my, vy=vy))
        juego["balas"].append(Bala(mx + 12, my, vy=vy))
    elif selected_ship == "TETE":
        juego["balas"].append(Bala(mx, my, vy=vy))
        juego["balas"].append(Bala(mx - 14, my, vy=vy))
        juego["balas"].append(Bala(mx + 14, my, vy=vy))
    else:  # BRAYAN
        juego["balas"].append(Bala(mx, my, vy=vy))
