import logging
import sys
from threading import Thread

from PyQt6.QtWidgets import QApplication

from src.bot import main_loop
from src.ui.game_state_observer import GameStateObserver
from src.ui.overlay import Overlay

logger = logging.getLogger(__name__)


class Context:
    def __init__(self) -> None:
        logger.info("Initializing context.")

        self.app = QApplication(sys.argv)

        # Bot
        self.bot_thread = Thread(target=main_loop)

        # UI
        self.overlay = Overlay()
        self.game_state_observer = GameStateObserver(self.overlay.on_game_state_change)

    def start(self):
        logger.info("Starting context.")

        # Bot
        self.bot_thread.start()

        # Overlay
        self.game_state_observer.start()
        self.overlay.showMaximized()

        self.app.exec()
