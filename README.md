# 🧠 Softbody Physics Engine

Un motore fisico custom per la simulazione di **corpi deformabili** (softbody) tramite un modello massa-molla in Python, con rendering grafico tramite **Pygame**.

---

## 📦 Struttura del Progetto

### Oggetti Principali

- **pointMass**: rappresenta una massa puntiforme.
- **beamElement**: connessione elastica tra due masse (molla).
- **polygon / regularPolygon**: struttura geometrica base composta da masse collegate da molle.
- **reticulate**: mesh strutturata di punti e connessioni.
- **springMassBody**: simulazione di corpo deformabile completo.
- **rigidBody**: corpo rigido (non deformabile).

### Funzionalità

- Forze elastiche e di smorzamento
- Gravità personalizzabile
- Punti ancorabili (pinned)
- Rilevamento collisione con terreno
- Costruzione automatica di poligoni regolari e reticolati

---

## ⚙️ Dipendenze

- [Python 3.x](https://www.python.org/)
- [Pygame](https://www.pygame.org/)
- [NumPy](https://numpy.org/)

Installa le dipendenze con:
```bash
pip install pygame numpy
```
# 🧪 Esempio di utilizzo
```python
import pygame
from your_module import springMassBody, regularPolygon

# Setup pygame
screen = pygame.display.set_mode((800, 800))

# Crea un poligono regolare
poly = regularPolygon(center=(400, 400), sidesNum=6, radius=80, surf=screen)

# Crea il corpo softbody
softbody = springMassBody(poly=poly, surf=screen, pinpoint=True)

# Ciclo principale
running = True
while running:
    screen.fill((255, 255, 255))

    softbody.initialize()
    softbody.draw()

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
```
# ✍️ Autore
Creato da [contemporaneamente](http://github.com/contemporaneamente)


