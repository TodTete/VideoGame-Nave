
---

# 🌌 Spaces Astro

Arcade 2D hecho con **Python + Pygame**.
Esquiva asteroides, recoge **power-ups**, consigue **bombas** durante el jefe y supera niveles cada vez más intensos.
Incluye **fondos GIF animados** (juego y menú), **transiciones**, **cámara con paneo**, **hiscore**, **menús**, y **música**.

[![Repo](https://img.shields.io/badge/GitHub-TodTete-blue?logo=github)](https://github.com/TodTete)
[![Status](https://img.shields.io/badge/status-en%20desarrollo-orange)](#estado)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![Pygame](https://img.shields.io/badge/pygame-2.x-3776AB)
![Pillow](https://img.shields.io/badge/pillow-10.x-555)

---

## 🎮 Gameplay

* **Objetivo:** sumar puntos destruyendo asteroides.
* **Jefe por nivel:** aparece al alcanzar **250 × nivel** puntos.
  Al derrotarlo:

  * Subes de nivel (pantalla **“NIVEL X”**).
  * **Se reinician las vidas a 3**.
  * Aumenta la **velocidad de caída** y el siguiente jefe es **más agresivo**.
* **Fondos animados:**

  * En juego: `fondo.gif` (normal) y `fondo-gf.gif` (modo jefe) con **crossfade**.
  * En menús: `space.gif` como **background animado**.
* **Intro de jefe:** bandas negras + marco de enfoque antes de empezar.
* **Cámara dinámica:** paneo suave siguiendo a la nave.

### Power-ups 🔻

* **S** → Aumenta **velocidad** de la nave (8 s).
* **P** → **Disparo rápido** (8 s).
* **F** → Mientras dure (8 s), **mantén `F`** para **ralentizar** los obstáculos.

### Bomba 💣 (durante el jefe)

* Aparece como **pickup** en la pelea.
* Al **recogerla**, se **dispara automáticamente** contra el jefe (alto daño).

### Patrones del jefe

1. **Aimed** (balas dirigidas)
2. **Spread** (abanico)
3. **Wave** (trayectoria sinusoidal)
4. **Burst** (ráfagas rápidas)
5. **Laser** (telegrafiado: aviso → rayo)

---

## 🧭 Menús

* **Inicio**: empieza la partida.
* **Dificultad**: **Baja / Media / Alta / Extrema**.

  * **EXTREMA**: mucho más dura (enemigos más rápidos, jefes con más vida, disparan más seguido, cambian de patrón más rápido y se mueven más).
* **Opciones**: sliders para **Volumen Maestro**, **Efectos (SFX)** y **Música**.
* **Créditos** al pie.

---

## ⌨️ Controles

* **Flechas**: mover
* **SPACE**: disparo
* **F**: activar ralentización (si tienes el power-up F)
* **ENTER**: pausa / reanudar
* **F11**: pantalla completa
* **M**: silenciar
* **ESC**: salir / volver en menús

> La bomba se dispara **automáticamente** al recogerla (solo durante el jefe).

---

## 🎧 Música y tipografía

* **Música de juego**: `assets/game.mp3`
* **Música de jefe**: `assets/boss.mp3`
* **Tipografía**: **Retronoid** (TTF/OTF). El juego intenta cargar:

  * `assets/Retronoid.ttf`, `assets/Retronoid.otf`, o en raíz `Retronoid.ttf/otf`.
    Copia tu archivo a `assets/Retronoid.ttf` para asegurar su uso.

---

## ✨ Detalles visuales

* **Título del menú** en **dorado** (no amarillo).
* Encabezados **OPCIONES** y **DIFICULTAD** en **morado** para no confundirlos con ítems.
* **Bala** ligeramente **más grande** para mejor lectura.

---

## 📦 Requisitos

* **Python 3.10+**
* **Pygame 2.x**
* **Pillow 10.x** (GIF animados)

**Instalación rápida**

```bash
# 1) Clona el repo
git clone https://github.com/TodTete/SpacesAstro.git
cd SpacesAstro

# 2) (Opcional) Entorno virtual
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3) Dependencias
pip install -r requirements.txt
# o manual:
pip install pygame pillow
```

**requirements.txt**

```
pygame>=2.5.0
Pillow>=10.0.0
```

---

## ▶️ Ejecutar

Asegúrate de tener en `assets/`:

* **Fondos (juego)**: `fondo.gif`, `fondo-gf.gif`
* **Fondo (menú)**: `space.gif`
* **Sprites**: `asteroides.gif`, `nave.gif`, `bala.png`
* **Audio**: `game.mp3`, `boss.mp3`, `game-over-381772.mp3`, `laser-shot-ingame-230500.mp3`,
  `wood-crate-destory-2-97263.mp3`, `powerup.mp3`
* **Fuente**: `Retronoid.ttf` (recomendado en `assets/`)

Ejecuta:

```bash
python main.py
```

---

## 🗂️ Estructura del proyecto

```
SpacesAstro/
├─ assets/
│  ├─ asteroides.gif
│  ├─ nave.gif
│  ├─ bala.png
│  ├─ fondo.gif
│  ├─ fondo-gf.gif
│  ├─ space.gif
│  ├─ game.mp3
│  ├─ boss.mp3
│  ├─ game-over-381772.mp3
│  ├─ laser-shot-ingame-230500.mp3
│  ├─ wood-crate-destory-2-97263.mp3
│  ├─ powerup.mp3
│  └─ Retronoid.ttf
├─ game/
│  ├─ __init__.py
│  ├─ constants.py
│  ├─ utils.py
│  ├─ gif.py
│  ├─ assets.py
│  ├─ background.py
│  ├─ camera.py
│  ├─ state.py
│  └─ entities/
│     ├─ player.py
│     ├─ bullet.py
│     ├─ enemy.py
│     ├─ boss.py
│     └─ powerups.py
├─ hiscore.txt
├─ main.py
├─ requirements.txt
├─ README.md
└─ LICENSE
```

> Si mueves rutas/archivos, ajusta las cargas en el código.

---

## 🧪 Troubleshooting

* **Pillow no disponible** → los GIF se verán estáticos (el juego sigue).
* **Audio no inicia** → el juego continúa sin sonido (revisa drivers/salidas).
* **Bajo rendimiento con GIF grandes** → usa GIF optimizados (≤800×600, menos frames).

---

## 🗺️ Roadmap

* [ ] Más jefes con patrones únicos
* [ ] Partículas y estelas
* [ ] Tabla online de puntuaciones
* [ ] Skins/temas visuales con selector
* [ ] Modos “endless” y “boss-rush”
* [ ] Cada nivel con Jefes distintos y mecanicas distintas
---

## 👤 Autor

**TodTete**
Créditos in-game: `created by: @TodTete / Ricardo Vallejo Sanchez`

---

## 📄 Licencia

Este proyecto se distribuye bajo licencia **MIT**.
Consulta [`LICENSE`](LICENSE) para más detalles.

---
