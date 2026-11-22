# -*- coding: utf-8 -*-
"""Zero · Sesión de chat (repo-aware)."""
from __future__ import annotations
from PySide6.QtCore import QObject, Signal


class ChatSession(QObject):
    message_added = Signal(str, str)
    busy_changed = Signal(bool)
    reset = Signal()

    def __init__(self, pet_key="zero", pet_name="Zero"):
        super().__init__()
        self.pet_key = pet_key
        self.pet_name = pet_name
        self.messages = []
        self.busy = False
        self.wake_active = False
        self.repo_ctx = ""
        self.owner = ""
        self.repo = ""

    def set_pet(self, key, name):
        self.pet_key = key
        self.pet_name = name

    def set_repo(self, owner, repo, ctx):
        self.owner = owner
        self.repo = repo
        self.repo_ctx = ctx

    def greet(self):
        self.message_added.emit("pet", f"Hola, soy {self.pet_name}. Carga un repo en 'Repos' y pregúntame.")

    def send(self, text):
        if not text.strip():
            return
        self.messages.append({"role": "user", "content": text})
        self.message_added.emit("user", text)
        self.busy_changed.emit(True)
        try:
            if not self.repo_ctx:
                ans = "Aún no hay repo cargado. Abre la ventana (clic derecho → Repos) y carga un repo."
            else:
                from core import agent_graph
                ans = agent_graph.run(text, repo_ctx=self.repo_ctx, owner=self.owner, repo=self.repo)
            self.messages.append({"role": "assistant", "content": ans})
            self.message_added.emit("pet", ans)
        except Exception as e:
            self.message_added.emit("pet", f"Error: {e}")
        finally:
            self.busy_changed.emit(False)

    def start_wake(self):
        return False

    def stop_wake(self):
        pass
