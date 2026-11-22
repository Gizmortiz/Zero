# -*- coding: utf-8 -*-
"""Zero · Ventana maestra."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame)
from PySide6.QtCore import Qt

ACCENT = "#58a6ff"


class MasterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zero")
        self.resize(900, 620)
        self.setStyleSheet(f"""
            QWidget {{ background:#0d1117; color:#e6edf3; font-family:'Segoe UI',Arial; font-size:13px; }}
            QFrame#card {{ background:#161b22; border:1px solid #2a313c; border-radius:10px; }}
            QPushButton {{ background:transparent; border:1px solid #2a313c; border-radius:8px; padding:6px 12px; color:#e6edf3; }}
            QPushButton:hover {{ border-color:#8b949e; }}
            QPushButton#primary {{ background:{ACCENT}; color:#0d1117; border:none; font-weight:bold; }}
            QLabel#title {{ font-size:18px; font-weight:bold; color:{ACCENT}; }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        head = QHBoxLayout()
        t = QLabel("Zero"); t.setObjectName("title")
        head.addWidget(t); head.addStretch(1)
        self.btn_chat = QPushButton("Chat")
        self.btn_repos = QPushButton("Repos")
        self.btn_memory = QPushButton("Memoria")
        self.btn_settings = QPushButton("Ajustes")
        for b in (self.btn_chat, self.btn_repos, self.btn_memory, self.btn_settings):
            head.addWidget(b)
        lay.addLayout(head)

        self.stack = QStackedWidget()
        lay.addWidget(self.stack, 1)

        self.btn_chat.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_repos.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_memory.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_settings.clicked.connect(lambda: self.stack.setCurrentIndex(3))

    def add_page(self, w):
        self.stack.addWidget(w)
