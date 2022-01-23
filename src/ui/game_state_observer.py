import logging
from time import sleep
from typing import Callable

from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from src.domain.game_state import FetchGameState, GameState
from src.domain.tile import Tile

logger = logging.getLogger(__name__)


class HighDPIPositionsSanitizer:
    def __init__(self, display_ratio: float) -> None:
        self.display_ratio = display_ratio

    def sanitize_game_state(self, game_state: GameState) -> GameState:
        return GameState(tiles=[self.sanitize_tile(tile) for tile in game_state.tiles])

    def sanitize_tile(self, tile: Tile) -> Tile:
        return Tile(
            tile.tile_type,
            self.sanitize_pos(tile.left),
            self.sanitize_pos(tile.top),
            self.sanitize_pos(tile.height),
            self.sanitize_pos(tile.width),
        )

    def sanitize_pos(self, pos: int) -> int:
        return int(float(pos) / self.display_ratio)


class GameStateObserverHandler(QObject):
    game_state_changed = pyqtSignal(GameState)

    def __init__(
        self,
        fetch_game_state: FetchGameState,
        position_sanitizer: HighDPIPositionsSanitizer,
    ) -> None:
        super().__init__()
        self.fetch_game_state = fetch_game_state
        self.position_sanitizer = position_sanitizer

    @pyqtSlot()
    def run(self) -> None:
        try:
            logger.info("Starting GameStateObserverHandler now running.")
            while True:
                sleep(0.1)
                # TODO save gameState, only trigger update when it changed (only saving hash could be easier)
                game_state = self.fetch_game_state.execute()

                logger.debug(f"GameState actually is {game_state}.")
                game_state = self.position_sanitizer.sanitize_game_state(game_state)

                self.game_state_changed.emit(game_state)

        except Exception as e:
            logger.exception(e)


class GameStateObserver:
    def __init__(
        self,
        fetch_game_state: FetchGameState,
        game_state_changed_callback: Callable,
        display_ratio: float,
    ) -> None:
        self.handler = GameStateObserverHandler(
            fetch_game_state, HighDPIPositionsSanitizer(display_ratio)
        )

        self.thread = QThread()

        self.handler.game_state_changed.connect(game_state_changed_callback)
        self.handler.moveToThread(self.thread)
        self.thread.started.connect(self.handler.run)

    def start(self) -> None:
        logger.info("Starting GameStateObserver.")
        self.thread.start()
