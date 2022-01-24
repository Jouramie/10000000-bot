import abc
import logging
from dataclasses import dataclass
from typing import Set

from src.domain.move import Move
from src.domain.tile import Grid, Point

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class GameState:
    grid: Grid = Grid()

    def find_possible_moves(self) -> Set[Move]:
        pairs = self.grid.find_clusters()

        movements = set()

        for pair in pairs:

            if pair[0].grid_position.x == pair[1].grid_position.x:
                if pair[0].grid_position.y + 2 == pair[1].grid_position.y:
                    missing_row_nos = [pair[0].grid_position.y + 1]
                elif pair[0].grid_position.y == 0:
                    missing_row_nos = [2]
                else:
                    missing_row_nos = [pair[0].grid_position.y - 1, pair[0].grid_position.y + 2]
                # FIXME this will crash of pair in last on column (will try to complete with row 9)

                rows = {missing_row_no: self.grid.get_row(missing_row_no) for missing_row_no in missing_row_nos}

                matching_tiles = {(row_no, tile) for row_no, row in rows.items() for tile in row if tile.type == pair[0].type}
                for row_no, matching_tile in matching_tiles:
                    movements.add(Move(pair, matching_tile, Point(pair[0].grid_position.x, row_no)))

        logger.debug(f"Movements found {movements}")

        return movements


class GameStateDetector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def detect_game_state(self) -> GameState:
        raise NotImplementedError()


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
