import logging
from functools import reduce
from typing import List

import pyautogui
import pyscreeze
import win32gui

from src.domain.game_state import GameState, GameStateDetector
from src.domain.move import TileMover, Move
from src.domain.tile import TileType, Tile, ScreenSquare, Point, Grid, InconsistentGrid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


TILE_ASSETS = {
    TileType.CHEST: "assets/tiles/chest.png",
    TileType.KEY: "assets/tiles/key.png",
    TileType.LOGS: "assets/tiles/logs.png",
    TileType.ROCKS: "assets/tiles/rocks.png",
    TileType.SHIELD: "assets/tiles/shield.png",
    TileType.SWORD: "assets/tiles/sword.png",
    TileType.WAND: "assets/tiles/wand.png",
}

GRID_SIZE_X = 8
GRID_SIZE_Y = 7
GRID_SIZE = Point(GRID_SIZE_X, GRID_SIZE_Y)

MOVE_SPEED = 1 / 600

REAL_WINDOW_TITLE = "10000000"
TESTING_WINDOW_TITLE = "C:\\Users\\Utilisateur\\dev\\10000000\\broken-grid,png.png - Greenshot image editor"
GAME_WINDOW_TITLE = REAL_WINDOW_TITLE


def activate_window(title):
    matching_windows = [window for window in pyautogui.getWindowsWithTitle(title) if window.title == title]
    if len(matching_windows) == 0:
        return None
    elif len(matching_windows) > 1:
        logger.warning(f"Looks like there are many windows of {title} opened...")

    try:
        win = matching_windows[0]
        win.activate()
    except Exception as e:
        logger.warning(e)


def find_window_region(title):
    # activate_window(title)

    window_handle = win32gui.FindWindow(None, title)
    win_region = win32gui.GetWindowRect(window_handle)

    return win_region[0], win_region[1], win_region[2] - win_region[0], win_region[3] - win_region[1]


def locate_all_on_window(needle_image, window_title) -> List[pyscreeze.Box]:
    region = find_window_region(window_title)
    window_screenshot = pyautogui.screenshot(region=region)
    # window_screenshot.show()

    logger.debug(f"Game window located at {region}.")
    # TODO lower confidence and undupe images
    return [
        pyscreeze.Box(box.left + region[0], box.top + region[1], box.width, box.height)
        for box in pyautogui.locateAll(needle_image, window_screenshot, grayscale=True)
    ]


def find_grid() -> Grid:
    """Should detect 8x7 56 tiles."""

    tiles = sorted(
        [
            (tile_type, ScreenSquare(tile.left, tile.top, tile.height, tile.width))
            for tile_type, asset in TILE_ASSETS.items()
            for tile in locate_all_on_window(asset, GAME_WINDOW_TITLE)
        ],
        key=lambda tile: tile[1],
    )

    # TODO attribution of the positions assumes all the tiles are detected. This could go really wrong.
    if len(tiles) != 56:
        logger.warning(f"{len(tiles)} tiles detected. Expected 56. Returning InconsistentGrid.")
        return InconsistentGrid([Tile(tile_type, screen_square, Point(-1, -1)) for tile_type, screen_square in tiles], GRID_SIZE)

    return Grid(
        [Tile(*tile) for tile in [(*tiles[i + j * GRID_SIZE_X], Point(i, j)) for j in range(0, GRID_SIZE_Y) for i in range(0, GRID_SIZE_X)]],
        GRID_SIZE,
    )


class PyAutoGuiGameStateDetector(GameStateDetector):
    def __init__(self) -> None:
        super().__init__()

    def detect_game_state(self) -> GameState:
        logger.debug("Finding tiles.")
        game_state = GameState(grid=find_grid())
        logger.debug(f"Found {len(game_state.grid)} tiles.")

        return game_state


class PyAutoGuiTileMover(TileMover):
    def execute(self, move: Move):
        logger.info(
            f"Completing cluster{move.get_combo_type()} "
            + reduce(lambda x, y: x + y, (f"({tile.grid_position.x}, {tile.grid_position.y}) " for tile in move.cluster.tiles))
            + f"with ({move.tile_to_move.grid_position.x}, {move.tile_to_move.grid_position.y}). "
            f"moving to ({move.grid_destination.x}, {move.grid_destination.y})"
        )

        start_drag = move.tile_to_move.screen_square.find_center()
        end_drag = move.calculate_screen_destination()

        logger.debug(f"Starting drag from {start_drag}.")
        pyautogui.moveTo(start_drag.x, start_drag.y, duration=0.2)
        logger.debug(f"Ending drag to {end_drag}.")
        pyautogui.dragTo(end_drag.x, end_drag.y, duration=MOVE_SPEED * start_drag.distance_between(end_drag))
