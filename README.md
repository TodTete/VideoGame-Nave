---

# 🚀 Game Nave

Juego arcade 2D hecho con **Python + Pygame**.
Esquiva fragmentos, recoge **power-ups**, carga **bombas** y enfréntate a un **jefe** en cada nivel.
Incluye **fondos GIF animados con transición**, **pantallas de nivel / intro de jefe**, **cámara con paneo y temblor**, **hiscore** y **sonidos**.

[![Repo](https://img.shields.io/badge/GitHub-TodTete-blue?logo=github)](https://github.com/TodTete)
[![Status](https://img.shields.io/badge/status-en%20desarrollo-orange)](#estado)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![Pygame](https://img.shields.io/badge/pygame-2.x-3776AB)
![Pillow](https://img.shields.io/badge/pillow-10.x-555)

---

## 🎮 Gameplay

* **Objetivo:** sumar puntos destruyendo cubos rojos.
* **Jefe por nivel:** aparece al alcanzar **250 × nivel** puntos.
  Al derrotarlo:

  * Subes de nivel (pantalla **“NIVEL X”**),
  * **Se reinician las vidas (3)**,
  * Los cubos caen más rápido y el siguiente jefe es más agresivo.
* **Fondo animado:** durante el jefe cambia a `fondo-gf.gif` con **transición suave** y vuelve al normal al terminar.
* **Intro de jefe (cinemática corta):** bandas negras + enfoque al jefe antes de empezar la pelea.
* **Cámara dinámica:** paneo suave que sigue a la nave (en X e Y) y **temblor** al impactar la bomba.

### Power-ups 🔻

* **S** → Aumenta **velocidad** de la nave (8 s).
* **P** → **Disparo rápido** (8 s).
* **F** → Queda “listo”; **mantén `F`** para **ralentizar** los obstáculos mientras dure (8 s).

### Bomba 💣 (solo en jefe)

* Aparece como **pickup** durante el combate contra el jefe.
* Al **recogerla**, se **guarda** en tu inventario (`Bombas: N` en el HUD).
* **Lánzala manualmente con `B`**: vuela hacia el jefe y causa **gran daño**.
* El impacto activa **temblor de cámara**.

### Jefe con ataques variados

Patrones rotativos:

1. **Aimed** (dirigidos al jugador)
2. **Spread** (abanico)
3. **Wave** (trayectorias sinusoidales)
4. **Burst** (ráfagas rápidas)
5. **Laser** (telegrafiado: aviso y luego rayo)

---

## ⌨️ Controles

* **Flechas**: mover nave
* **SPACE**: disparo normal
* **B**: **lanzar bomba** (si recogiste una y el **jefe está activo**)
* **F**: usar el poder de **ralentización** (si tienes el power-up F)
* **ENTER**: **pausa** / reanudar
* **F11**: pantalla completa
* **M**: silenciar
* **ESC**: salir (o navegar entre estados)

---

## ✨ Características

* 🛩️ **Nave** con inclinación (tilt) en giros.
* 🎥 **Cámara con paneo** (suavizado) y **temblor** en explosiones grandes.
* 👾 **Jefes** con **HP bar**, **patrones de ataque** variados y **intro** con enfoque.
* 💣 **Bomba recogible** y **lanzable** a voluntad (inventario y HUD).
* 🧩 **Power-ups** (S, F, P) con **timers** en HUD.
* 🖼️ **Fondos GIF** animados con **crossfade** a fondo de jefe.
* ⏸️ **Pausa** a pantalla negra.
* 🏆 **Hiscore** persistente (`hiscore.txt`).
* 🔊 Sonidos opcionales.

---

## 📦 Requisitos

* **Python 3.10+**
* **Pygame 2.x**
* **Pillow 10.x** (para GIF animados)

### Instalación

```bash
# 1) Clonar
git clone https://github.com/TodTete/GameNave.git
cd GameNave

# 2) (Opcional) Crear venv
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3) Instalar dependencias
pip install -r requirements.txt
# o manualmente:
pip install pygame pillow
```

**requirements.txt** sugerido:

```
pygame>=2.5.0
Pillow>=10.0.0
```

---

## ▶️ Ejecutar

Asegúrate de tener en `assets/`:

* **Fondos**: `fondo.gif`, `fondo-gf.gif`
* **Sonidos** (opcionales):
  `game-start-317318.mp3`, `game-over-381772.mp3`, `laser-shot-ingame-230500.mp3`,
  `wood-crate-destory-2-97263.mp3`, `boss.mp3`, `powerup.mp3`

Luego:

```bash
python -m src.main
# o si ejecutas desde la raíz con main.py directo
python src/main.py
```

---

## 🗂️ Estructura del proyecto (modular)

```
GameNave/
├─ assets/
│  ├─ fondo.gif
│  ├─ fondo-gf.gif
│  ├─ game-start-317318.mp3
│  ├─ game-over-381772.mp3
│  ├─ laser-shot-ingame-230500.mp3
│  ├─ wood-crate-destory-2-97263.mp3
│  ├─ boss.mp3
│  └─ powerup.mp3
├─ src/
│  ├─ main.py          # punto de entrada
│  ├─ game.py          # loop principal, estados, reglas, HUD y entradas
│  ├─ ui.py            # dibujo de menús, HUD y pantallas
│  ├─ entities.py      # Jugador, Boss, enemigos
│  ├─ powerups.py      # Power-ups y lógica de bomba (pickup/proyectil)
│  ├─ background.py    # AnimatedBackground (fondos GIF + crossfade)
│  ├─ camera.py        # Cámara (paneo + temblor) y helpers cam_apply_*
│  └─ utils.py         # constantes, colores, helpers (texto/sonido/hiscore)
├─ requirements.txt
├─ README.md
└─ LICENSE
```

> Si cambias rutas, ajusta las cargas de `assets/` en el código.

---

## 🧠 Detalles técnicos

* **Estados de juego:** `MENU`, `LEVEL_INTRO`, `BOSS_INTRO`, `JUGANDO`, `PAUSA`, `GAME_OVER`.
* **Jefe por nivel:** se activa cuando `puntaje >= 250 * nivel`.
* **Vidas:** se **reinician a 3** al comenzar cada nivel (`LEVEL_INTRO`).
* **Cámara:**

  * Paneo: `lerp` hacia un **offset** dependiente de la posición de la nave.
  * Temblor: amplitud y duración configurables; se dispara en impacto de **bomba**.
* **Bomba:**

  * `BombPickup` aparece periódicamente durante el jefe (timeout si no se recoge).
  * Al recogerla, incrementa `bomb_stock`.
  * Tecla **`B`** lanza `BombProjectile` hacia el jefe (daño alto + shake).
* **Boss patterns:** rotan cada cierto tiempo; **laser** incluye **pre-aviso** visual.
* **Fondos:** `AnimatedBackground` gestiona frames y **transiciones**.

---

## 🧪 Troubleshooting

* **El juego se “cierra”/para con `KeyboardInterrupt`:**
  Eso indica una interrupción manual (Ctrl+C) o cierre de ventana. No es un crash.
* **Audio no inicializa:**
  En equipos sin salida de audio, la carga está envuelta en `try/except`. Puedes desactivar sonidos o verificar drivers.
* **GIF estático / sin animación:**
  Instala **Pillow** y revisa que los GIF existan y sean animados.
* **Rendimiento bajo con GIF:**
  Usa GIFs optimizados (≤800×600, menos frames) o cambia a imágenes estáticas.

---

## 🧰 Ejecutable (opcional)

Con **PyInstaller**:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed \
  --add-data "assets/fondo.gif;assets" \
  --add-data "assets/fondo-gf.gif;assets" \
  --add-data "assets/*.mp3;assets" \
  src/main.py
```

El binario estará en `dist/`.

---

## 📸 Capturas (placeholders)

* Menú principal renovado (instrucciones y mejor legibilidad)
* Pantalla “NIVEL 1”
* Enfoque de **BOSS_INTRO** (con bandas y marco)
* HUD mostrando **Bombas: N (B)**
* Impacto de bomba con **temblor** de cámara

---

## 🗺️ Roadmap

* [ ] Varias clases de jefes (sprites y patrones únicos)
* [ ] Partículas/estela en nave y colisiones
* [ ] Tabla online de puntuaciones
* [ ] Skins/temas visuales con selector en el menú
* [ ] Modo “endless” y “boss rush”

---

## 👤 Autor

**TodTete**
Créditos in-game: `created by: TodTete`

---

## 📄 Licencia

Este proyecto se distribuye bajo licencia **MIT**.
Consulta [`LICENSE`](LICENSE) para más detalles.

---
