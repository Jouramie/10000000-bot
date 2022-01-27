import abc
import logging
from dataclasses import dataclass
from typing import Set

from src.domain.move import Move
from src.domain.objective import NoObjective, Objective
from src.domain.tile import Grid, Point, InconsistentGrid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class GameState:
    grid: Grid = InconsistentGrid()
    objective: Objective = NoObjective()

    def find_possible_moves(self) -> Set[Move]:
        pairs = self.grid.find_clusters()

        logger.debug(f"Grid: {str(self.grid)}")
        if not pairs:
            logger.warning("Found no clusters.")
            return set()

        movements = set()

        for cluster in pairs:

            completing_row_indices = cluster.find_completing_row_indices()
            if completing_row_indices:
                x = cluster.get_completed_line_index()
                completing_cluster_rows = {missing_row_no: self.grid.get_row(missing_row_no) for missing_row_no in completing_row_indices}

                matching_tiles = {(row_no, tile) for row_no, row in completing_cluster_rows.items() for tile in row if tile.type == cluster.type}
                for y, matching_tile in matching_tiles:
                    movements.add(Move(cluster, matching_tile, Point(x, y)))
            else:
                y = cluster.get_completed_line_index()
                completing_column_indices = cluster.find_completing_column_indices()
                completing_cluster_columns = {missing_column_no: self.grid.get_column(missing_column_no) for missing_column_no in completing_column_indices}

                matching_tiles = {(row_no, tile) for row_no, row in completing_cluster_columns.items() for tile in row if tile.type == cluster.type}
                for x, matching_tile in matching_tiles:
                    movements.add(Move(cluster, matching_tile, Point(x, y)))

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

        logger.info(f"GameState updated. {{{len(game_state.grid)} tiles. Objective: {game_state.objective.type}.")
        return game_state


class FetchGameState:
    def execute(self) -> GameState:
        global game_state
        return game_state
