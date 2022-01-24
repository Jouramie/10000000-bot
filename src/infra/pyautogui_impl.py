import logging

import pyautogui

from src.domain.game_state import GameState, GameStateDetector
from src.domain.move import TileMover, Move
from src.domain.tile import TileType, Tile, ScreenSquare, GridPosition, Grid

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
        logger.warning(f"{len(tiles)} tiles detected. Expected 56. Returning 0 tiles.")

    return Grid(
        [Tile(*tile) for tile in [(*tiles[i + j * GRID_SIZE_X], GridPosition(i, j)) for j in range(0, GRID_SIZE_Y) for i in range(0, GRID_SIZE_X)]],
        GridPosition(GRID_SIZE_X, GRID_SIZE_Y),
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
        logger.debug(f"Moving tile {move.tile_to_move.grid_position} to {move.destination}.")
