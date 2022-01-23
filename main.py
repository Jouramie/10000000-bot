import logging
import sys

from PyQt6.QtWidgets import QApplication

from src.domain.game_state import FetchGameState
from src.infra.autogui.game_state_detector_impl import AutoGuiGameStateDetector
from src.ui.game_state_observer import GameStateObserver
from src.ui.overlay import Overlay

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        display_ratio = app.devicePixelRatio()

        logger.debug(f"Display ration = {display_ratio}")

        fetch_game_state = FetchGameState(AutoGuiGameStateDetector())
        main = Overlay()
        game_state_observer = GameStateObserver(
            fetch_game_state, main.on_game_state_change, display_ratio
        )

        game_state_observer.start()
        main.showMaximized()
        app.exec()
    except Exception as e:
        logger.exception(e)
