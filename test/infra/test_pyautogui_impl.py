from unittest import TestCase
from unittest.mock import patch

from PIL import Image

from src.domain.tile import TileType
from src.infra.pyautogui_impl import find_grid

easy_grid = Image.open("test/infra/easy-grid.png")
key_in_wrong_column_4_3 = Image.open("test/infra/key-in-wrong-column-4-3.png")
sword_not_detected_1_6 = Image.open("test/infra/sword-not-detected-1-6.png")
star_6_0 = Image.open("test/infra/star-6-0.png")
so_many_errors = Image.open("test/infra/so-many-errors.png")
while_combo = Image.open("test/infra/while-combo.png")


class TestFindGrid(TestCase):
    @patch("pyautogui.screenshot", return_value=easy_grid)
    @patch("win32gui.GetWindowRect", return_value=(0, 0, easy_grid.size[0], easy_grid.size[1]))
    def test_find_grid(self, screenshot, get_window_rect):
        grid = find_grid()

        expected_grid = [
            TileType.WAND,
            TileType.SWORD,
            TileType.KEY,
            TileType.LOGS,
            TileType.SHIELD,
            TileType.KEY,
            TileType.WAND,
            TileType.KEY,
            TileType.KEY,
            TileType.WAND,
            TileType.LOGS,
            TileType.SWORD,
            TileType.WAND,
            TileType.SHIELD,
            TileType.SWORD,
            TileType.WAND,
            TileType.SHIELD,
            TileType.SWORD,
            TileType.CHEST,
            TileType.KEY,
            TileType.ROCKS,
            TileType.SWORD,
            TileType.SHIELD,
            TileType.KEY,
            TileType.LOGS,
            TileType.ROCKS,
            TileType.SWORD,
            TileType.WAND,
            TileType.SHIELD,
            TileType.LOGS,
            TileType.WAND,
            TileType.CHEST,
            TileType.CHEST,
            TileType.KEY,
            TileType.ROCKS,
            TileType.SWORD,
            TileType.KEY,
            TileType.SWORD,
            TileType.ROCKS,
            TileType.KEY,
            TileType.LOGS,
            TileType.SWORD,
            TileType.CHEST,
            TileType.KEY,
            TileType.SHIELD,
            TileType.WAND,
            TileType.LOGS,
            TileType.SWORD,
            TileType.KEY,
            TileType.WAND,
            TileType.SWORD,
            TileType.WAND,
            TileType.SWORD,
            TileType.KEY,
            TileType.CHEST,
            TileType.WAND,
        ]

        self.assertEqual(expected_grid, [tile.type for tile in grid])

    @patch("pyautogui.screenshot", return_value=star_6_0)
    @patch("win32gui.GetWindowRect", return_value=(0, 0, star_6_0.size[0], star_6_0.size[1]))
    def test_star_6_0(self, screenshot, get_window_rect):
        grid = find_grid()

        expected_grid = [
            TileType.SWORD,
            TileType.WAND,
            TileType.LOGS,
            TileType.WAND,
            TileType.LOGS,
            TileType.STAR,
            TileType.SWORD,
            TileType.LOGS,
            TileType.WAND,
            TileType.KEY,
            TileType.WAND,
            TileType.ROCKS,
            TileType.KEY,
            TileType.ROCKS,
            TileType.SWORD,
            TileType.WAND,
            TileType.LOGS,
            TileType.SWORD,
            TileType.SHIELD,
            TileType.LOGS,
            TileType.CHEST,
            TileType.WAND,
            TileType.ROCKS,
            TileType.SHIELD,
            TileType.SWORD,
            TileType.KEY,
            TileType.CHEST,
            TileType.KEY,
            TileType.ROCKS,
            TileType.WAND,
            TileType.KEY,
            TileType.KEY,
            TileType.LOGS,
            TileType.SHIELD,
            TileType.SHIELD,
            TileType.ROCKS,
            TileType.KEY,
            TileType.LOGS,
            TileType.LOGS,
            TileType.SWORD,
            TileType.WAND,
            TileType.CHEST,
            TileType.CHEST,
            TileType.WAND,
            TileType.KEY,
            TileType.SWORD,
            TileType.ROCKS,
            TileType.SWORD,
            TileType.ROCKS,
            TileType.WAND,
            TileType.KEY,
            TileType.WAND,
            TileType.SWORD,
            TileType.SWORD,
            TileType.KEY,
            TileType.WAND,
        ]

        self.assertEqual(expected_grid, [tile.type for tile in grid])

    @patch("pyautogui.screenshot", return_value=key_in_wrong_column_4_3)
    @patch("win32gui.GetWindowRect", return_value=(0, 0, key_in_wrong_column_4_3.size[0], key_in_wrong_column_4_3.size[1]))
    def test_key_in_wrong_column_4_3(self, screenshot, get_window_rect):
        grid = find_grid()

        expected_grid = [
            TileType.LOGS,
            TileType.WAND,
            TileType.KEY,
            TileType.ROCKS,
            TileType.SHIELD,
            TileType.LOGS,
            TileType.SWORD,
            TileType.SWORD,
            TileType.WAND,
            TileType.ROCKS,
            TileType.SWORD,
            TileType.SHIELD,
            TileType.WAND,
            TileType.SWORD,
            TileType.WAND,
            TileType.SWORD,
            TileType.SHIELD,
            TileType.SHIELD,
            TileType.LOGS,
            TileType.KEY,
            TileType.KEY,
            TileType.SHIELD,
            TileType.LOGS,
            TileType.LOGS,
            TileType.LOGS,
            TileType.WAND,
            TileType.SWORD,
            TileType.WAND,
            TileType.SHIELD,
            TileType.CHEST,
            TileType.WAND,
            TileType.KEY,
            TileType.SHIELD,
            TileType.CHEST,
            TileType.SHIELD,
            TileType.KEY,
            TileType.CHEST,
            TileType.KEY,
            TileType.LOGS,
            TileType.LOGS,
            TileType.SHIELD,
            TileType.SHIELD,
            TileType.WAND,
            TileType.LOGS,
            TileType.KEY,
            TileType.WAND,
            TileType.SWORD,
            TileType.WAND,
            TileType.SWORD,
            TileType.CHEST,
            TileType.SWORD,
            TileType.CHEST,
            TileType.SHIELD,
            TileType.KEY,
            TileType.ROCKS,
            TileType.LOGS,
        ]

        self.assertEqual(expected_grid, [tile.type for tile in grid])

    @patch("pyautogui.screenshot", return_value=so_many_errors)
    @patch("win32gui.GetWindowRect", return_value=(0, 0, so_many_errors.size[0], so_many_errors.size[1]))
    def test_so_many_errors(self, screenshot, get_window_rect):
        grid = find_grid()

        expected_grid = [
            TileType.KEY,
            TileType.WAND,
            TileType.SWORD,
            TileType.CHEST,
            TileType.WAND,
            TileType.WAND,
            TileType.SWORD,
            TileType.CHEST,
            TileType.WAND,
            TileType.ROCKS,
            TileType.SHIELD,
            TileType.SWORD,
            TileType.ROCKS,
            TileType.SWORD,
            TileType.WAND,
            TileType.CHEST,
            TileType.SWORD,
            TileType.KEY,
            TileType.SWORD,
            TileType.SHIELD,
            TileType.SHIELD,
            TileType.LOGS,
            TileType.WAND,
            TileType.SWORD,
            TileType.WAND,
            TileType.WAND,
            TileType.KEY,
            TileType.SHIELD,
            TileType.KEY,
            TileType.LOGS,
            TileType.SWORD,
            TileType.WAND,
            TileType.LOGS,
            TileType.KEY,
            TileType.CHEST,
            TileType.LOGS,
            TileType.SHIELD,
            TileType.SWORD,
            TileType.ROCKS,
            TileType.SWORD,
            TileType.CHEST,
            TileType.SHIELD,
            TileType.ROCKS,
            TileType.KEY,
            TileType.SWORD,
            TileType.WAND,
            TileType.LOGS,
            TileType.SWORD,
            TileType.LOGS,
            TileType.SWORD,
            TileType.CHEST,
            TileType.WAND,
            TileType.WAND,
            TileType.KEY,
            TileType.CHEST,
            TileType.WAND,
        ]

        self.assertEqual(expected_grid, [tile.type for tile in grid])

    @patch("pyautogui.screenshot", return_value=sword_not_detected_1_6)
    @patch("win32gui.GetWindowRect", return_value=(0, 0, sword_not_detected_1_6.size[0], sword_not_detected_1_6.size[1]))
    def test_sword_not_detected_1_6(self, screenshot, get_window_rect):
        grid = find_grid()

        expected_grid = [
            TileType.WAND,
            TileType.ROCKS,
            TileType.CHEST,
            TileType.WAND,
            TileType.LOGS,
            TileType.ROCKS,
            TileType.SWORD,
            TileType.WAND,
            TileType.WAND,
            TileType.SWORD,
            TileType.WAND,
            TileType.SWORD,
            TileType.SHIELD,
            TileType.SWORD,
            TileType.ROCKS,
            TileType.KEY,
            TileType.SWORD,
            TileType.SWORD,
            TileType.KEY,
            TileType.WAND,
            TileType.SHIELD,
            TileType.WAND,
            TileType.SWORD,
            TileType.LOGS,
            TileType.CHEST,
            TileType.SHIELD,
            TileType.SWORD,
            TileType.LOGS,
            TileType.WAND,
            TileType.CHEST,
            TileType.SHIELD,
            TileType.LOGS,
            TileType.CHEST,
            TileType.SHIELD,
            TileType.SWORD,
            TileType.KEY,
            TileType.SHIELD,
            TileType.SWORD,
            TileType.ROCKS,
            TileType.CHEST,
            TileType.LOGS,
            TileType.SWORD,
            TileType.ROCKS,
            TileType.WAND,
            TileType.LOGS,
            TileType.KEY,
            TileType.LOGS,
            TileType.WAND,
            TileType.KEY,
            TileType.SWORD,
            TileType.CHEST,
            TileType.LOGS,
            TileType.SHIELD,
            TileType.KEY,
            TileType.CHEST,
            TileType.WAND,
        ]

        self.assertEqual(expected_grid, [tile.type for tile in grid])

    @patch("pyautogui.screenshot", return_value=while_combo)
    @patch("win32gui.GetWindowRect", return_value=(0, 0, while_combo.size[0], while_combo.size[1]))
    def test_sword_not_detected_1_6(self, screenshot, get_window_rect):
        grid = find_grid()

        expected_grid = [
            TileType.SWORD,
            TileType.KEY,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.SWORD,
            TileType.LOGS,
            TileType.SWORD,
            TileType.SWORD,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.WAND,
            TileType.LOGS,
            TileType.LOGS,
            TileType.CHEST,
            TileType.SHIELD,
            TileType.LOGS,
            TileType.KEY,
            TileType.WAND,
            TileType.CHEST,
            TileType.ROCKS,
            TileType.SHIELD,
            TileType.WAND,
            TileType.SHIELD,
            TileType.LOGS,
            TileType.ROCKS,
            TileType.WAND,
            TileType.KEY,
            TileType.SHIELD,
            TileType.CHEST,
            TileType.WAND,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.LOGS,
            TileType.KEY,
            TileType.ROCKS,
            TileType.WAND,
            TileType.CHEST,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.UNKNOWN,
            TileType.SHIELD,
            TileType.KEY,
            TileType.LOGS,
            TileType.SWORD,
            TileType.ROCKS,
            TileType.ROCKS,
            TileType.LOGS,
            TileType.ROCKS,
            TileType.LOGS,
            TileType.KEY,
            TileType.WAND,
        ]

        self.assertEqual(expected_grid, [tile.type for tile in grid])
