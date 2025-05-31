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

        file_menu = self.addMenu("File")

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
