import abc
from dataclasses import dataclass

from src.domain.tile import Tile, Point, Cluster, TileType


@dataclass(frozen=True)
class Move:
    cluster: Cluster
    tile_to_move: Tile
    grid_destination: Point
    # TODO impact

    def get_combo_type(self) -> TileType:
        return self.tile_to_move.type

    def calculate_screen_destination(self) -> Point:
        """
        Should work with any size of cluster
        """
        any_pair = []
        for tile in self.cluster.tiles:
            any_pair.append(tile)
            if len(any_pair) == 2:
                break

        tile_centers = any_pair[0].screen_square.find_center(), any_pair[1].screen_square.find_center()
        pair_screen_distance = tile_centers[0].distance_between(tile_centers[1])
        pair_grid_distance = any_pair[0].grid_position.distance_between(any_pair[1].grid_position)

        unitary_distance = int(pair_screen_distance / pair_grid_distance)

        first_tile_center = any_pair[0].screen_square.find_center() - any_pair[0].grid_position * unitary_distance

        return first_tile_center + self.grid_destination * unitary_distance


class TileMover(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self, move: Move):
        raise NotImplementedError()
