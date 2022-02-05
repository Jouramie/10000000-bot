import logging
from time import sleep
from typing import Callable

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from src.bot import fetch_game_state
from src.ui.model import GameStateModel, to_model

logger = logging.getLogger(__name__)


# FIXME probably don't need another thread for this. Observer could be in the bot.
class GameStateObserverHandler(QObject):
    game_state_changed = pyqtSignal(GameStateModel)

    def __init__(self) -> None:
        super().__init__()

    @pyqtSlot()
    def run(self) -> None:
        try:
            logger.info("Starting GameStateObserverHandler now running.")
            while True:
                # TODO save gameState, only trigger update when it changed (only saving hash could be easier)
                logger.debug("Fetching GameState.")
                self.game_state_changed.emit(to_model(fetch_game_state()))

                sleep(0.1)
        except Exception as e:
            logger.exception(e)
        finally:
            logger.info("GameStateObserverHandler is stopped.")


class GameStateObserver:
    def __init__(self, game_state_changed_callback: Callable[[GameStateModel], None]) -> None:
        self.handler = GameStateObserverHandler()

        self.thread = QThread()

        self.handler.game_state_changed.connect(game_state_changed_callback)
        self.handler.moveToThread(self.thread)
        self.thread.started.connect(self.handler.run)

    def start(self) -> None:
        logger.info("Starting GameStateObserver.")
        self.thread.start()

    def stop(self) -> None:
        logger.info("Stopping GameStateObserver.")
        self.thread.stop()
