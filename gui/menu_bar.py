from __future__ import annotations
from typing import TYPE_CHECKING
from PyQt6.QtWidgets import QMenuBar, QFileDialog
from PyQt6.QtGui import (
    QShortcut,
    QKeySequence,
    QAction,
)
from PyQt6.QtCore import QPoint

from core.game import Game

if TYPE_CHECKING:
    from main import Window


class MenuBar(QMenuBar):
    def __init__(self, app: Window):
        super().__init__()
        self.app = app

        self.quicksave_count: int = 1

        file_menu = self.addMenu("File")

        quicksave_action = QAction("Quicksave", self)
        quicksave_action.triggered.connect(self._quicksave_game)
        self.addAction(quicksave_action)  # Adds it directly to the menu bar

        if file_menu:
            new_action = QAction("New", self)
            new_action.triggered.connect(self._new_game)
            file_menu.addAction(new_action)

            load_action = QAction("Load", self)
            load_action.triggered.connect(self._load_game)
            file_menu.addAction(load_action)

            save_action = QAction("Save", self)
            save_action.triggered.connect(self._save_game)
            file_menu.addAction(save_action)

    def _new_game(self) -> None:
        # TODO: support for other games
        self.app.game.__init__(self.app.game.year)
        self.app.reset_state()

    def _load_game(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Save File", "", "JSON Files (*.json)"
        )
        if path:
            year = Game.load_year(path)
            self.app.game.__init__(year)
            self.app.game.load(path)
            self.app.reset_state()

    def _save_game(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Game", "save.json", "JSON Files (*.json)"
        )
        if path:
            self.app.game.save(path)

    # ! This is a quick hack for debug purposes, needs to be reworked
    # ! The idea is to quicksave mid irl game with data on which railway scored how much on what turn
    # ! to help compare results between algorithms later.
    # TODO: Implement it properly, maybe tracking round number and phase
    # TODO: At the very least remove quicksave count and instead check for last file to extract number, resetting on phase change
    def _quicksave_game(self) -> None:
        if not self.app.selected_railway or not self.app.canvas.solution:
            self.app.logbox.logger.append("Quicksave failed due to lack of a working route to save.")
            return

        meta=f"{self.app.game.phase.id}-{self.quicksave_count}-{self.app.selected_railway.id}-{self.app.canvas.solution.value}"
        path = f"saves/quicksaves/{meta}.json"
        self.app.game.save(path)
        self.quicksave_count += 1
        self.app.logbox.logger.append(f"Quicksave {meta} saved successfully.")