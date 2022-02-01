from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Set, Tuple, Sized, Iterable, Dict

from frozendict import frozendict

from src.domain.objective import TileMove
from src.domain.screen import Point
from src.domain.tile import TileType, Tile, Cluster

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass(frozen=True)
class Grid(Sized, Iterable[Tile]):
    """
    8x7 56 tiles
    self.size.x=8
    self.size.y=7
    """

    tiles: List[Tile]
    size: Point

    def __iter__(self):
        return iter(self.tiles)

    def __len__(self) -> int:
        return len(self.tiles)

    def __str__(self):
        grid = ""
        for row in self.get_rows():
            grid += str([str(tile) for tile in row]) + "\n"
        return grid[:-1]

    def get(self, x, y) -> Tile:
        for tile in self.tiles:
            if tile.grid_position.x == x and tile.grid_position.y == y:
                return tile

    def get_row(self, y) -> List[Tile]:
        return [tile for tile in self.tiles if tile.grid_position.y == y]

    def get_column(self, x) -> List[Tile]:
        return [tile for tile in self.tiles if tile.grid_position.x == x]

    def set_row(self, y, line: List[Tile]):
        tiles = self.tiles.copy()
        tiles[y * self.size.x : (y + 1) * self.size.x] = line
        return Grid(tiles, self.size)

    def set_column(self, x, line: List[Tile]):
        tiles = self.tiles.copy()
        tiles[x :: self.size.x] = line
        return Grid(tiles, self.size)

    def get_rows(self) -> List[List[Tile]]:
        return [self.get_row(y) for y in range(0, self.size.y)]

    def get_columns(self) -> List[List[Tile]]:
        return [self.get_column(x) for x in range(0, self.size.x)]

    def get_lines(self) -> List[List[Tile]]:
        return self.get_columns() + self.get_rows()

    def get_triples(self) -> List[List[Tile]]:
        return [line[i : i + 3] for line in self.get_lines() for i in range(0, len(line) - 2)]

    def find_clusters(self) -> Set[Cluster]:
        pairs = {Grid._find_pair_in_triple(triple) for triple in self.get_triples()}
        return {pair for pair in pairs if pair is not None}

    @staticmethod
    def _find_pair_in_triple(triple: List[Tile]) -> Cluster | None:
        different_types = {tile.type for tile in triple if tile.type != TileType.UNKNOWN and tile.type != TileType.STAR}

        for potential_type in different_types:
            potential_cluster = frozenset(tile for tile in triple if tile.type == potential_type or tile.type == TileType.STAR)
            if len(potential_cluster) == 2:
                return Cluster(potential_type, potential_cluster)

    def find_possible_moves(self) -> Set[TileMove]:
        pairs = self.find_clusters()

        if not pairs:
            return set()

        movements = set()

        for cluster in pairs:

            completing_row_indices = cluster.find_completing_row_indices()
            if completing_row_indices:
                x = cluster.get_completed_line_index()
                completing_cluster_rows = {missing_row_index: self.get_row(missing_row_index) for missing_row_index in completing_row_indices}

                matching_tiles = {(row_index, tile) for row_index, row in completing_cluster_rows.items() for tile in row if tile.type == cluster.type}
                for y, matching_tile in matching_tiles:
                    destination = Point(x, y)
                    movements.add(TileMove(self.simulate_line_shift(matching_tile.grid_position, destination)[0], cluster, matching_tile, destination))
            else:
                y = cluster.get_completed_line_index()
                completing_column_indices = cluster.find_completing_column_indices()
                completing_cluster_columns = {missing_column_no: self.get_column(missing_column_no) for missing_column_no in completing_column_indices}

                matching_tiles = {(row_no, tile) for row_no, row in completing_cluster_columns.items() for tile in row if tile.type == cluster.type}
                for x, matching_tile in matching_tiles:
                    destination = Point(x, y)
                    movements.add(TileMove(self.simulate_line_shift(matching_tile.grid_position, destination)[0], cluster, matching_tile, destination))

        return movements

    def simulate_line_shift(self, shift_start: Point, shift_destination: Point) -> Tuple[Dict[TileType, int], Grid]:
        """
        1. Shift
        2. Remove combining tiles
        3. Gravity
        4. Loop 2-3
        """
        simulated_grid = self.shift(shift_start, shift_destination)

        combining_tiles = set()
        new_combining_tiles, simulated_grid = simulated_grid.remove_completed_combos()
        while new_combining_tiles:
            combining_tiles |= new_combining_tiles
            simulated_grid = simulated_grid.gravity()
            new_combining_tiles, simulated_grid = simulated_grid.remove_completed_combos()

        impact = dict()
        for tile in combining_tiles:
            if tile.type not in impact:
                impact[tile.type] = 0

            impact[tile.type] += 1

        return frozendict(impact), simulated_grid.fill_with_unknown()

    def shift(self, shift_start: Point, shift_destination: Point):
        assert shift_start.x == shift_destination.x or shift_start.y == shift_destination.y

        shift = shift_destination - shift_start

        if shift.y == 0:
            line = self.get_row(shift_start.y)
            distance = shift.x
            new_line = [Tile(tile.type, Point(x, shift_start.y)) for x, tile in enumerate(line[-distance:] + line[:-distance])]
            return self.set_row(shift_start.y, new_line)
        else:
            line = self.get_column(shift_start.x)
            distance = shift.y
            new_line = [Tile(tile.type, Point(shift_start.x, y)) for y, tile in enumerate(line[-distance:] + line[:-distance])]
            return self.set_column(shift_start.x, new_line)

    def remove_completed_combos(self):
        combining_tiles = set()
        for triple in self.get_triples():
            different_types = {tile.type for tile in triple if tile.type != TileType.STAR}
            if len(different_types) == 1 and TileType.UNKNOWN not in different_types:
                combining_tiles |= set(triple)

        remaining_tiles = [tile for tile in self.tiles if tile not in combining_tiles]

        return combining_tiles, InconsistentGrid(remaining_tiles, self.size)

    def gravity(self):
        fallen_tiles = []
        for column in self.get_columns():
            missing_tiles = self.size.y - len(column)

            if missing_tiles == 0:
                fallen_tiles += column
                continue

            for i, tile in enumerate(column):
                fallen_tiles.append(Tile(tile.type, Point(tile.grid_position.x, missing_tiles + i)))

        fallen_tiles.sort(key=lambda x: x.grid_position)

        return InconsistentGrid(fallen_tiles, self.size)

    def fill_with_unknown(self) -> Grid:
        return self


class InconsistentGrid(Grid):
    def find_clusters(self, minimal_quantity=2, maximal_distance=3) -> Set[Tuple[Tile]]:
        return set()

    def fill_with_unknown(self) -> Grid:
        tiles = self.tiles.copy()

        # FIXME there should be a better approximation for screensize... meh what ever
        for y in range(0, self.size.y):
            for x in range(0, self.size.x):
                index = x + y * self.size.x
                expected_grid_position = Point(x, y)
                if len(tiles) <= index or tiles[index].grid_position != expected_grid_position:
                    tiles.insert(index, Tile(TileType.UNKNOWN, expected_grid_position))

        return Grid(tiles, self.size)


class EmptyGrid(Grid):
    def __init__(self):
        super().__init__([], Point(0, 0))

    def find_clusters(self, minimal_quantity=2, maximal_distance=3) -> Set[Tuple[Tile]]:
        return set()
