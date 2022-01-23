import pyautogui

from copy import deepcopy
from typing import List


def find_tiles():
    return [
        [tile.left, tile.top, tile.width, tile.height]
        for tile in pyautogui.locateAllOnScreen("assets/tiles/sword.png")
    ]


class GameState:
    def __init__(self) -> None:
        self.tiles: List[List[int]] = []

    def __str__(self) -> str:
        return f"Tiles{{{str(self.tiles)}}}"


class FetchGameState:
    def __init__(self) -> None:
        self.game_state = GameState()

    def execute(self) -> GameState:
        self.game_state.tiles = find_tiles()
        return deepcopy(self.game_state)
