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
from core.railway import Railway

if TYPE_CHECKING:
    from main import Window


class RailwaySelector(QWidget):
    app: Window

    def __init__(self, app: Window) -> None:
        super().__init__()
        self.app = app

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.label = QLabel("Select a Railway:")

        self.railway_list = QListWidget()
        self.railway_list.setDragEnabled(False)
        self.railway_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.railway_list.setMovement(QListView.Movement.Static)
        self.railway_list.itemClicked.connect(self._on_railway_selected)
        self._populate_railway_list()

        layout.addWidget(self.label)
        layout.addWidget(self.railway_list)

    def _on_railway_selected(self, item: QListWidgetItem) -> None:
        railway: Railway = item.data(Qt.ItemDataRole.UserRole)
        self.app.selected_railway = railway

    def _populate_railway_list(self):
        for railway in self.app.game.railways.values():
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, railway)
            item.setText(f"{railway.name} ({railway.id})")
            self.railway_list.addItem(item)
