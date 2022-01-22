import logging
from time import sleep
from typing import Callable, List

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from cv2 import displayOverlay

from src.domain.game_state import FetchGameState, GameState


logger = logging.getLogger(__name__)


class HighDPIPositionsSanitizer:
    def __init__(self, display_ratio: int) -> None:
        self.display_ratio = display_ratio

    def sanitize_inplace(self, gameState: GameState) -> None:
        gameState.tiles = [self.sanitize_tile(tile) for tile in gameState.tiles]

    def sanitize_tile(self, tile: List[int]) -> List[int]:
        return [int(pos / self.display_ratio) for pos in tile]


class GameStateObserverHandler(QObject):
    game_state_changed = pyqtSignal(GameState)

    def __init__(
        self,
        fetchGameState: FetchGameState,
        positionSanitizer: HighDPIPositionsSanitizer,
    ) -> None:
        super().__init__()
        self.fetch_game_state = fetchGameState
        self.position_sanitizer = positionSanitizer

    @pyqtSlot()
    def run(self) -> None:
        while True:
            sleep(0.1)
            # TODO save gameState, only trigger update when it changed (only saving hash could be easier)
            game_state = self.fetch_game_state.execute()
            logger.info(f"GameState actually is {game_state}.")
            self.position_sanitizer.sanitize_inplace(game_state)
            self.game_state_changed.emit(game_state)


class GameStateObserver:
    def __init__(
        self,
        fetchGameState: FetchGameState,
        gameStateChangedCallback: Callable,
        displayRatio: float,
    ) -> None:
        self.handler = GameStateObserverHandler(
            fetchGameState, HighDPIPositionsSanitizer(displayRatio)
        )

        self.thread = QThread()

        self.handler.game_state_changed.connect(gameStateChangedCallback)
        self.handler.moveToThread(self.thread)
        self.thread.started.connect(self.handler.run)

    def start(self) -> None:
        self.thread.start()
