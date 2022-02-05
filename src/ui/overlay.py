import logging
from typing import Union

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QGraphicsDropShadowEffect, QCheckBox

from src import properties
from src.domain.tile import TileType
from src.ui.model import GameStateModel

GRID_LEFT = 20
GRID_TOP = 220

logger = logging.getLogger(__name__)

TILE_BORDER_COLORS = {
    TileType.CHEST: QColor(255, 0, 255, 255),
    TileType.KEY: QColor(0, 255, 0, 255),
    TileType.LOGS: QColor(153, 76, 0, 255),
    TileType.ROCKS: QColor(76, 76, 76, 255),
    TileType.SHIELD: QColor(0, 101, 101, 255),
    TileType.SWORD: QColor(0, 101, 204, 255),
    TileType.WAND: QColor(255, 0, 0, 255),
    TileType.STAR: QColor(255, 255, 255, 255),
    TileType.UNKNOWN: QColor(126, 126, 126, 255),
}

TILE_FILL_COLORS = {
    TileType.CHEST: QColor(255, 0, 255, 80),
    TileType.KEY: QColor(0, 255, 0, 80),
    TileType.LOGS: QColor(153, 76, 0, 80),
    TileType.ROCKS: QColor(76, 76, 76, 80),
    TileType.SHIELD: QColor(0, 101, 101, 80),
    TileType.SWORD: QColor(0, 101, 204, 80),
    TileType.WAND: QColor(255, 0, 0, 80),
    TileType.STAR: QColor(255, 255, 255, 80),
    TileType.UNKNOWN: QColor(126, 126, 126, 80),
}

TILE_DIMENSION = 50


class Overlay(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setGeometry(0, 0, 450, 600)

        self.screenshot_logging_cb = QCheckBox("Screenshot logging", self)
        self.screenshot_logging_cb.move(20, 20)
        self.screenshot_logging_cb.setChecked(properties.SCREENSHOT_LOGGING_ENABLED)
        self.screenshot_logging_cb.stateChanged.connect(self.toggle_screenshot_logging)

        self.movement_cb = QCheckBox("Movements", self)
        self.movement_cb.move(20, 40)
        self.movement_cb.setChecked(properties.MOVEMENT_ENABLED)
        self.movement_cb.stateChanged.connect(self.toggle_movement)

        self.auto_run_again_cb = QCheckBox("Auto run gain", self)
        self.auto_run_again_cb.move(20, 60)
        self.auto_run_again_cb.setChecked(properties.AUTO_RUN_AGAIN_ENABLED)
        self.auto_run_again_cb.stateChanged.connect(self.toggle_auto_run_again)

        self.objective_label = QLabel(self)
        self.objective_label.setText("No objective yet")
        self.objective_label.setGeometry(20, 190, 500, 30)
        font = QFont()
        font.setBold(True)
        self.objective_label.setFont(font)
        effect = QGraphicsDropShadowEffect()
        effect.setColor(QColor(255, 255, 255, 255))
        effect.setOffset(0, 0)
        effect.setBlurRadius(20)
        self.objective_label.setGraphicsEffect(effect)

        self.game_state: Union[GameStateModel, None] = None

        self.start = 0

    def toggle_screenshot_logging(self):
        properties.SCREENSHOT_LOGGING_ENABLED = self.screenshot_logging_cb.isChecked()

    def toggle_movement(self):
        properties.MOVEMENT_ENABLED = self.movement_cb.isChecked()

    def toggle_auto_run_again(self):
        properties.AUTO_RUN_AGAIN_ENABLED = self.auto_run_again_cb.isChecked()

    def on_game_state_change(self, game_state: GameStateModel):
        self.game_state = game_state
        self.objective_label.setText(repr(game_state.objective))
        self.update()

    # Called by self.update()
    def paintEvent(self, event):
        if self.game_state is None or not self.game_state.tiles:
            logger.debug("Received no tiles to display :(")
            return

        painter = QPainter(self)
        for tile in self.game_state.tiles:
            if tile.type == TileType.UNKNOWN:
                continue

            rect = [GRID_LEFT + tile.grid_x * TILE_DIMENSION, GRID_TOP + tile.grid_y * TILE_DIMENSION, TILE_DIMENSION, TILE_DIMENSION]
            painter.setPen(QPen(TILE_BORDER_COLORS[tile.type], 1))
            painter.setBrush(QBrush(TILE_FILL_COLORS[tile.type], Qt.BrushStyle.SolidPattern))
            painter.drawRect(*rect)
        painter.end()
