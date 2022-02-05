import logging
import os
import re
from datetime import datetime
from functools import reduce, singledispatch
from pathlib import Path
from typing import List, Tuple, FrozenSet

import pyautogui
import pyscreeze
import win32gui
from PIL.Image import Image

from src import properties
from src.domain.game_state import GameState
from src.domain.grid import Grid, InconsistentGrid, EmptyGrid
from src.domain.item import Item, ItemType
from src.domain.objective import Objective, ObjectiveType, TileMove, ItemMove, Move
from src.domain.screen import ScreenSquare, Point
from src.domain.tile import TileType, Tile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GRID_BOX = (300, 180, 1200, 800)
ITEMS_BOX = (20, 60, 290, 330)
OBJECTIVES_BOX = (300, 50, 1200, 190)


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

TILE_DIMENSION = 86

OBJETIVE_ASSETS = {
    ObjectiveType.ZOMBIE: "assets/objectives/zombie2.png",
    ObjectiveType.SKELETON: "assets/objectives/skeleton.png",
    ObjectiveType.SKELETON_ARCHER: "assets/objectives/skeleton-archer.png",
    ObjectiveType.T_REX: "assets/objectives/t-rex2.png",
    ObjectiveType.FALLEN_SOLDIER: "assets/objectives/fallen-soldier2.png",
    ObjectiveType.WHITE_DRAGON: "assets/objectives/white-dragon.png",
    ObjectiveType.FIRE_ELEMENTAL: "assets/objectives/fire-elemental.png",
    ObjectiveType.WATER_ELEMENTAL: "assets/objectives/water-elemental2.png",
    ObjectiveType.RED_DRAGON: "assets/objectives/red-dragon2.png",
    ObjectiveType.GOLEM: "assets/objectives/golem2.png",
    ObjectiveType.NINJA: "assets/objectives/ninja2.png",
    ObjectiveType.REPTILIAN: "assets/objectives/reptilian2.png",
    ObjectiveType.TREANT: "assets/objectives/treant2.png",
    ObjectiveType.DEMON: "assets/objectives/demon2.png",
    ObjectiveType.GHOST: "assets/objectives/ghost2.png",
    ObjectiveType.DOGGO: "assets/objectives/doggo2.png",
    ObjectiveType.BEAR: "assets/objectives/bear2.png",
    ObjectiveType.BLACK_DRAGON: "assets/objectives/black-dragon2.png",
    ObjectiveType.EARTH_ELEMENTAL: "assets/objectives/earth-elemental2.png",
    ObjectiveType.DARK_ELF: "assets/objectives/dark-elf2.png",
    ObjectiveType.CHEST: "assets/objectives/chest2.png",
    ObjectiveType.DOOR: "assets/objectives/door2.png",
}

ITEM_ASSETS = {
    ItemType.LOG_TO_KEY_SCROLL: "assets/items/log-to-key-scroll.png",
    ItemType.LOG_TO_WAND_SCROLL: "assets/items/log-to-wand-scroll.png",
    ItemType.LOG_TO_SWORD_SCROLL: "assets/items/log-to-sword-scroll.png",
    ItemType.ROCK_TO_KEY_SCROLL: "assets/items/rock-to-key-scroll.png",
    ItemType.ROCK_TO_WAND_SCROLL: "assets/items/rock-to-wand-scroll.png",
    ItemType.ROCK_TO_SWORD_SCROLL: "assets/items/rock-to-sword-scroll.png",
    ItemType.KEY: "assets/items/key.png",
    ItemType.AXE: "assets/items/axe.png",
    ItemType.BATTLEAXE: "assets/items/battleaxe.png",
    ItemType.HALBERD: "assets/items/halberd.png",
    ItemType.GREAT_AXE: "assets/items/great-axe.png",
    ItemType.BREAD: "assets/items/bread.png",
    ItemType.CHEESE: "assets/items/cheese.png",
    ItemType.COFFEE: "assets/items/coffee.png",
    ItemType.HAM: "assets/items/ham.png",
    ItemType.PIE: "assets/items/pie.png",
    ItemType.RED_ORB: "assets/items/red-orb.png",
    ItemType.YELLOW_ORB: "assets/items/yellow-orb.png",
    ItemType.GREEN_ORB: "assets/items/green-orb.png",
    ItemType.PURPLE_ORB: "assets/items/purple-orb.png",
    ItemType.BLUE_ORB: "assets/items/blue-orb.png",
}

GRID_SIZE_X = 8
GRID_SIZE_Y = 7
GRID_SIZE = Point(GRID_SIZE_X, GRID_SIZE_Y)


SECONDS_PER_TILE_DISTANCE = {
    1: 0.11,
    2: 0.25,
    3: 0.37,
    4: 0.48,
    5: 0.50,
    6: 0.50,
    7: 0.50,
    8: 0.50,
}

REAL_WINDOW_TITLE = "10000000"
TESTING_WINDOW_TITLE = "Visionneuse de photos Windows"
EXCLUDED_WINDOWS_PATTERN = {r"10000000 - .+\.py"}
GAME_WINDOW_TITLE = REAL_WINDOW_TITLE


_grid_left = 0
_grid_top = 0


def screen_to_grid(screen_square: ScreenSquare | pyscreeze.Box) -> Point:
    return Point(round((screen_square.left - _grid_left) / TILE_DIMENSION), round((screen_square.top - _grid_top) / TILE_DIMENSION))


def grid_to_screen(point: Point) -> ScreenSquare:
    return ScreenSquare(_grid_left + point.x * TILE_DIMENSION, _grid_top + point.y * TILE_DIMENSION, TILE_DIMENSION, TILE_DIMENSION)


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

    possible_game_windows = [window.title for window in pyautogui.getWindowsWithTitle(title)]
    logger.info(f"Found {len(possible_game_windows)} possible game windows: {possible_game_windows}.")

    actual_game_window = title if title in possible_game_windows else possible_game_windows[0]
    if True in {re.match(pattern, actual_game_window) for pattern in EXCLUDED_WINDOWS_PATTERN}:
        return None

    try:
        window_handle = win32gui.FindWindow(None, actual_game_window)
        win_region = win32gui.GetWindowRect(window_handle)
    except Exception as e:
        return None

    return pyscreeze.Box(win_region[0], win_region[1], win_region[2] - win_region[0], win_region[3] - win_region[1])


def screenshot_window(window_title: str) -> Tuple[pyscreeze.Box, Image] | None:
    region = find_window_region(window_title)
    if region is None or region.left < 0:
        return None

    logger.debug(f"Game window located at {region}.")
    screenshot = pyautogui.screenshot(region=region)
    logger.debug(f"Screenshot size is {screenshot.size}.")
    # screenshot.show()
    return region, screenshot


def locate_all_on_window(needle_image, offset: Point, screenshot: Image, **kwargs) -> List[pyscreeze.Box]:
    return [pyscreeze.Box(box.left + offset.x, box.top + offset.y, box.width, box.height) for box in pyautogui.locateAll(needle_image, screenshot, **kwargs)]


def locate_on_window(needle_image, offset: Point, screenshot: Image, **kwargs) -> pyscreeze.Box:
    box = pyautogui.locate(needle_image, screenshot, **kwargs)
    return pyscreeze.Box(box.left + offset.x, box.top + offset.y, box.width, box.height) if box is not None else None


def find_grid(offset: Point, screenshot: Image) -> Grid:
    """Should detect 8x7 56 tiles."""
    # TODO lower confidence and undupe images
    prospect_tiles = [
        (tile_type, ScreenSquare(tile.left, tile.top, tile.height, tile.width))
        for tile_type, asset in TILE_ASSETS.items()
        for tile in locate_all_on_window(asset, Point(offset.x + GRID_BOX[0], offset.y + GRID_BOX[1]), screenshot.crop(GRID_BOX), grayscale=True)
    ]

    if not prospect_tiles:
        logger.warning(f"No tiles found. Returning EmptyGrid.")
        return EmptyGrid()

    global _grid_left
    global _grid_top

    _grid_left = min(tile[1].left for tile in prospect_tiles)
    _grid_top = min(tile[1].top for tile in prospect_tiles)

    tiles = []
    for tile in prospect_tiles:
        screen_square = tile[1]
        grid_position = screen_to_grid(screen_square)

        # TODO instead of ignoring the tile, it should be recalculated (only between the found possibilities to speed up)
        if grid_position not in {t.grid_position for t in tiles}:
            tiles.append(Tile(tile[0], grid_position))

    tiles = sorted(tiles, key=lambda tile: tile.grid_position)

    size_x = max(tile.grid_position.x for tile in tiles) + 1
    size_y = max(tile.grid_position.y for tile in tiles) + 1
    grid = InconsistentGrid(tiles, Point(size_x, size_y))
    if size_x != GRID_SIZE_X or size_y != GRID_SIZE_Y:
        logger.warning(f"Detected grid is {size_x} / {size_y}. Expected grid should be {GRID_SIZE_X} / {GRID_SIZE_Y}. Returning InconsistentGrid")
        return grid

    return grid


def find_objective(offset: Point, screenshot: Image) -> Objective:
    objectives = []
    logger.debug(f"Looking for objectives.")

    for objective_assets, asset in OBJETIVE_ASSETS.items():
        square = locate_on_window(
            asset, Point(offset.x + OBJECTIVES_BOX[0], offset.y + OBJECTIVES_BOX[1]), screenshot.crop(OBJECTIVES_BOX), grayscale=True, confidence=0.85
        )
        if square is not None:
            objectives.append(Objective(objective_assets, ScreenSquare(square.left, square.top, square.height, square.width)))

    if not objectives:
        return Objective()

    logger.debug(f"Found objectives {objectives}.")
    return sorted(objectives, key=lambda x: x.screen_square.left)[0]


def find_items(offset: Point, screenshot: Image) -> FrozenSet[Item]:
    items = []
    logger.debug(f"Looking for items.")

    for item_assets, asset in ITEM_ASSETS.items():
        square = locate_on_window(asset, Point(offset.x + ITEMS_BOX[0], offset.y + ITEMS_BOX[1]), screenshot.crop(ITEMS_BOX), grayscale=True)
        if square is not None:
            items.append(Item(item_assets, ScreenSquare(square.left, square.top, square.height, square.width)))

    logger.info(f"Found items {[str(item) for item in items]}.")
    return frozenset(items)


def log_screenshot(screenshot: Image):
    logs_folder = Path("logs")
    if not logs_folder.exists():
        logs_folder.mkdir()
    screenshot.save(Path(f"logs/{datetime.now().replace().isoformat().replace(':', '')}.tiff"))

    saved_screenshots = os.listdir("logs")

    if len(saved_screenshots) > properties.SAVED_SCREENSHOT_QUANTITY:
        os.remove(Path(f"logs/{sorted(saved_screenshots)[0]}"))


def detect_game_state() -> GameState:
    packed_screenshot = screenshot_window(GAME_WINDOW_TITLE)
    if packed_screenshot is None:
        return GameState(EmptyGrid(), Objective(), frozenset())

    region, screenshot = packed_screenshot
    offset = Point(region.left, region.top)
    found_grid = find_grid(offset, screenshot)

    if len(found_grid) > 16 and GAME_WINDOW_TITLE == REAL_WINDOW_TITLE and properties.SCREENSHOT_LOGGING_ENABLED:
        log_screenshot(screenshot)

    return GameState(found_grid, find_objective(offset, screenshot), find_items(offset, screenshot))


@singledispatch
def do_move(move: Move) -> float:
    raise NotImplementedError(f"No implementation for {type(move)}")


@do_move.register
def _(move: TileMove) -> float:
    if move.calculate_grid_distance() == 0:
        return 0

    logger.info(
        f"Completing cluster {move.get_combo_type()} "
        + reduce(lambda x, y: x + y, (f"({tile.grid_position.x}, {tile.grid_position.y}) " for tile in move.cluster.tiles))
        + f"with ({move.tile_to_move.grid_position.x}, {move.tile_to_move.grid_position.y}). "
        f"moving to ({move.grid_destination.x}, {move.grid_destination.y}) for expected impact " + str(dict(move.impact))
    )

    shift = move.calculate_shift()
    start_drag = grid_to_screen(shift[0]).find_center()
    end_drag = grid_to_screen(shift[1]).find_center()

    logger.debug(f"Starting drag from {start_drag}.")
    pyautogui.moveTo(start_drag.x, start_drag.y)
    logger.debug(f"Ending drag to {end_drag}.")
    grid_distance = move.calculate_shift_distance()
    pyautogui.dragTo(end_drag.x, end_drag.y, duration=SECONDS_PER_TILE_DISTANCE[grid_distance])

    return 0.5


@do_move.register
def _(move: ItemMove) -> float:
    logger.info(f"Using item {move.item.type}.")
    click_point = move.item.screen_square.find_center()
    pyautogui.click(click_point.x, click_point.y)

    return 0
