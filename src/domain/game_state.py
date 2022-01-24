import abc
import logging
from dataclasses import dataclass
from typing import Set

from src.domain.movement import Movement
from src.domain.tile import Grid, GridPosition

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class GameState:
    grid: Grid = Grid()

    def find_possible_moves(self) -> Set[Movement]:
        pairs = self.grid.find_clusters()

        movements = set()

        for pair in pairs:

            if pair[0].grid_position.x == pair[1].grid_position.x:
                if pair[0].grid_position.y + 2 == pair[1].grid_position.y:
                    missing_row_no = pair[0].grid_position.y + 1
                elif pair[0].grid_position.y == 0:
                    missing_row_no = 3
                else:
                    missing_row_no = pair[0].grid_position.y + 2

                row = self.grid.get_row(missing_row_no)

                matching_tiles = [tile for tile in row if tile.type == pair[0].type]
                for matching_tile in matching_tiles:
                    movements.add(Movement(pair, matching_tile, GridPosition(pair[0].grid_position.x, missing_row_no)))

        logger.debug(f"Movements found {movements}")

        return movements


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
