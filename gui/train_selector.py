from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import (
    QWidget,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
)
from PyQt6.QtCore import Qt, QSize

from core.game import Game
from core.tile import Tile
from core.train import Train
from gui.tile_preview import TilePreview
from tools.exceptions import RuleError

if TYPE_CHECKING:
    from main import Window


class TrainSelector(QWidget):
    game: Game
    app: Window

    def __init__(self, app: Window, game: Game) -> None:
        super().__init__()
        self.app = app
        self.game = game

        layout = QVBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        self.label = QLabel("Buy a Train:")
        self.rows = [TrainRow(app, game, train) for train in game.database.trains]

        layout.addWidget(self.label)
        for row in self.rows:
            layout.addWidget(row)


class TrainRow(QWidget):
    game: Game
    app: Window

    def __init__(self, app: Window, game: Game, train_id: str) -> None:
        super().__init__()
        self.app = app
        self.game = game

        self.train_id = train_id

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.label = QLabel(f"{self.train_id}-Train (Available: {self.game.bank.trains[self.train_id]})")
        self.button = QPushButton("Buy")
        self.button.setEnabled(False)
        self.button.clicked.connect(self._on_pressed)

        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def _on_pressed(self):
        if self.app.selected_railway:
            try:
                self.game.give_train(Train.from_id(self.train_id), self.app.selected_railway)
            except RuleError as e:
                self.app.logbox.logger.append(str(e))
            else:
                self.label.setText(f"{self.train_id}-Train (Available: {self.game.bank.trains[self.train_id]})")
                self.app.update_routes()