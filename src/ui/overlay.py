import logging
from typing import Union

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from PyQt6.QtWidgets import QPushButton, QWidget

from src.domain.tile import TileType
from src.ui.model import GameStateModel

logger = logging.getLogger(__name__)

TILE_BORDER_COLORS = {
    TileType.CHEST: QColor(255, 0, 255, 255),
    TileType.KEY: QColor(0, 255, 0, 255),
    TileType.LOGS: QColor(153, 76, 0, 255),
    TileType.ROCKS: QColor(76, 76, 76, 255),
    TileType.SHIELD: QColor(0, 101, 101, 255),
    TileType.SWORD: QColor(0, 101, 204, 255),
    TileType.WAND: QColor(255, 0, 0, 255),
}

TILE_FILL_COLORS = {
    TileType.CHEST: QColor(255, 0, 255, 80),
    TileType.KEY: QColor(0, 255, 0, 80),
    TileType.LOGS: QColor(153, 76, 0, 80),
    TileType.ROCKS: QColor(76, 76, 76, 80),
    TileType.SHIELD: QColor(0, 101, 101, 80),
    TileType.SWORD: QColor(0, 101, 204, 80),
    TileType.WAND: QColor(255, 0, 0, 80),
}

GRID_TOP_OFFSET = -700


class Overlay(QWidget):
    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        self.toggle_btn = QPushButton("Exit", self)
        self.toggle_btn.setGeometry(1700, 150, 100, 30)
        self.toggle_btn.clicked.connect(self.close)

        self.intangible_btn = QPushButton("Intangible", self)
        self.intangible_btn.setGeometry(1820, 150, 100, 30)
        self.intangible_btn.clicked.connect(self.on_intangible)

        self.game_state: Union[GameStateModel, None] = None

        self.start = 0

    def on_intangible(self):
        logger.info("Overlay set to intangible mode.")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def on_game_state_change(self, game_state: GameStateModel):
        self.game_state = game_state
        self.update()

    # Called by self.update()
    def paintEvent(self, event):
        if self.game_state is None:
            return

        painter = QPainter(self)
        for tile in self.game_state.tiles:
            rect = [tile.left, tile.top + GRID_TOP_OFFSET, tile.height, tile.width]
            painter.setPen(QPen(TILE_BORDER_COLORS[tile.type], 1))
            painter.setBrush(QBrush(TILE_FILL_COLORS[tile.type], Qt.BrushStyle.SolidPattern))
            painter.drawRect(*rect)
        painter.end()
