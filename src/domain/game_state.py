import abc
import logging

logger = logging.getLogger(__name__)


class GameState:
    def __init__(self, tiles=None) -> None:
        if tiles is None:
            tiles = []
        self.tiles = tiles

    def __str__(self) -> str:
        return f"Tiles: {[str(tile) for tile in self.tiles]}"


class GameStateDetector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def detect_game_state(self) -> GameState:
        raise NotImplementedError


game_state = GameState()


class UpdateGameState:
    def __init__(self, detector: GameStateDetector) -> None:
        self.detector = detector

    def execute(self) -> GameState:
        global game_state
        game_state = self.detector.detect_game_state()

        logger.info(f"GameState updated. {{{len(game_state.tiles)} tiles, }}")
        return game_state


class FetchGameState:
    def execute(self) -> GameState:
        global game_state
        return game_state
