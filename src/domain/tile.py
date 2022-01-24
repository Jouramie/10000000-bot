from dataclasses import dataclass, field
from enum import Enum, auto
from math import sqrt
from typing import List, Set, Tuple, Sized, Iterable


class TileType(Enum):
    CHEST = auto()
    KEY = auto()
    LOGS = auto()
    ROCKS = auto()
    SHIELD = auto()
    SWORD = auto()
    WAND = auto()


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
        if isinstance(other, type(self)):
            return Point(self.x + other.x, self.y + other.y)
        raise NotImplementedError()

    def __sub__(self, other):
        if isinstance(other, type(self)):
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


def find_pairs_in_lines(lines: List[List[Tile]]) -> Set[Tuple[Tile]]:
    return set().union(*(find_pairs_in_line(line) for line in lines))


def find_pairs_in_line(line: List[Tile]) -> Set[Tuple[Tile]]:
    pairs = {find_pair_in_triple(line[i : i + 3]) for i in range(0, len(line) - 2)}
    return {pair for pair in pairs if pair is not None}


def find_pair_in_triple(triple: List[Tile]) -> Tuple[Tile] | None:
    different_types = {tile.type for tile in triple}

    if len(different_types) != 2:
        return

    potential_type = different_types.pop()
    potential_pair = tuple(tile for tile in triple if tile.type == potential_type)
    if len(potential_pair) == 2:
        return potential_pair
    else:
        potential_type = different_types.pop()
        return tuple(tile for tile in triple if tile.type == potential_type)


@dataclass(frozen=True)
class Grid(Sized, Iterable[Tile]):
    """
    8x7 56 tiles
    self.size.x=8
    self.size.y=7
    """

    tiles: List[Tile] = field(default_factory=list)
    size: Point = Point(0, 0)

    def __iter__(self):
        return iter(self.tiles)

    def __len__(self) -> int:
        return len(self.tiles)

    def get_row(self, y) -> List[Tile]:
        return self.tiles[y * self.size.x : (y + 1) * self.size.x]

    def get_column(self, x) -> List[Tile]:
        return self.tiles[x :: self.size.x]

    def get_rows(self) -> List[List[Tile]]:
        return [self.tiles[i : i + self.size.x] for i in range(0, len(self), self.size.x)]

    def get_columns(self) -> List[List[Tile]]:
        return [self.tiles[i :: self.size.x] for i in range(0, self.size.x)]

    # TODO
    def find_clusters(self, minimal_quantity=2, maximal_distance=3) -> Set[Tuple[Tile]]:
        return find_pairs_in_lines(self.get_columns() + self.get_rows())


class InconsistentGrid(Grid):
    def __init__(self, tiles: List[Tile], size: Point):
        super().__init__(tiles, size)

    def find_clusters(self, minimal_quantity=2, maximal_distance=3) -> Set[Tuple[Tile]]:
        return set()
