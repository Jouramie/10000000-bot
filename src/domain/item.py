from dataclasses import dataclass
from enum import Enum, auto

from src.domain.screen import ScreenSquare


class ItemType(Enum):
    LOG_TO_WAND_SCROLL = auto()
    LOG_TO_SWORD_SCROLL = auto()
    LOG_TO_KEY_SCROLL = auto()
    ROCK_TO_WAND_SCROLL = auto()
    ROCK_TO_SWORD_SCROLL = auto()
    ROCK_TO_KEY_SCROLL = auto()
    KEY = auto()
    AXE = auto()
    BATTLEAXE = auto()
    HALBERD = auto()
    BREAD = auto()
    CHEESE = auto()
    COFFEE = auto()
    RED_ORB = auto()
    YELLOW_ORB = auto()
    GREEN_ORB = auto()
    PURPLE_ORB = auto()

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Item:
    type: ItemType
    screen_square: ScreenSquare

    def __str__(self):
        return str(self.type)
