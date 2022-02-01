from typing import List

from src.domain.grid import Grid
from src.domain.screen import Point
from src.domain.tile import TileType, Tile


def _a_grid(tile_types: List[TileType], size: Point):
    return Grid([Tile(tile_types[x + y * size.x], None, Point(x, y)) for y in range(size.y) for x in range(size.x)], size)
