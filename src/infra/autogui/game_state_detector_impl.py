import logging

import pyautogui

from src.domain.game_state import GameState, GameStateDetector
from src.domain.tile import TileType, Tile

logger = logging.getLogger(__name__)

TILE_ASSETS = {
    TileType.CHEST: "assets/tiles/chest.png",
    TileType.KEY: "assets/tiles/key.png",
    TileType.LOGS: "assets/tiles/logs.png",
    TileType.ROCKS: "assets/tiles/rocks.png",
    TileType.SHIELD: "assets/tiles/shield.png",
    TileType.SWORD: "assets/tiles/sword.png",
    TileType.WAND: "assets/tiles/wand.png",
}


def find_tiles():
    return [
        Tile(tile_type, tile.left, tile.top, tile.height, tile.width) for tile_type, asset in TILE_ASSETS.items() for tile in pyautogui.locateAllOnScreen(asset)
    ]


class AutoGuiGameStateDetector(GameStateDetector):
    def __init__(self) -> None:
        super().__init__()

    def detect_game_state(self) -> GameState:
        logger.debug("Finding tiles.")
        game_state = GameState(tiles=find_tiles())
        logger.debug(f"Found {len(game_state.tiles)} tiles.")

        return game_state
