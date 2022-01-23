import pyautogui
import logging
import sys

from PyQt6.QtWidgets import QApplication

from src.domain.game_state import FetchGameState
from src.ui.bot.game_state_observer import GameStateObserver
from src.ui.overlay.overlay import Overlay

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    displayRatio = app.devicePixelRatio()

    fetch_game_state = FetchGameState()
    main = Overlay()
    game_state_observer = GameStateObserver(
        fetch_game_state, main.on_game_state_change, displayRatio
    )

    game_state_observer.start()
    main.showMaximized()
    app.exec()
