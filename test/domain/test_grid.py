from typing import List
from unittest import TestCase

from src.domain.grid import Grid
from src.domain.screen import Point
from src.domain.tile import TileType, Tile
from test.utils import _a_grid


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


class TestMultipleClusters(TestCase):
    grid = _a_grid(
        [TileType.KEY, TileType.KEY, TileType.STAR, TileType.SWORD, TileType.WAND, TileType.STAR, TileType.CHEST, TileType.WAND, TileType.CHEST],
        Point(3, 3),
    )

    def when_find_clusters_then_all_2_clusters_are_found(self):
        clusters = self.grid.find_clusters()

        self.assertEqual(
            {
                frozenset((Point(0, 0), Point(1, 0))),
                frozenset((Point(2, 0), Point(2, 1))),
                frozenset((Point(1, 1), Point(1, 2))),
                frozenset((Point(0, 2), Point(2, 2))),
            },
            {frozenset(tile.grid_position for tile in cluster) for cluster in clusters},
        )


class TestGridFullOfUnknown(TestCase):
    grid = _a_grid(
        [TileType.UNKNOWN] * 9,
        Point(3, 3),
    )

    def when_find_clusters_then_all_2_clusters_are_found(self):
        clusters = self.grid.find_clusters()

        self.assertEqual(set(), clusters)


class TestGridShifts(TestCase):
    grid = _a_grid(
        [TileType.KEY, TileType.LOGS, TileType.SHIELD, TileType.SWORD, TileType.WAND, TileType.STAR, TileType.UNKNOWN, TileType.CHEST, TileType.ROCKS],
        Point(3, 3),
    )

    def when_row_is_shifted_then_tiles_change_place(self):
        resulting_grid = self.grid.shift(Point(0, 0), Point(2, 0))

        self.assertEqual(
            [TileType.LOGS, TileType.SHIELD, TileType.KEY, TileType.SWORD, TileType.WAND, TileType.STAR, TileType.UNKNOWN, TileType.CHEST, TileType.ROCKS],
            [tile.type for tile in resulting_grid],
        )

    def when_column_is_shifted_then_tiles_change_place(self):
        resulting_grid = self.grid.shift(Point(1, 1), Point(1, 0))

        self.assertEqual(
            [TileType.KEY, TileType.WAND, TileType.SHIELD, TileType.SWORD, TileType.CHEST, TileType.STAR, TileType.UNKNOWN, TileType.LOGS, TileType.ROCKS],
            [tile.type for tile in resulting_grid],
        )


class TestGridDoubleCombo(TestCase):
    grid = _a_grid(
        [TileType.KEY, TileType.KEY, TileType.KEY, TileType.SWORD, TileType.WAND, TileType.STAR, TileType.CHEST, TileType.CHEST, TileType.CHEST],
        Point(3, 3),
    )

    def when_remove_completed_combos_then_the_two_combos_are_removed(self):
        combining_tiles, resulting_grid = self.grid.remove_completed_combos()

        self.assertEqual(
            {Point(0, 0), Point(1, 0), Point(2, 0), Point(0, 2), Point(1, 2), Point(2, 2)},
            {tile.grid_position for tile in combining_tiles},
        )
        self.assertEqual(
            [Point(0, 1), Point(1, 1), Point(2, 1)],
            [tile.grid_position for tile in resulting_grid],
        )


class TestGridCrossCombo(TestCase):
    grid = _a_grid(
        [TileType.ROCKS, TileType.KEY, TileType.KEY, TileType.KEY, TileType.KEY, TileType.KEY, TileType.CHEST, TileType.KEY, TileType.CHEST],
        Point(3, 3),
    )

    def when_remove_completed_combos_then_the_two_combos_are_removed(self):
        combining_tiles, resulting_grid = self.grid.remove_completed_combos()

        self.assertEqual(
            {Point(1, 0), Point(0, 1), Point(1, 1), Point(2, 1), Point(1, 2)},
            {tile.grid_position for tile in combining_tiles},
        )
        self.assertEqual(
            [Point(0, 0), Point(2, 0), Point(0, 2), Point(2, 2)],
            [tile.grid_position for tile in resulting_grid],
        )


class TestGridDoubleComboWithGravity(TestCase):
    grid = _a_grid(
        [
            TileType.UNKNOWN,
            TileType.SWORD,
            TileType.KEY,
            TileType.UNKNOWN,
            TileType.KEY,
            TileType.KEY,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.SWORD,
            TileType.SWORD,
        ],
        Point(4, 3),
    )

    def when_simulate_line_shift_then_the_two_combos_are_counted(self):
        impact = self.grid.simulate_line_shift(Point(1, 0), Point(1, 2))[0]

        self.assertEqual(
            {TileType.KEY: 3, TileType.SWORD: 3},
            impact,
        )
