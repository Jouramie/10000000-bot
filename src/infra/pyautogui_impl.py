import logging

import pyautogui

from src.domain.game_state import GameState, GameStateDetector
from src.domain.move import TileMover, Move
from src.domain.tile import TileType, Tile, ScreenSquare, Point, Grid, InconsistentGrid

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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


def find_grid() -> Grid:
    """Should detect 8x7 56 tiles."""

    tiles = sorted(
        [
            (tile_type, ScreenSquare(tile.left, tile.top, tile.height, tile.width))
            for tile_type, asset in TILE_ASSETS.items()
            for tile in pyautogui.locateAllOnScreen(asset)
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
            f"Completing {move.get_combo_type()} "
            f"({move.pair[0].grid_position.x}, {move.pair[0].grid_position.y}) "
            f"({move.pair[1].grid_position.x}, {move.pair[1].grid_position.y}) "
            f"with ({move.tile_to_move.grid_position.x}, {move.tile_to_move.grid_position.y}). "
            f"moving to ({move.grid_destination.x}, {move.grid_destination.y})"
        )

        start_drag = move.tile_to_move.screen_square.find_center()
        end_drag = move.calculate_screen_destination()

        logger.debug(f"Starting drag from {start_drag}.")
        pyautogui.moveTo(start_drag.x, start_drag.y, duration=0.2)
        logger.debug(f"Ending drag to {end_drag}.")
        pyautogui.dragTo(end_drag.x, end_drag.y, duration=MOVE_SPEED * start_drag.distance_between(end_drag))
