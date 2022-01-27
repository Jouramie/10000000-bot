import logging
from functools import reduce
from typing import List

import pyautogui
import pyscreeze
import win32gui

from src.domain.game_state import GameState, GameStateDetector
from src.domain.move import TileMover, Move
from src.domain.objective import Objective, ObjectiveType, create_objective
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
    TileType.STAR: "assets/tiles/star.png",
}

TILE_DIMENSION = 84

OBJETIVE_ASSETS = {
    ObjectiveType.ZOMBIE: "assets/objectives/zombie.png",
    ObjectiveType.SKELETON: "assets/objectives/skeleton.png",
    ObjectiveType.SKELETON_ARCHER: "assets/objectives/skeleton-archer.png",
    ObjectiveType.FALLEN_SOLDIER: "assets/objectives/fallen-soldier.png",
    ObjectiveType.WHITE_DRAGON: "assets/objectives/white-dragon.png",
    ObjectiveType.FIRE_ELEMENTAL: "assets/objectives/fire-elemental.png",
    ObjectiveType.CHEST: "assets/objectives/chest2.png",
    ObjectiveType.DOOR: "assets/objectives/door.png",
}


GRID_SIZE_X = 8
GRID_SIZE_Y = 7
GRID_SIZE = Point(GRID_SIZE_X, GRID_SIZE_Y)


MOUSE_MOVEMENT_SPEED = 1 / 600

REAL_WINDOW_TITLE = "10000000"
TESTING_WINDOW_TITLE = "e.png - Greenshot image editor"
GAME_WINDOW_TITLE = REAL_WINDOW_TITLE


def activate_window(title):
    possible_game_windows = pyautogui.getWindowsWithTitle(title)
    matching_windows = [window for window in possible_game_windows if window.title == title]
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

    possible_game_windows = [win.title for win in pyautogui.getWindowsWithTitle(title)]
    logger.debug(f"Found {len(possible_game_windows)} possible game windows: {possible_game_windows}.")

    window_handle = win32gui.FindWindow(None, title)
    win_region = win32gui.GetWindowRect(window_handle)

    return win_region[0], win_region[1], win_region[2] - win_region[0], win_region[3] - win_region[1]


# FIXME we should not take a screenshot for each tile type
def locate_all_on_window(needle_image, window_title, **kwargs) -> List[pyscreeze.Box]:
    region = find_window_region(window_title)
    if region[0] < 0:
        return []
    window_screenshot = pyautogui.screenshot(region=region)
    # window_screenshot.show()

    logger.debug(f"Game window located at {region}.")
    return [
        pyscreeze.Box(box.left + region[0], box.top + region[1], box.width, box.height)
        for box in pyautogui.locateAll(needle_image, window_screenshot, **kwargs)
    ]


def find_grid() -> Grid:
    """Should detect 8x7 56 tiles."""

    # TODO lower confidence and undupe images
    prospect_tiles = [
        (tile_type, ScreenSquare(tile.left, tile.top, tile.height, tile.width))
        for tile_type, asset in TILE_ASSETS.items()
        for tile in locate_all_on_window(asset, GAME_WINDOW_TITLE, grayscale=True)
    ]

    if not prospect_tiles:
        logger.warning(f"No tiles found. Returning InconsistentGrid")
        return InconsistentGrid([], GRID_SIZE)

    min_left = min([tile[1].left for tile in prospect_tiles])
    min_top = min([tile[1].top for tile in prospect_tiles])

    tiles = []
    for tile in prospect_tiles:
        screen_square = tile[1]
        grid_position = Point(round((screen_square.left - min_left) / TILE_DIMENSION), round((screen_square.top - min_top) / TILE_DIMENSION))

        # TODO instead of ignoring the tile, it should be recalculated (only between the found possibilities to speed up)
        if grid_position not in {t.grid_position for t in tiles}:
            tiles.append(Tile(tile[0], screen_square, grid_position))

    tiles = sorted(tiles, key=lambda tile: tile.grid_position)

    size_x = len({tile.grid_position.x for tile in tiles})
    size_y = len({tile.grid_position.y for tile in tiles})
    if size_x != GRID_SIZE_X or size_y != GRID_SIZE_Y:
        logger.warning(f"Detected grid is {size_x} / {size_y}. Expected grid should be {GRID_SIZE_X} / {GRID_SIZE_Y}. Returning InconsistentGrid")
        return InconsistentGrid(tiles, GRID_SIZE)

    return Grid(tiles, GRID_SIZE)


def find_objective() -> Objective:
    objectives = [
        create_objective(objective_assets, ScreenSquare(square.left, square.top, square.height, square.width))
        for objective_assets, asset in OBJETIVE_ASSETS.items()
        for square in locate_all_on_window(asset, GAME_WINDOW_TITLE, grayscale=True, confidence=0.85)
    ]

    if not objectives:
        return create_objective()

    logger.info(f"Found objectives {objectives}.")
    return sorted(objectives, key=lambda x: x.screen_square.left)[0]


class PyAutoGuiGameStateDetector(GameStateDetector):
    def __init__(self) -> None:
        super().__init__()

    def detect_game_state(self) -> GameState:
        game_state = GameState(grid=find_grid(), objective=find_objective())
        logger.debug(f"Found {len(game_state.grid)} tiles.")

        return game_state


class PyAutoGuiTileMover(TileMover):
    def execute(self, move: Move):
        logger.info(
            f"Completing cluster {move.get_combo_type()} "
            + reduce(lambda x, y: x + y, (f"({tile.grid_position.x}, {tile.grid_position.y}) " for tile in move.cluster.tiles))
            + f"with ({move.tile_to_move.grid_position.x}, {move.tile_to_move.grid_position.y}). "
            f"moving to ({move.grid_destination.x}, {move.grid_destination.y})"
        )

        start_drag = move.tile_to_move.screen_square.find_center()
        end_drag = move.calculate_screen_destination()

        logger.debug(f"Starting drag from {start_drag}.")
        pyautogui.moveTo(start_drag.x, start_drag.y, duration=0.2)
        logger.debug(f"Ending drag to {end_drag}.")
        pyautogui.dragTo(end_drag.x, end_drag.y, duration=MOUSE_MOVEMENT_SPEED * start_drag.distance_between(end_drag))


if __name__ == "__main__":
    logging.basicConfig()
    print(find_objective())
