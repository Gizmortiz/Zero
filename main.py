# -*- coding: utf-8 -*-
"""Zero · Punto de entrada."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtWidgets import QApplication

from interfaces.master_window import MasterWindow
from interfaces.chat_window import ChatWindow
from interfaces.repo_browser import RepoBrowser
from interfaces.settings_window import SettingsWindow
from interfaces.memory_window import MemoryWindow
from interfaces.desktop_pet import DesktopPet
from core.chat_session import ChatSession


def main():
    pet_key = sys.argv[1] if len(sys.argv) > 1 else "zero"
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setQuitOnLastWindowClosed(False)

    session = ChatSession(pet_key, pet_key.capitalize())

    master = MasterWindow()
    chat = ChatWindow()
    def on_repo(owner, repo, ctx):
        chat.set_repo(owner, repo, ctx)
        session.set_repo(owner, repo, ctx)
    repos = RepoBrowser(on_select=on_repo)
    settings = SettingsWindow()
    memory = MemoryWindow()
    master.add_page(chat)
    master.add_page(repos)
    master.add_page(memory)
    master.add_page(settings)

    pet = DesktopPet(session, pet_key)
    pet.chat_requested.connect(lambda: (master.show(), master.raise_(), master.activateWindow(), master.stack.setCurrentIndex(0)))
    pet.repos_requested.connect(lambda: (master.show(), master.raise_(), master.activateWindow(), master.stack.setCurrentIndex(1)))
    pet.memory_requested.connect(lambda: (master.show(), master.raise_(), master.activateWindow(), master.stack.setCurrentIndex(2)))
    pet.settings_requested.connect(lambda: (master.show(), master.raise_(), master.activateWindow(), master.stack.setCurrentIndex(3)))
    pet.quit_requested.connect(app.quit)

    pet.show()
    master.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
