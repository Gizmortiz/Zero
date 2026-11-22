# -*- coding: utf-8 -*-
"""Zero · Navegador de repositorios."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QTextBrowser, QTreeWidget, QTreeWidgetItem, QMessageBox)
from PySide6.QtCore import Qt

from core import github_client as GH, settings as S


class RepoBrowser(QWidget):
    repo_selected = None

    def __init__(self, on_select=None):
        super().__init__()
        self.on_select = on_select
        self.owner = ""
        self.repo = ""
        self.current_context = ""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("owner/repo  (ej. anomalyco/opencode)")
        self.btn_load = QPushButton("Cargar")
        self.btn_load.setObjectName("primary")
        row.addWidget(self.input, 1); row.addWidget(self.btn_load)
        lay.addLayout(row)

        self.info = QLabel("")
        self.info.setWordWrap(True)
        lay.addWidget(self.info)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Archivos"])
        lay.addWidget(self.tree, 1)

        self.view = QTextBrowser()
        self.view.setMaximumHeight(180)
        lay.addWidget(self.view)

        self.btn_load.clicked.connect(self.load)
        self.tree.itemClicked.connect(self.on_item)

    def load(self):
        text = self.input.text().strip()
        if "/" not in text:
            QMessageBox.warning(self, "Zero", "Formato: owner/repo")
            return
        owner, repo = text.split("/", 1)
        self.owner, self.repo = owner, repo
        r = GH.get_repo(owner, repo)
        if not r.ok:
            self.info.setText(f"Error: {r.error}")
            QMessageBox.warning(self, "Zero", f"No se pudo cargar el repo:\n{r.error}")
            return
        d = r.data or {}
        self.info.setText(f"{d.get('full_name')} — {d.get('description','')}\n"
                         f"Lenguaje: {d.get('language')} | ★ {d.get('stargazers_count')} | branch: {d.get('default_branch')}")
        QMessageBox.information(self, "Zero", f"Repo cargado: {owner}/{repo}")
        # tree
        self.tree.clear()
        tr = GH.get_tree(owner, repo)
        if tr.ok and isinstance(tr.data, dict):
            paths = [t["path"] for t in tr.data.get("tree", []) if t.get("type") == "blob"]
            for p in paths[:500]:
                QTreeWidgetItem(self.tree, [p])
        # context
        from core import chat_engine
        self.current_context = chat_engine.build_repo_context(owner, repo)
        if self.on_select:
            self.on_select(owner, repo, self.current_context)
        self.view.setPlainText(self.current_context[:1500])

    def on_item(self, item, col):
        path = item.text(0)
        if not self.owner:
            return
        r = GH.get_file(self.owner, self.repo, path)
        if r.ok and isinstance(r.data, dict):
            content = r.data.get("_decoded", "")
            self.view.setPlainText(content[:4000] if content else str(r.data)[:2000])
