# -*- coding: utf-8 -*-
"""Zero · Herramientas del sistema (computer use)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextBrowser, QLineEdit, QMessageBox)
from core import computer_use as CU


class SystemToolsWindow(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        row = QHBoxLayout()
        self.btn_shot = QPushButton("Capturar pantalla")
        self.btn_windows = QPushButton("Listar ventanas")
        self.btn_active = QPushButton("Ventana activa")
        row.addWidget(self.btn_shot); row.addWidget(self.btn_windows); row.addWidget(self.btn_active)
        lay.addLayout(row)

        row2 = QHBoxLayout()
        self.app_input = QLineEdit(); self.app_input.setPlaceholderText("app o URL (ej. notepad, https://...)")
        self.btn_launch = QPushButton("Abrir")
        row2.addWidget(self.app_input, 1); row2.addWidget(self.btn_launch)
        lay.addLayout(row2)

        row3 = QHBoxLayout()
        self.x_input = QLineEdit(); self.x_input.setPlaceholderText("x")
        self.y_input = QLineEdit(); self.y_input.setPlaceholderText("y")
        self.btn_click = QPushButton("Clic")
        row3.addWidget(self.x_input); row3.addWidget(self.y_input); row3.addWidget(self.btn_click)
        lay.addLayout(row3)

        self.view = QTextBrowser()
        lay.addWidget(self.view, 1)

        self.btn_shot.clicked.connect(self.do_shot)
        self.btn_windows.clicked.connect(self.do_windows)
        self.btn_active.clicked.connect(self.do_active)
        self.btn_launch.clicked.connect(self.do_launch)
        self.btn_click.clicked.connect(self.do_click)

    def do_shot(self):
        r = CU.screenshot()
        self.view.append(f"Captura guardada: {r.get('path')} ({r.get('size')})")

    def do_windows(self):
        r = CU.list_windows()
        titles = [w["title"] for w in r.get("windows", [])]
        self.view.setPlainText("\n".join(titles))

    def do_active(self):
        r = CU.active_window_title()
        self.view.append(f"Ventana activa: {r.get('title')}")

    def do_launch(self):
        t = self.app_input.text().strip()
        if not t:
            return
        r = CU.launch_app(t)
        self.view.append(f"Abrir {t}: {'OK' if r.get('ok') else r.get('error')}")

    def do_click(self):
        try:
            x = int(self.x_input.text()); y = int(self.y_input.text())
        except ValueError:
            QMessageBox.warning(self, "Zero", "x e y deben ser números.")
            return
        r = CU.click(x, y)
        self.view.append(f"Clic en ({x},{y}): {'OK' if r.get('ok') else r.get('error')}")
