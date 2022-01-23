import abc
import logging
from typing import List, Tuple, Set

from src.domain.tile import Tile

logger = logging.getLogger(__name__)


class GameState:
    def __init__(self, tiles: List[Tile] = None) -> None:
        if tiles is None:
            tiles = []
        self.tiles: List[Tile] = sorted(tiles, key=lambda tile: (tile.left, tile.top))

    def __str__(self) -> str:
        return f"Tiles: {[str(tile) for tile in self.tiles]}"

    def find_possible_moves(self) -> Set[Tuple[Tile]]:
        tile_array = [self.tiles[i : i + 7] for i in range(0, len(self.tiles), 7)]
        pairs = set()

        for i in range(0, len(tile_array)):
            for j in range(0, len(tile_array[i]) - 2):

                triple = tile_array[i][j : j + 3]
                different_tile_types = {tile.tile_type for tile in triple}

                if len(different_tile_types) == 2:
                    potential_type = different_tile_types.pop()
                    potential_pair = tuple(tile for tile in triple if tile.tile_type == potential_type)
                    if len(potential_pair) == 2:
                        pairs.add(potential_pair)
                    else:
                        potential_type = different_tile_types.pop()
                        pairs.add(tuple(tile for tile in triple if tile.tile_type == potential_type))

        for i in range(0, len(tile_array) - 2):
            for j in range(0, len(tile_array[i])):

                triple = [row[j] for row in tile_array][i : i + 3]
                different_tile_types = {tile.tile_type for tile in triple}

                if len(different_tile_types) == 2:
                    potential_type = different_tile_types.pop()
                    potential_pair = tuple(tile for tile in triple if tile.tile_type == potential_type)
                    if len(potential_pair) == 2:
                        pairs.add(potential_pair)
                    else:
                        potential_type = different_tile_types.pop()
                        pairs.add(tuple(tile for tile in triple if tile.tile_type == potential_type))

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

        logger.info(f"GameState updated. {{{len(game_state.tiles)} tiles, }}")
        return game_state


class FetchGameState:
    def execute(self) -> GameState:
        global game_state
        return game_state
