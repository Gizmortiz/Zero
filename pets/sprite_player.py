# -*- coding: utf-8 -*-
"""
I-Pet · Reproductor de sprites (para cualquier I-Pet)

Ventana/widget TOTALMENTE INDEPENDIENTE. Lee assets/<pet>/sprites/manifest.json
y anima las tiras de cuadros (cada estado = un PNG con los cuadros en fila).

Prueba (con botones para cada estado):

    python pets/sprite_player.py wukong
    python pets/sprite_player.py takeo

Uso dentro de otra ventana:

    player = SpritePlayer(Path("assets/wukong/sprites"), scale=0.8)
    player.play("searching")
    player.state_finished.connect(...)   # estados sin loop avisan al terminar

Formato del manifest (el mismo de Takeo):
    {"name", "size": [ancho, alto], "default": "idle",
     "states": {"idle": {"file", "frames", "fps", "loop", "then"?}, ...}}
El ancho de cada cuadro se calcula como ancho_png / frames, así que el
campo "size" es solo informativo.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class SpritePlayer(QWidget):
    """Anima un I-Pet según su manifest.json."""

    state_changed = Signal(str)
    state_finished = Signal(str)  # un estado sin loop llegó a su último cuadro

    def __init__(self, sprites_dir: Path | str, scale: float = 0.75, parent: QWidget | None = None):
        super().__init__(parent)
        self.sprites_dir = Path(sprites_dir)
        self.scale = scale
        self.manifest: dict = {}
        self._sheets: dict[str, QPixmap] = {}
        self._frames: list[QPixmap] = []
        self._index = 0
        self._state = ""
        self._facing = "right"
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.load(self.sprites_dir)

    # -- carga -----------------------------------------------------------------
    def load(self, sprites_dir: Path | str) -> None:
        self.sprites_dir = Path(sprites_dir)
        path = self.sprites_dir / "manifest.json"
        self.manifest = json.loads(path.read_text(encoding="utf-8"))
        self._sheets.clear()
        default = self.manifest.get("default", "idle")
        self.play(default)

    @property
    def states(self) -> list[str]:
        return list(self.manifest.get("states", {}))

    @property
    def state(self) -> str:
        return self._state

    def _cut_frames(self, info: dict) -> list[QPixmap]:
        file = info["file"]
        sheet = self._sheets.get(file)
        if sheet is None:
            sheet = QPixmap(str(self.sprites_dir / file))
            self._sheets[file] = sheet
        count = max(1, int(info.get("frames", 1)))
        if sheet.isNull():
            return []
        width = sheet.width() // count
        return [sheet.copy(i * width, 0, width, sheet.height()) for i in range(count)]

    # -- reproducción ----------------------------------------------------------
    def set_facing(self, direction: str) -> None:
        """Orienta horizontalmente la mascota hacia la dirección del movimiento."""
        if direction not in ("left", "right") or direction == self._facing:
            return
        self._facing = direction
        self.update()

    def play(self, state: str) -> None:
        """Cambia de estado. Un estado desconocido usa el estado por defecto."""
        states = self.manifest.get("states", {})
        if state not in states:
            state = self.manifest.get("default", "idle")
        info = states.get(state)
        if info is None:
            return
        frames = self._cut_frames(info)
        if not frames:
            print(f"[sprite_player] No se pudo leer {info['file']} en {self.sprites_dir}")
            return
        self._state = state
        self._frames = frames
        self._index = 0
        self._timer.stop()
        if len(frames) > 1:
            self._timer.start(max(16, int(1000 / max(1, info.get("fps", 8)))))
        self.setFixedSize(self.sizeHint())
        self.update()
        self.state_changed.emit(state)

    def _advance(self) -> None:
        info = self.manifest["states"][self._state]
        self._index += 1
        if self._index >= len(self._frames):
            if info.get("loop", True):
                self._index = 0
            else:
                self._index = len(self._frames) - 1
                self._timer.stop()
                finished = self._state
                self.state_finished.emit(finished)
                then = info.get("then")
                if then and self._state == finished:
                    self.play(then)
                return
        self.update()

    # -- dibujo ----------------------------------------------------------------
    def sizeHint(self) -> QSize:  # noqa: N802 (nombre de Qt)
        if not self._frames:
            return QSize(120, 120)
        f = self._frames[0]
        return QSize(int(f.width() * self.scale), int(f.height() * self.scale))

    def paintEvent(self, event):  # noqa: N802 (nombre de Qt)
        if not self._frames:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        frame = self._frames[min(self._index, len(self._frames) - 1)]
        p.save()
        if self._facing == "left":
            p.translate(self.width(), 0)
            p.scale(-1, 1)
        p.drawPixmap(QRectF(0, 0, self.width(), self.height()), frame, QRectF(frame.rect()))
        p.restore()
        p.end()


class _Demo(QWidget):
    def __init__(self, pet: str):
        super().__init__()
        self.setWindowTitle(f"I-Pet · Prueba de sprites · {pet}")
        self.setStyleSheet(
            "QWidget { background:#0d1117; color:#e6edf3; font-family:'Segoe UI',Arial; }"
            "QPushButton { background:transparent; border:1px solid #2a313c; border-radius:8px; padding:6px 12px; }"
            "QPushButton:hover { border-color:#8b949e; }"
        )
        sprites = PROJECT_ROOT / "assets" / pet / "sprites"
        self.player = SpritePlayer(sprites, scale=1.0)
        self.label = QLabel("")
        self.player.state_changed.connect(lambda s: self.label.setText(f"Estado: {s}"))
        self.label.setText(f"Estado: {self.player.state}")

        lay = QVBoxLayout(self)
        lay.addWidget(self.label)
        lay.addWidget(self.player, 0, Qt.AlignmentFlag.AlignHCenter)
        grid = QGridLayout()
        for i, state in enumerate(self.player.states):
            btn = QPushButton(state)
            btn.clicked.connect(lambda checked=False, s=state: self.player.play(s))
            grid.addWidget(btn, i // 5, i % 5)
        lay.addLayout(grid)


def main() -> int:
    pet = sys.argv[1] if len(sys.argv) > 1 else "wukong"
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = _Demo(pet)
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
