# -*- coding: utf-8 -*-
"""Zero · Memoria (feedback, estilo, prompts)."""
from __future__ import annotations
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextBrowser, QPushButton, QLineEdit, QMessageBox, QTabWidget)
from core import self_improve, companion


class MemoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        tabs = QTabWidget()
        lay.addWidget(tabs, 1)

        # Feedback tab
        fb = QWidget(); fbl = QVBoxLayout(fb)
        self.fb_view = QTextBrowser()
        fbl.addWidget(self.fb_view)
        b = QPushButton("Refrescar")
        b.clicked.connect(self.refresh)
        fbl.addWidget(b)
        tabs.addTab(fb, "Feedback")

        # Style tab
        st = QWidget(); stl = QVBoxLayout(st)
        self.style_view = QTextBrowser()
        stl.addWidget(self.style_view)
        row = QHBoxLayout()
        self.style_input = QLineEdit(); self.style_input.setPlaceholderText("Nuevo ejemplo de estilo…")
        btn = QPushButton("Añadir")
        btn.clicked.connect(self.add_style)
        row.addWidget(self.style_input, 1); row.addWidget(btn)
        stl.addLayout(row)
        tabs.addTab(st, "Estilo")

        # Prompts tab
        pr = QWidget(); prl = QVBoxLayout(pr)
        self.prompt_view = QTextBrowser()
        prl.addWidget(self.prompt_view)
        row2 = QHBoxLayout()
        self.ver_input = QLineEdit(); self.ver_input.setPlaceholderText("companion_v2")
        btn2 = QPushButton("Registrar versión")
        btn2.clicked.connect(self.register_ver)
        row2.addWidget(self.ver_input, 1); row2.addWidget(btn2)
        prl.addLayout(row2)
        tabs.addTab(pr, "Prompts")

        self.refresh()

    def refresh(self):
        s = self_improve.stats()
        fb = __import__("json").loads((__import__("pathlib").Path(str(ROOT / "memory" / "feedback_log.json")).read_text() if (ROOT / "memory" / "feedback_log.json").exists() else "[]"))
        self.fb_view.setPlainText(f"Total: {s['total']}\nPor señal: {s['by_signal']}\n\nÚltimos 20:\n" + "\n".join(f"- {e['signal']}: {e['detail']}" for e in fb[-20:]))
        # style
        import json
        p = ROOT / "memory" / "style_layer.json"
        d = json.loads(p.read_text()) if p.exists() else {}
        exs = d.get("examples", [])
        self.style_view.setPlainText("\n".join(f"- {e}" for e in exs) if exs else "(sin ejemplos)")
        # prompts
        vs = companion.list_versions()
        cur = companion.current_version()
        self.prompt_view.setPlainText(f"Versión actual: {cur}\nVersiones: {vs}\n\n--- Prompt actual ---\n{companion.load_prompt(cur)}")

    def add_style(self):
        txt = self.style_input.text().strip()
        if not txt:
            return
        companion.add_style_example(txt)
        self.style_input.clear()
        self.refresh()
        QMessageBox.information(self, "Zero", "Ejemplo añadido.")

    def register_ver(self):
        v = self.ver_input.text().strip()
        if not v:
            return
        companion.register_version(v, note="registrado desde UI")
        self.ver_input.clear()
        self.refresh()
        QMessageBox.information(self, "Zero", f"Versión {v} registrada.")
