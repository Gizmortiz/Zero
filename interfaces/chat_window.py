# -*- coding: utf-8 -*-
"""Zero · Chat."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QLineEdit, QPushButton, QLabel)
from PySide6.QtCore import Qt

from core import chat_engine, self_improve, agent_graph


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.repo_ctx = ""
        self.owner = ""
        self.repo = ""
        self.history = []
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        self.status = QLabel("Sin repo seleccionado. Carga uno en 'Repos'.")
        lay.addWidget(self.status)

        self.view = QTextBrowser()
        lay.addWidget(self.view, 1)

        fb = QHBoxLayout()
        self.btn_good = QPushButton("👍 Útil")
        self.btn_bad = QPushButton("👎 No útil")
        self.btn_good.clicked.connect(lambda: self._feedback("good"))
        self.btn_bad.clicked.connect(lambda: self._feedback("bad"))
        fb.addWidget(self.btn_good); fb.addWidget(self.btn_bad); fb.addStretch(1)
        lay.addLayout(fb)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Pregunta sobre el repo…")
        self.input.returnPressed.connect(self.send)
        self.btn = QPushButton("Enviar")
        self.btn.setObjectName("primary")
        self.btn.clicked.connect(self.send)
        row.addWidget(self.input, 1); row.addWidget(self.btn)
        lay.addLayout(row)

    def set_repo(self, owner, repo, ctx):
        self.repo_ctx = ctx
        self.owner = owner
        self.repo = repo
        self.status.setText(f"Repo activo: {owner}/{repo}")
        self.view.append(f"<b>Zero:</b> Repo cargado: {owner}/{repo}. Pregúntame lo que quieras.")

    def send(self):
        text = self.input.text().strip()
        if not text:
            return
        if not self.repo_ctx:
            self.input.clear()
            self.view.append("<b>Zero:</b> Aún no hay repo cargado. Ve a la pestaña 'Repos', escribe owner/repo y pulsa 'Cargar'.")
            return
        self.input.clear()
        self.view.append(f"<b>Tú:</b> {text}")
        self.btn.setEnabled(False)
        try:
            ans = agent_graph.run(text, repo_ctx=self.repo_ctx, owner=self.owner, repo=self.repo)
            self.view.append(f"<b>Zero:</b> {ans}")
            self.history.append({"role": "user", "content": text})
            self.history.append({"role": "assistant", "content": ans})
        except Exception as e:
            self.view.append(f"<b>Zero:</b> Error: {e}")
        finally:
            self.btn.setEnabled(True)

    def _feedback(self, kind):
        self_improve.record_feedback(kind, detail="", context=self.repo_ctx[:200])

