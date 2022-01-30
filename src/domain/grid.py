from dataclasses import dataclass
from enum import Enum, auto
from functools import reduce
from math import sqrt
from typing import List, Set, Tuple, Sized, Iterable, FrozenSet, Dict

from frozendict import frozendict, FrozenOrderedDict


class TileType(Enum):
    CHEST = auto()
    KEY = auto()
    LOGS = auto()
    ROCKS = auto()
    SHIELD = auto()
    SWORD = auto()
    WAND = auto()
    STAR = auto()
    UNKNOWN = auto()

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def __lt__(self, other) -> bool:
        return (self.y, self.x) < (other.y, other.x)

    def __mul__(self, other):
        if isinstance(other, int):
            return Point(self.x * other, self.y * other)
        raise NotImplementedError()

    def __add__(self, other):
        if type(self) is type(other):
            return Point(self.x + other.x, self.y + other.y)
        raise NotImplementedError()

    def __sub__(self, other):
        if type(self) is type(other):
            return Point(self.x - other.x, self.y - other.y)
        raise NotImplementedError()

    def __str__(self):
        return str((self.x, self.y))

    def distance_between(self, other) -> int:
        return int(sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2))


@dataclass(frozen=True)
class ScreenSquare:
    left: int = 0
    top: int = 0
    height: int = 0
    width: int = 0

    def __lt__(self, other) -> bool:
        return (self.top, self.left) < (other.top, other.left)

    def find_center(self) -> Point:
        return Point(self.left + int(self.width / 2), self.top + int(self.height / 2))


@dataclass(frozen=True)
class Tile:
    type: TileType
    screen_square: ScreenSquare | None
    grid_position: Point

    def has_type(self, tile_type: TileType) -> bool:
        return self.type == tile_type

    def __str__(self):
        return f"{{{str(self.type)} {str(self.grid_position)}}}"


# TODO use stars in combo


@dataclass(frozen=True)
class Cluster(Sized, Iterable[Tile]):
    # FIXME this field is convenient but not necessary
    type: TileType
    tiles: FrozenSet[Tile]

    def __iter__(self):
        return iter(self.tiles)

    def __len__(self) -> int:
        return len(self.tiles)

    def get_completed_line_index(self):
        present_indices_in_line = self._find_present_indices_in_row()

        if len(present_indices_in_line) == 1:
            return present_indices_in_line.pop()

        # Get any element from the set
        for tile in self.tiles:
            return tile.grid_position.x

    def _find_present_indices_in_row(self) -> set[int]:
        return {tile.grid_position.y for tile in self}

    def _find_present_indices_in_column(self) -> set[int]:
        return {tile.grid_position.x for tile in self}

    def find_completing_row_indices(self) -> Set[int]:
        return Cluster._find_completing_indices_in_line(self._find_present_indices_in_row())

    def find_completing_column_indices(self) -> Set[int]:
        return Cluster._find_completing_indices_in_line(self._find_present_indices_in_column())

    @staticmethod
    def _find_completing_indices_in_line(present_index_in_line: {Set[int]}) -> Set[int]:
        if len(present_index_in_line) == 1:
            return set()

        min_present_tile = min(present_index_in_line)
        max_present_tile = max(present_index_in_line)

        if min_present_tile + 1 == max_present_tile:
            return {min_present_tile - 1, max_present_tile + 1}

        for i in range(min_present_tile, max_present_tile):
            if i not in present_index_in_line:
                return {i}


@dataclass(frozen=True)
class Move:
    cluster: Cluster
    tile_to_move: Tile
    grid_destination: Point
    impact: FrozenOrderedDict[TileType, int]

    def __str__(self):
        return (
            f"{{Move {str(self.tile_to_move)} -> {str(self.grid_destination)} " f"for { {str(tile_type):impact for tile_type, impact in self.impact.items()}}}}"
        )

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

    def calculate_impact(self, tile_type: TileType) -> int:
        return self.impact.get(tile_type, 0)

    def calculate_value(self, value_per_tile_type: Dict[TileType, int]) -> int:
        return reduce(
            lambda x, y: x + y,
            [self.impact[tile_type] * value_per_tile_type.get(tile_type, 0) for tile_type in self.impact],
            0,
        )


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
        different_types = {tile.type for tile in triple if tile.type != TileType.UNKNOWN}

        # FIXME might not be needed with the add of unknown tiles
        # Excludes the clusters with too much missing tiles
        grid_xs = {tile.grid_position.x for tile in triple}
        grid_ys = {tile.grid_position.y for tile in triple}
        if sum(grid_xs) - min(grid_xs) * 3 != 3 and sum(grid_ys) - min(grid_ys) * 3 != 3:
            return

        for potential_type in different_types:
            potential_cluster = frozenset(tile for tile in triple if tile.type == potential_type)
            if len(potential_cluster) == 2:
                return Cluster(potential_type, potential_cluster)

    def find_possible_moves(self) -> Set[Move]:
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
                    movements.add(Move(cluster, matching_tile, destination, self.simulate_line_shift(matching_tile.grid_position, destination)))
            else:
                y = cluster.get_completed_line_index()
                completing_column_indices = cluster.find_completing_column_indices()
                completing_cluster_columns = {missing_column_no: self.get_column(missing_column_no) for missing_column_no in completing_column_indices}

                matching_tiles = {(row_no, tile) for row_no, row in completing_cluster_columns.items() for tile in row if tile.type == cluster.type}
                for x, matching_tile in matching_tiles:
                    destination = Point(x, y)
                    movements.add(Move(cluster, matching_tile, destination, self.simulate_line_shift(matching_tile.grid_position, destination)))

        return movements

    def simulate_line_shift(self, shift_start: Point, shift_destination: Point) -> Dict[TileType, int]:
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

        return frozendict(impact)

    def shift(self, shift_start: Point, shift_destination: Point):
        assert shift_start.x == shift_destination.x or shift_start.y == shift_destination.y

        shift = shift_destination - shift_start

        if shift.y == 0:
            line = self.get_row(shift_start.y)
            distance = shift.x
            new_line = [Tile(tile.type, None, Point(x, shift_start.y)) for x, tile in enumerate(line[-distance:] + line[:-distance])]
            return self.set_row(shift_start.y, new_line)
        else:
            line = self.get_column(shift_start.x)
            distance = shift.y
            new_line = [Tile(tile.type, None, Point(shift_start.x, y)) for y, tile in enumerate(line[-distance:] + line[:-distance])]
            return self.set_column(shift_start.x, new_line)

    def remove_completed_combos(self):
        combining_tiles = set()
        for triple in self.get_triples():
            different_types = {tile.type for tile in triple}
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
                fallen_tiles.append(Tile(tile.type, None, Point(tile.grid_position.x, missing_tiles + i)))

        fallen_tiles.sort(key=lambda x: x.grid_position)

        return InconsistentGrid(fallen_tiles, self.size)


class InconsistentGrid(Grid):
    def __init__(self, tiles=None, size: Point = Point(0, 0)):
        if tiles is None:
            tiles = []
        super().__init__(tiles, size)

    def find_clusters(self, minimal_quantity=2, maximal_distance=3) -> Set[Tuple[Tile]]:
        return set()
