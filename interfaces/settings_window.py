# -*- coding: utf-8 -*-
"""Zero · Ajustes."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QMessageBox)
from core import settings as S, codex_pet_importer as CPI


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        lay.addWidget(QLabel("Token de GitHub (PAT):"))
        self.tok = QLineEdit()
        self.tok.setEchoMode(QLineEdit.EchoMode.Password)
        self.tok.setText(S.get_token())
        lay.addWidget(self.tok)
        b = QPushButton("Guardar token")
        b.setObjectName("primary")
        b.clicked.connect(self.save_tok)
        lay.addWidget(b)

        lay.addWidget(QLabel(""))
        lay.addWidget(QLabel("Modelo LLM (OpenAI-compatible, opcional):"))
        self.base = QLineEdit(); self.base.setPlaceholderText("https://api.openai.com/v1")
        self.key = QLineEdit(); self.key.setEchoMode(QLineEdit.EchoMode.Password); self.key.setPlaceholderText("API key")
        self.model = QLineEdit(); self.model.setPlaceholderText("gpt-4o-mini")
        cfg = S.get_llm()
        self.base.setText(cfg["base_url"]); self.key.setText(cfg["api_key"]); self.model.setText(cfg["model"])
        for w in (self.base, self.key, self.model):
            lay.addWidget(w)
        b2 = QPushButton("Guardar modelo")
        b2.clicked.connect(self.save_llm)
        lay.addWidget(b2)

        lay.addWidget(QLabel(""))
        lay.addWidget(QLabel("Importar Codex Pet (por ID, ej. genshin-impact-keqing):"))
        self.petid = QLineEdit(); self.petid.setPlaceholderText("genshin-impact-keqing")
        lay.addWidget(self.petid)
        b3 = QPushButton("Importar pet")
        b3.clicked.connect(self.import_pet)
        lay.addWidget(b3)

        lay.addStretch(1)

    def save_tok(self):
        S.set_token(self.tok.text().strip())
        QMessageBox.information(self, "Zero", "Token guardado.")

    def save_llm(self):
        S.set_llm(self.base.text().strip(), self.key.text().strip(), self.model.text().strip())
        QMessageBox.information(self, "Zero", "Modelo guardado.")

    def import_pet(self):
        pid = self.petid.text().strip()
        if not pid:
            return
        try:
            pid2, name = CPI.import_pet(pid)
            QMessageBox.information(self, "Zero", f"Pet importado: {name} ({pid2}). Reinicia Zero para usarlo.")
        except Exception as e:
            QMessageBox.warning(self, "Zero", f"Error importando pet:\n{e}")
