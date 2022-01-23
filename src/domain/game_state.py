import abc
import logging
from dataclasses import dataclass
from typing import Tuple, Set

from src.domain.tile import Tile, Grid

logger = logging.getLogger(__name__)


@dataclass
class GameState:
    grid: Grid = Grid()

    def find_possible_moves(self) -> Set[Tuple[Tile]]:
        pairs = self.grid.find_clusters()

        return pairs


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

        logger.info(f"GameState updated. {{{len(game_state.grid)} tiles, }}")
        return game_state


class FetchGameState:
    def execute(self) -> GameState:
        global game_state
        return game_state
