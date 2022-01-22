import pyautogui
import logging
import sys

from PyQt6.QtWidgets import QApplication

from src.domain.game_state import FetchGameState
from src.ui.bot.game_state_observer import GameStateObserver
from src.ui.overlay.overlay import Overlay

logger = logging.getLogger(__name__)

if __name__ == "__main__":

    logger.info(f"Failsafe points {pyautogui.FAILSAFE_POINTS}")

    app = QApplication(sys.argv)
    displayRatio = app.devicePixelRatio()
    logger.info(f"ratio = {displayRatio}")

    fetch_game_state = FetchGameState()
    main = Overlay()
    game_state_observer = GameStateObserver(
        fetch_game_state, main.on_game_state_change, displayRatio
    )

    game_state_observer.start()
    main.showMaximized()
    app.exec()
