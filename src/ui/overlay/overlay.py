import numpy as np

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QPushButton, QWidget

from src.domain.game_state import GameState


class Overlay(QWidget):
    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )

        self.toggle_btn = QPushButton("Exit", self)
        self.toggle_btn.setGeometry(1700, 150, 100, 30)
        self.toggle_btn.clicked.connect(self.close)

        self.draw_btn = QPushButton("Draw rectangle", self)
        self.draw_btn.setGeometry(1820, 150, 100, 30)
        self.draw_btn.clicked.connect(self.draw_rectangle)

        self.draw_btn = QPushButton("Remove rectangle", self)
        self.draw_btn.setGeometry(1940, 150, 100, 30)
        self.draw_btn.clicked.connect(self.remove_rectangle)

        self.enflatedTiles = []

        self.start = 0

    def remove_rectangle(self):
        self.enflatedTiles.pop()
        self.update()

    def draw_rectangle(self):
        rect = [
            np.random.randint(1920 - 150),
            np.random.randint(1080 - 100),
            np.random.randint(150),
            np.random.randint(100),
        ]
        self.enflatedTiles.append(rect)
        self.update()

    def on_game_state_change(self, game_state: GameState):
        self.enflatedTiles = [
            [tile[0] - 2, tile[1] - 2, tile[2] + 5, tile[3] + 5]
            for tile in game_state.tiles
        ]
        self.update()

    # Called by self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.green, 1))
        # painter.setBrush(QBrush(QColor(0, 255, 0, 80), Qt.BrushStyle.SolidPattern))
        for rect in self.enflatedTiles:
            painter.drawRect(*rect)
        painter.end()
