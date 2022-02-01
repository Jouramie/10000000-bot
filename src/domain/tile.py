from dataclasses import dataclass
from enum import Enum, auto
from typing import Sized, Iterable, FrozenSet, Set

from src.domain.screen import Point


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
class Tile:
    type: TileType
    grid_position: Point

    def has_type(self, tile_type: TileType) -> bool:
        return self.type == tile_type

    def __str__(self):
        return f"{{{str(self.type)} {str(self.grid_position)}}}"


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
