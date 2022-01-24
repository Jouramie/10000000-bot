import abc
from dataclasses import dataclass
from typing import Tuple

from src.domain.tile import Tile, Point


@dataclass(frozen=True)
class Move:
    pair: Tuple[Tile]
    tile_to_move: Tile
    grid_destination: Point
    # TODO impact

    def get_combo_type(self):
        return self.tile_to_move.type

    def calculate_screen_destination(self):
        tile_centers = self.pair[0].screen_square.find_center(), self.pair[1].screen_square.find_center()
        pair_screen_distance = tile_centers[0].distance_between(tile_centers[1])
        pair_grid_distance = self.pair[0].grid_position.distance_between(self.pair[1].grid_position)

        unitary_distance = int(pair_screen_distance / pair_grid_distance)

        first_tile_center = self.pair[0].screen_square.find_center() - self.pair[0].grid_position * unitary_distance

        return first_tile_center + self.grid_destination * unitary_distance


class TileMover(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self, move: Move):
        raise NotImplementedError()
