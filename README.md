# 🚀 Game Nave

Juego arcade 2D hecho con **Python + Pygame**.
Esquiva fragmentos, recoge **power-ups** y enfréntate a un **jefe** en cada nivel.
Incluye **fondo animado (GIF) con transición**, **pantallas de nivel**, **pausa**, **hiscore** y **créditos**.

[![Repo](https://img.shields.io/badge/GitHub-TodTete-blue?logo=github)](https://github.com/TodTete)
[![Status](https://img.shields.io/badge/status-en%20desarrollo-orange)](#estado)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![Pygame](https://img.shields.io/badge/pygame-2.x-3776AB)
![Pillow](https://img.shields.io/badge/pillow-10.x-555)

---

## 🎮 Gameplay

* **Objetivo:** sumar puntos destruyendo cubos rojos.
* **Jefe por nivel:** aparece al alcanzar **250 × nivel** puntos. Al derrotarlo:

  * Subes de nivel (aparece pantalla **“Nivel X”**),
  * **Se reinician las vidas (3)**,
  * Los cubos **caen más rápido** y el jefe **se mueve/dispara más rápido**.
* **Fondo animado:** en el jefe cambia a `fondo-gf.gif` con **transición suave** y vuelve al normal al terminar.

### Power-ups que caen 🔻

* **S** → Aumenta **velocidad** de la nave (8 s).
* **P** → **Disparo rápido** (8 s).
* **F** → Al recogerlo queda “listo”; **mantén `F`** para **ralentizar** los obstáculos mientras dure el efecto (8 s).

---

## ⌨️ Controles

* **Flechas**: mover nave
* **SPACE**: disparar
* **ENTER**: **pausar** / reanudar (pantalla negra “PAUSA”)
* **F**: activar/usar poder de **ralentización** (si tienes el power-up F)
* **F11**: pantalla completa
* **M**: silenciar
* **ESC**: salir (o navegar entre estados)

---

## ✨ Características

* 🛩️ **Nave** con inclinación (tilt) al mover a izquierda/derecha.
* 👾 **Jefe** con barra de vida, patrón de disparo y movimiento lateral.
* 📈 **Dificultad progresiva** nivel a nivel (jefe y fragmentos más rápidos).
* 🧩 **Power-ups** (S, F, P) con HUD de tiempo restante.
* 🖼️ **Fondos GIF animados** con transición al modo jefe.
* ⏸️ **Pausa** en pantalla negra.
* 🏆 **Hiscore** persistente (`hiscore.txt`).
* 🔊 Soporte de **sonidos** (opcional).

---

## 📦 Requisitos

* **Python 3.10+**
* **Pygame 2.x**
* **Pillow 10.x** (para GIF animados)

### Instalación rápida

```bash
# 1) Clonar
git clone [https://github.com/TodTete/GameNave.git](https://github.com/TodTete/VideoGame-Nave)
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

Coloca estos archivos **en la misma carpeta** que el script principal (por ejemplo `main.py`):

* Fondos: `fondo.gif`, `fondo-gf.gif`
* Sonidos (opcionales):

  * `game-start-317318.mp3`
  * `game-over-381772.mp3`
  * `laser-shot-ingame-230500.mp3`
  * `wood-crate-destory-2-97263.mp3`
  * `boss.mp3`
  * `powerup.mp3`

Luego:

```bash
python main.py
```

---

## 🗂️ Estructura recomendada

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
├─ main.py
├─ requirements.txt
├─ README.md
└─ LICENSE
```

> Si cambias la ubicación, ajusta las rutas de carga en el código.

---

## 🧠 Detalles técnicos

* **Estados**: `MENU`, `LEVEL_INTRO`, `JUGANDO`, `PAUSA`, `GAME_OVER`.
* **Niveles**: jefe aparece cuando `puntaje >= 250 * nivel`.
* **Reset de vidas** al iniciar cada nivel (pantalla “NIVEL X”).
* **Transición de fondo**: `AnimatedBackground` hace crossfade entre `fondo.gif` y `fondo-gf.gif`.
* **Invulnerabilidad breve** al recibir daño.
* **HUD**: puntaje, nivel, vidas, aviso de jefe y timers de power-ups.

---

## 🧪 Problemas comunes (Troubleshooting)

* **Se cierra al iniciar / audio falla:**
  Asegúrate de tener dispositivos/soporte de audio. Si no usas sonidos, puedes envolver `pygame.mixer.init()` en `try/except` o remover cargas de audio.
* **Fondos no animan:**
  Instala **Pillow** (`pip install pillow`) y confirma que `fondo.gif`/`fondo-gf.gif` existan y sean GIF animados válidos.
* **Rendimiento bajo:**
  Usa GIFs optimizados (resolución <= 800×600 y menos frames), o cambia a imágenes estáticas.

---

## 🧰 Construir ejecutable (opcional)

Con **PyInstaller**:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed \
  --add-data "assets/fondo.gif;assets" \
  --add-data "assets/fondo-gf.gif;assets" \
  --add-data "assets/*.mp3;assets" \
  main.py
```

El binario quedará en `dist/`.

---

## 📸 Capturas (placeholders)

> Reemplaza con tus imágenes/gifs reales.

* Menú de inicio (simple y limpio)
* Pantalla “NIVEL 1”
* Combate contra el jefe (fondo alterno)

---

## 🗺️ Roadmap

* [ ] Disparo del jefe teledirigido hacia la nave
* [ ] Efecto de **escape flame** en la nave
* [ ] Varios tipos de jefes por mundo
* [ ] Tabla de puntuaciones online
* [ ] Skins para la nave

---

## 👤 Autor

**TodTete**
Créditos in-game: `created by: TodTete`

---

## 📄 Licencia

Este proyecto se distribuye bajo licencia **MIT**.
Consulta el archivo [`LICENSE`](LICENSE) para más detalles.

---

## 🤝 Agradecimientos

* Comunidad de **Pygame**
* Autores de los **assets** (sonidos/fondos) utilizados

---

## 🔗 Notas de integración

* El título en ventana es **“Game Nave”**.
* La nave se inclina (tilt) al moverse a los lados.
* Pausa con ENTER muestra una **pantalla negra** con el rótulo **PAUSA**.
* Los power-ups y el jefe escalan **dificultad** entre niveles.

---
