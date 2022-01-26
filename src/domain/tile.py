from dataclasses import dataclass
from enum import Enum, auto
from math import sqrt
from typing import List, Set, Tuple, Sized, Iterable, FrozenSet


class TileType(Enum):
    CHEST = auto()
    KEY = auto()
    LOGS = auto()
    ROCKS = auto()
    SHIELD = auto()
    SWORD = auto()
    WAND = auto()
    STAR = auto()


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

    def distance_between(self, other) -> int:
        return int(sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2))


@dataclass(frozen=True)
class ScreenSquare:
    left: int
    top: int
    height: int
    width: int

    def __lt__(self, other) -> bool:
        return (self.top, self.left) < (other.top, other.left)

    def find_center(self) -> Point:
        return Point(self.left + int(self.width / 2), self.top + int(self.height / 2))


@dataclass(frozen=True)
class Tile:
    type: TileType
    screen_square: ScreenSquare
    grid_position: Point

    def has_type(self, tile_type: TileType) -> bool:
        return self.type == tile_type


@dataclass(frozen=True)
class Cluster:
    # FIXME this field is convenient but not necessary
    type: TileType
    tiles: FrozenSet[Tile]

    def get_completed_line_index(self):
        present_indices_in_line = self._find_present_indices_in_row()

        if len(present_indices_in_line) == 1:
            return present_indices_in_line.pop()

        # Get any element from the set
        for tile in self.tiles:
            return tile.grid_position.x

    def _find_present_indices_in_row(self) -> set[int]:
        return {tile.grid_position.y for tile in self.tiles}

    def _find_present_indices_in_column(self) -> set[int]:
        return {tile.grid_position.x for tile in self.tiles}

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

    def get_row(self, y) -> List[Tile]:
        if y == -1 or y == self.size.y + 1:
            return []
        return self.tiles[y * self.size.x : (y + 1) * self.size.x]

    def get_column(self, x) -> List[Tile]:
        if x == -1 or x == self.size.x + 1:
            return []
        return self.tiles[x :: self.size.x]

    def get_rows(self) -> List[List[Tile]]:
        return [self.tiles[i : i + self.size.x] for i in range(0, len(self), self.size.x)]

    def get_columns(self) -> List[List[Tile]]:
        return [self.tiles[i :: self.size.x] for i in range(0, self.size.x)]

    # TODO handle min max
    def find_clusters(self, minimal_quantity=2, maximal_distance=3) -> Set[Cluster]:
        return Grid._find_clusters_in_lines(self.get_columns() + self.get_rows())

    @staticmethod
    def _find_clusters_in_lines(lines: List[List[Tile]]) -> Set[Cluster]:
        return set().union(*(Grid._find_pairs_in_line(line) for line in lines))

    @staticmethod
    def _find_pairs_in_line(line: List[Tile]) -> Set[Cluster]:
        pairs = {Grid._find_pair_in_triple(line[i : i + 3]) for i in range(0, len(line) - 2)}
        return {pair for pair in pairs if pair is not None}

    @staticmethod
    def _find_pair_in_triple(triple: List[Tile]) -> Cluster | None:
        different_types = {tile.type for tile in triple}

        if len(different_types) != 2:
            return

        potential_type = different_types.pop()
        potential_cluster = frozenset(tile for tile in triple if tile.type == potential_type)
        if len(potential_cluster) == 2:
            return Cluster(potential_type, potential_cluster)
        else:
            potential_type = different_types.pop()
            return Cluster(potential_type, frozenset(tile for tile in triple if tile.type == potential_type))


class InconsistentGrid(Grid):
    def __init__(self, tiles=None, size: Point = Point(0, 0)):
        if tiles is None:
            tiles = []
        super().__init__(tiles, size)

    def find_clusters(self, minimal_quantity=2, maximal_distance=3) -> Set[Tuple[Tile]]:
        return set()
