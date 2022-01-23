from unittest import TestCase

from src.domain.tile import GridPosition, Grid


class TestGivenEmptyGrid(TestCase):
    def when_arrange_tiles_as_grid_then_grid_is_empty(self):
        grid = Grid([], GridPosition(0, 0))

        arranged_tiles = grid.get_columns()

        self.assertEqual(arranged_tiles, [])


class TestFilledGrid(TestCase):
    grid = Grid([0, 1, 2, 3, 4, 5], GridPosition(3, 2))

    def when_get_columns_then_grid_is_arranged(self):
        columns = self.grid.get_columns()

        self.assertEqual([[0, 3], [1, 4], [2, 5]], columns)

    def when_get_rows_then_grid_is_arranged(self):
        rows = self.grid.get_rows()

        self.assertEqual([[0, 1, 2], [3, 4, 5]], rows)


class TestArrangedGrid(TestCase):
    def when_query_then_find_right_number(self):
        tiles = [[0, 3], [1, 4], [2, 5]]

        self.assertEqual(tiles[0][0], 0)
        self.assertEqual(tiles[1][0], 1)
        self.assertEqual(tiles[2][0], 2)
        self.assertEqual(tiles[0][1], 3)
        self.assertEqual(tiles[1][1], 4)
        self.assertEqual(tiles[2][1], 5)
