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

from core.enums.settlement_location import SettlementLocation
from core.game import Game
from core.tile import Tile
from gui.tile_preview import TilePreview
from tools.exceptions import RuleError

if TYPE_CHECKING:
    from main import Window


class TileSelector(QWidget):
    app: Window

    tile_rotation: int = 0

    def __init__(self, app: Window) -> None:
        super().__init__()
        self.app = app

        layout = QVBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.label = QLabel("Select a Tile:")

        self.tile_list = QListWidget()
        self.tile_list.setDragEnabled(False)
        self.tile_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.tile_list.setMovement(QListView.Movement.Static)
        self.tile_list.setIconSize(QSize(100, 100))
        self.tile_list.setViewMode(QListView.ViewMode.IconMode)
        self.tile_list.itemClicked.connect(self._on_tile_selected)

        rotate_layout = QHBoxLayout()

        self.rotate_left_button = QPushButton("⟲ Rotate Left")
        self.rotate_right_button = QPushButton("⟳ Rotate Right")
        self.submit_button = QPushButton("Place Tile")
        self.enable_tile_buttons(False)

        self.rotate_left_button.clicked.connect(self._on_rotate_left)
        self.rotate_right_button.clicked.connect(self._on_rotate_right)
        self.submit_button.clicked.connect(self._on_submit_tile)

        self.station_button = QPushButton("Place Station")
        self.station_button.setEnabled(False)
        self.station_button.clicked.connect(self._on_place_station)

        layout.addWidget(self.label)
        layout.addWidget(self.tile_list)
        layout.addLayout(rotate_layout)
        rotate_layout.addWidget(self.rotate_left_button)
        rotate_layout.addWidget(self.rotate_right_button)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.station_button)

    def populate_tile_list(self, tile: Tile | None) -> None:
        self.reset_tile_list()
        if tile:
            for upgrade in tile.upgrades:
                item = TilePreview(self.app.game, Tile.from_id(upgrade))
                item.setData(Qt.ItemDataRole.UserRole, upgrade)
                self.tile_list.addItem(item)

    def reset_tile_list(self):
        self.tile_list.clear()
        self.enable_tile_buttons(False)

    def _on_tile_selected(self, item: QListWidgetItem) -> None:
        self.app.selected_tile = self.tile_list.selectedItems()[0].tile  # type: ignore

    def _on_submit_tile(self) -> None:
        if self.app.selected_hex and self.app.selected_tile:
            try:
                self.app.game.place_tile(self.app.selected_hex, self.app.selected_tile)
            except RuleError as e:
                self.app.logbox.logger.append(str(e))
            else:
                self.app.selected_hex = None
                self.app.selected_tile = None
                self.app.update_routes()

    def _on_rotate_left(self) -> None:
        self._update_tile_rotation(-1)

    def _on_rotate_right(self) -> None:
        self._update_tile_rotation(1)

    def _on_place_station(self) -> None:
        if self.app.selected_hex and self.app.selected_railway:
            try:
                # TODO: Figure it out at some point :(
                #! Oh god what if there's two stations
                self.app.game.place_station(
                    self.app.selected_hex,
                    self.app.selected_railway,
                    SettlementLocation.C,
                )
            except RuleError as e:
                self.app.logbox.logger.append(str(e))
            else:
                self.app.update_routes()

    def _update_tile_rotation(self, r: int) -> None:
        for i in range(self.tile_list.count()):
            item: TilePreview = self.tile_list.item(i)  # type: ignore
            item.tile = item.tile.rotated(r)
            item.updateIcon()

        self.app.selected_tile = self.tile_list.selectedItems()[0].tile  # type: ignore

    def enable_tile_buttons(self, enabled: bool) -> None:
        self.submit_button.setEnabled(enabled)
        self.rotate_left_button.setEnabled(enabled)
        self.rotate_right_button.setEnabled(enabled)
