from enum import Enum, auto


class TileType(Enum):
    CHEST = auto()
    KEY = auto()
    LOGS = auto()
    ROCKS = auto()
    SHIELD = auto()
    SWORD = auto()
    WAND = auto()


class Tile:
    def __init__(
        self, tile_type: TileType, left: int, top: int, height: int, width: int
    ) -> None:
        self.tile_type = tile_type
        self.left = left
        self.top = top
        self.height = height
        self.width = width

    def __str__(self):
        return (
            f"Tile{{type: {self.tile_type}, "
            f"left: {self.left}, top: {self.top}, height: {self.height}, width: {self.width} }}"
        )
