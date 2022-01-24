import logging
from typing import Union

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QPushButton, QWidget

from src.domain.tile import TileType
from src.ui.model import GameStateModel

logger = logging.getLogger(__name__)

TILE_COLORS = {
    TileType.CHEST: Qt.GlobalColor.magenta,
    TileType.KEY: Qt.GlobalColor.green,
    TileType.LOGS: Qt.GlobalColor.darkYellow,
    TileType.ROCKS: Qt.GlobalColor.darkBlue,
    TileType.SHIELD: Qt.GlobalColor.darkGreen,
    TileType.SWORD: Qt.GlobalColor.blue,
    TileType.WAND: Qt.GlobalColor.red,
}


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
        # painter.setBrush(QBrush(QColor(0, 255, 0, 80), Qt.BrushStyle.SolidPattern))
        for tile in self.game_state.tiles:
            rect = [tile.left - 2, tile.top - 2, tile.height + 5, tile.width + 5]
            painter.setPen(QPen(TILE_COLORS[tile.type], 1))
            painter.drawRect(*rect)
        painter.end()
