from typing import List
from unittest import TestCase

from src.domain.grid import Point, Grid, TileType, Tile


def _a_grid(tile_types: List[TileType], size: Point):
    return Grid([Tile(tile_types[x + y * size.x], None, Point(x, y)) for y in range(size.y) for x in range(size.x)], size)


def _to_types(tiles: List[List[Tile]]) -> List[List[TileType]]:
    return [[tile.type for tile in line] for line in tiles]


class TestGivenEmptyGrid(TestCase):
    def when_arrange_tiles_as_grid_then_grid_is_empty(self):
        grid = Grid([], Point(0, 0))

        arranged_tiles = grid.get_columns()

        self.assertEqual(arranged_tiles, [])


class TestGridLines(TestCase):
    grid = _a_grid([TileType.KEY, TileType.LOGS, TileType.SHIELD, TileType.SWORD, TileType.WAND, TileType.STAR], Point(3, 2))

    def when_get_columns_then_grid_is_arranged(self):
        columns = self.grid.get_columns()

        self.assertEqual([[TileType.KEY, TileType.SWORD], [TileType.LOGS, TileType.WAND], [TileType.SHIELD, TileType.STAR]], _to_types(columns))

    def when_get_rows_then_grid_is_arranged(self):
        rows = self.grid.get_rows()

        self.assertEqual([[TileType.KEY, TileType.LOGS, TileType.SHIELD], [TileType.SWORD, TileType.WAND, TileType.STAR]], _to_types(rows))


class TestGridShifts(TestCase):
    tiles = [TileType.KEY, TileType.LOGS, TileType.SHIELD, TileType.SWORD, TileType.WAND, TileType.STAR, TileType.UNKNOWN, TileType.CHEST, TileType.ROCKS]
    size = Point(3, 3)

    def when_row_is_shifted_then_tiles_change_place(self):
        grid = _a_grid(self.tiles, self.size)

        grid.shift(Point(0, 0), Point(2, 0))

        self.assertEqual(
            [TileType.LOGS, TileType.SHIELD, TileType.KEY, TileType.SWORD, TileType.WAND, TileType.STAR, TileType.UNKNOWN, TileType.CHEST, TileType.ROCKS],
            [tile.type for tile in grid],
        )

    def when_column_is_shifted_then_tiles_change_place(self):
        grid = _a_grid(self.tiles, self.size)

        grid.shift(Point(1, 1), Point(1, 0))

        self.assertEqual(
            [TileType.KEY, TileType.WAND, TileType.SHIELD, TileType.SWORD, TileType.CHEST, TileType.STAR, TileType.UNKNOWN, TileType.LOGS, TileType.ROCKS],
            [tile.type for tile in grid],
        )
