import logging
from functools import reduce
from typing import List, Tuple, FrozenSet

import pyautogui
import pyscreeze
import pywintypes
import win32gui
from PIL.Image import Image

from src.domain.grid import Grid, InconsistentGrid
from src.domain.item import Item, ItemType
from src.domain.objective import Objective, ObjectiveType, Move, TileMove, ItemMove
from src.domain.screen import ScreenSquare, Point
from src.domain.tile import TileType, Tile

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
    ObjectiveType.ZOMBIE: "assets/objectives/zombie2.png",
    ObjectiveType.SKELETON: "assets/objectives/skeleton.png",
    ObjectiveType.SKELETON_ARCHER: "assets/objectives/skeleton-archer.png",
    ObjectiveType.T_REX: "assets/objectives/t-rex.png",
    ObjectiveType.FALLEN_SOLDIER: "assets/objectives/fallen-soldier2.png",
    ObjectiveType.WHITE_DRAGON: "assets/objectives/white-dragon.png",
    ObjectiveType.FIRE_ELEMENTAL: "assets/objectives/fire-elemental.png",
    ObjectiveType.WATER_ELEMENTAL: "assets/objectives/water-elemental2.png",
    ObjectiveType.RED_DRAGON: "assets/objectives/red-dragon2.png",
    ObjectiveType.GOLEM: "assets/objectives/golem.png",
    ObjectiveType.NINJA: "assets/objectives/ninja2.png",
    ObjectiveType.CHEST: "assets/objectives/chest2.png",
    ObjectiveType.DOOR: "assets/objectives/door2.png",
}

ITEM_ASSETS = {
    ItemType.LOG_TO_KEY_SCROLL: "assets/items/log-to-key-scroll.png",
    ItemType.LOG_TO_WAND_SCROLL: "assets/items/log-to-wand-scroll.png",
    ItemType.KEY: "assets/items/key.png",
    ItemType.AXE: "assets/items/axe.png",
    ItemType.BREAD: "assets/items/bread.png",
    ItemType.CHEESE: "assets/items/bread.png",
    ItemType.RED_ORB: "assets/items/red-orb.png",
    ItemType.YELLOW_ORB: "assets/items/yellow-orb.png",
}


GRID_SIZE_X = 8
GRID_SIZE_Y = 7
GRID_SIZE = Point(GRID_SIZE_X, GRID_SIZE_Y)


MOUSE_MOVEMENT_SPEED = 1 / 600

REAL_WINDOW_TITLE = "10000000"
TESTING_WINDOW_TITLE = "ninja-mid-combo.png - Greenshot image editor"
GAME_WINDOW_TITLE = TESTING_WINDOW_TITLE


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


def find_window_region(title) -> pyscreeze.Box | None:
    # activate_window(title)

    possible_game_windows = [win.title for win in pyautogui.getWindowsWithTitle(title)]
    logger.debug(f"Found {len(possible_game_windows)} possible game windows: {possible_game_windows}.")

    window_handle = win32gui.FindWindow(None, title)
    try:
        win_region = win32gui.GetWindowRect(window_handle)
    except pywintypes.error as e:
        return None

    return pyscreeze.Box(win_region[0], win_region[1], win_region[2] - win_region[0], win_region[3] - win_region[1])


def screenshot_window(window_title: str) -> Tuple[pyscreeze.Box, Image] | None:
    region = find_window_region(window_title)
    if region is None or region.left < 0:
        return None

    logger.debug(f"Game window located at {region}.")
    screenshot = pyautogui.screenshot(region=region)
    # screenshot.show()
    return region, screenshot


def locate_all_on_window(needle_image, region: pyscreeze.Box, screenshot: Image, **kwargs) -> List[pyscreeze.Box]:
    return [
        pyscreeze.Box(box.left + region.left, box.top + region.top, box.width, box.height) for box in pyautogui.locateAll(needle_image, screenshot, **kwargs)
    ]


def find_grid() -> Grid:
    """Should detect 8x7 56 tiles."""
    packed_screenshot = screenshot_window(GAME_WINDOW_TITLE)

    if packed_screenshot is None:
        return InconsistentGrid([], GRID_SIZE)

    region, screenshot = packed_screenshot

    # TODO lower confidence and undupe images
    prospect_tiles = [
        (tile_type, ScreenSquare(tile.left, tile.top, tile.height, tile.width))
        for tile_type, asset in TILE_ASSETS.items()
        for tile in locate_all_on_window(asset, region, screenshot, grayscale=True)
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

    # FIXME there should be a better approximation... meh what ever

    for y in range(0, GRID_SIZE_Y):
        for x in range(0, GRID_SIZE_X):
            index = x + y * GRID_SIZE_X
            expected_grid_position = Point(x, y)
            if len(tiles) <= index or tiles[index].grid_position != expected_grid_position:
                tiles.insert(index, Tile(TileType.UNKNOWN, None, expected_grid_position))

    return Grid(tiles, GRID_SIZE)


def find_objective() -> Objective:
    region, screenshot = screenshot_window(GAME_WINDOW_TITLE)

    objectives = [
        Objective(objective_assets, ScreenSquare(square.left, square.top, square.height, square.width))
        for objective_assets, asset in OBJETIVE_ASSETS.items()
        for square in locate_all_on_window(asset, region, screenshot, grayscale=True, confidence=0.85)
    ]

    if not objectives:
        return Objective()

    logger.debug(f"Found objectives {objectives}.")
    return sorted(objectives, key=lambda x: x.screen_square.left)[0]


def find_items() -> FrozenSet[Item]:
    region, screenshot = screenshot_window(GAME_WINDOW_TITLE)

    items = {
        Item(objective_assets, ScreenSquare(square.left, square.top, square.height, square.width))
        for objective_assets, asset in ITEM_ASSETS.items()
        for square in locate_all_on_window(asset, region, screenshot, grayscale=True)
    }

    logger.info(f"Found items {items}.")
    return frozenset(items)


def detect_game_state() -> Tuple[Grid, Objective, FrozenSet[Item]]:
    return find_grid(), find_objective(), find_items()


def do_move(move: Move):
    if isinstance(move, TileMove):
        logger.info(
            f"Completing cluster {move.get_combo_type()} "
            + reduce(lambda x, y: x + y, (f"({tile.grid_position.x}, {tile.grid_position.y}) " for tile in move.cluster.tiles))
            + f"with ({move.tile_to_move.grid_position.x}, {move.tile_to_move.grid_position.y}). "
            f"moving to ({move.grid_destination.x}, {move.grid_destination.y}) for expected impact " + str(dict(move.impact))
        )
    elif isinstance(move, ItemMove):
        logger.info(f"Using item {move.item.type}.")

    mouse_movement = move.calculate_mouse_movement()

    if len(mouse_movement) == 2:
        start_drag = mouse_movement[0]
        end_drag = mouse_movement[1]

        logger.debug(f"Starting drag from {start_drag}.")
        pyautogui.moveTo(start_drag.x, start_drag.y, duration=0.2)
        logger.debug(f"Ending drag to {end_drag}.")
        pyautogui.dragTo(end_drag.x, end_drag.y, duration=MOUSE_MOVEMENT_SPEED * start_drag.distance_between(end_drag))

    else:
        click_point = move.item.screen_square.find_center()

        pyautogui.click(click_point.x, click_point.y)


if __name__ == "__main__":
    logging.basicConfig()
    print(find_objective())
