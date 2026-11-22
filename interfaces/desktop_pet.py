# -*- coding: utf-8 -*-
"""Zero · Mascota de escritorio (flotante)."""
from __future__ import annotations
import sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtCore import Qt, QTimer, QPoint, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QMenu, QLabel)

from core.chat_session import ChatSession
from pets.sprite_player import SpritePlayer

PET_HEIGHT_PX = 220
ACCENT = "#58a6ff"
NAMES = {"zero": "Zero"}


class DesktopPet(QWidget):
    chat_requested = Signal()
    repos_requested = Signal()
    memory_requested = Signal()
    settings_requested = Signal()
    quit_requested = Signal()

    def __init__(self, session: ChatSession):
        super().__init__()
        self.session = session
        self.setWindowTitle("Zero")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        folder = ROOT / "assets" / "zero" / "sprites"
        self.player = None
        try:
            import json
            size = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))["size"]
            scale = PET_HEIGHT_PX / float(size[1])
        except Exception:
            scale = 0.7
        try:
            self.player = SpritePlayer(folder, scale=scale)
            lay.addWidget(self.player)
        except Exception as e:
            lbl = QLabel("Zero"); lbl.setStyleSheet("color:#e6edf3; background:#161b22; border-radius:10px; padding:20px;")
            lay.addWidget(lbl)
        self.adjustSize()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 24, screen.bottom() - self.height() - 8)

        self._press = None
        self._dragged = False
        self._last = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._press = event.globalPosition().toPoint()
            self._drag_offset = self._press - self.frameGeometry().topLeft()
            self._last = self._press
            self._dragged = False
            event.accept()

    def mouseMoveEvent(self, event):
        if self._press is None:
            return
        pos = event.globalPosition().toPoint()
        if not self._dragged and (pos - self._press).manhattanLength() > 6:
            self._dragged = True
            if self.player:
                self.player.play("walking")
        if self._dragged:
            if self.player and self._last:
                dx = pos.x() - self._last.x()
                if dx >= 2 and hasattr(self.player, "set_facing"):
                    self.player.set_facing("right")
                elif dx <= -2 and hasattr(self.player, "set_facing"):
                    self.player.set_facing("left")
            self.move(pos - self._drag_offset)
        self._last = pos

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._press:
            was = self._dragged
            self._press = None
            self._dragged = False
            self._last = None
            if not was:
                self.chat_requested.emit()
            elif self.player:
                self.player.play("idle")

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu{background:#161b22;color:#e6edf3;border:1px solid #2a313c;padding:6px;font-size:13px;} QMenu::item{padding:7px 26px 7px 14px;border-radius:6px;} QMenu::item:selected{background:#2a313c;color:#58a6ff;}")
        a = menu.addAction("Chat"); a.triggered.connect(self.chat_requested.emit)
        b = menu.addAction("Repos"); b.triggered.connect(self.repos_requested.emit)
        c = menu.addAction("Memoria"); c.triggered.connect(self.memory_requested.emit)
        d = menu.addAction("Ajustes"); d.triggered.connect(self.settings_requested.emit)
        menu.addSeparator()
        q = menu.addAction("Salir"); q.triggered.connect(self.quit_requested.emit)
        menu.exec(event.globalPos())

    def play(self, state):
        if self.player:
            try:
                self.player.play(state)
            except Exception:
                pass
