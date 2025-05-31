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
    app: Window

    def __init__(self, app: Window) -> None:
        super().__init__()
        self.app = app

        layout = QVBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        self.label = QLabel("Buy a Train:")
        self.rows = [TrainRow(app, train) for train in self.app.game.database.trains]

        layout.addWidget(self.label)
        for row in self.rows:
            layout.addWidget(row)

    def update_train_count(self):
        for row in self.rows:
            row.label.setText(
                f"{row.train_id}-Train (Available: {self.app.game.bank.trains[row.train_id]})"
            )


class TrainRow(QWidget):
    app: Window

    def __init__(self, app: Window, train_id: str) -> None:
        super().__init__()
        self.app = app

        self.train_id = train_id

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.label = QLabel(
            f"{self.train_id}-Train (Available: {self.app.game.bank.trains[self.train_id]})"
        )
        self.button = QPushButton("Buy")
        self.button.setEnabled(False)
        self.button.clicked.connect(self._on_pressed)

        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def _on_pressed(self):
        if self.app.selected_railway:
            try:
                self.app.game.give_train(
                    Train.from_id(self.train_id), self.app.selected_railway
                )
            except RuleError as e:
                self.app.logbox.logger.append(str(e))
            else:
                self.app.train_selector.update_train_count()
                self.app.update_routes()
