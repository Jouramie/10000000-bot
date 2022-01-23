import logging
import sys
from threading import Thread

from PyQt6.QtWidgets import QApplication

from src.bot import Bot
from src.domain.game_state import FetchGameState, UpdateGameState
from src.infra.autogui.game_state_detector_impl import AutoGuiGameStateDetector
from src.ui.game_state_observer import GameStateObserver
from src.ui.overlay import Overlay

logger = logging.getLogger(__name__)


class Context:
    def __init__(self) -> None:
        logger.info("Initializing context.")

        self.app = QApplication(sys.argv)
        display_ratio = self.app.devicePixelRatio()
        logger.debug(f"Display ration = {display_ratio}")

        # Domain
        fetch_game_state = FetchGameState()
        update_game_state = UpdateGameState(AutoGuiGameStateDetector())

        # Bot
        bot = Bot(update_game_state.execute)
        self.bot_thread = Thread(target=bot.main_loop)

        # UI
        self.overlay = Overlay()
        self.game_state_observer = GameStateObserver(
            fetch_game_state.execute, self.overlay.on_game_state_change, display_ratio
        )

    def start(self):
        logger.info("Starting context.")

        # Bot
        self.bot_thread.start()

        # Overlay
        self.game_state_observer.start()
        self.overlay.showMaximized()

        self.app.exec()
