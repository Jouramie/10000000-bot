import abc
from dataclasses import dataclass
from enum import Enum, auto
from functools import reduce
from typing import Set, Dict, Tuple

from frozendict import FrozenOrderedDict, frozendict

from src.domain.item import Item, ItemType
from src.domain.screen import ScreenSquare, Point
from src.domain.tile import TileType, Tile, Cluster


class ObjectiveType(Enum):
    ZOMBIE = auto()
    SKELETON = auto()
    SKELETON_ARCHER = auto()
    T_REX = auto()
    FALLEN_SOLDIER = auto()
    WHITE_DRAGON = auto()
    FIRE_ELEMENTAL = auto()
    WATER_ELEMENTAL = auto()
    RED_DRAGON = auto()
    GOLEM = auto()
    NINJA = auto()
    REPTILIAN = auto()
    TREANT = auto()
    DEMON = auto()
    GHOST = auto()
    DOGGO = auto()
    CHEST = auto()
    DOOR = auto()
    # DOOR2 = auto()

    def __str__(self):
        return self.name


GENERIC_MONSTER_TILE_VALUES = {
    TileType.SWORD: 3,
    TileType.WAND: 3,
    TileType.SHIELD: 2,
    TileType.LOGS: 1,
    TileType.CHEST: 1,
    TileType.ROCKS: 1,
    TileType.KEY: -1,
}

SWORD_RESISTANT_MONSTER_TILE_VALUES = {
    TileType.WAND: 4,
    TileType.SWORD: 2,
    TileType.SHIELD: 2,
    TileType.LOGS: 1,
    TileType.CHEST: 1,
    TileType.ROCKS: 1,
    TileType.KEY: -0.5,
}

WAND_RESISTANT_MONSTER_TILE_VALUES = {
    TileType.SWORD: 4,
    TileType.WAND: 2,
    TileType.SHIELD: 2,
    TileType.LOGS: 1,
    TileType.CHEST: 1,
    TileType.ROCKS: 1,
    TileType.KEY: -0.5,
}


GENERIC_KEY_TILE_VALUES = {
    TileType.KEY: 3,
    TileType.SHIELD: 2,
    TileType.LOGS: 1,
    TileType.CHEST: 1,
    TileType.ROCKS: 1,
    TileType.SWORD: -0.5,
    TileType.WAND: -0.5,
}

NO_OBJECTIVE_TILE_VALUES = {
    TileType.SHIELD: 2,
    TileType.LOGS: 1,
    TileType.CHEST: 1,
    TileType.ROCKS: 1,
    TileType.SWORD: -0.5,
    TileType.WAND: -0.5,
    TileType.KEY: -0.5,
}

TILE_VALUES_PER_OBJECTIVE_TYPES = {
    ObjectiveType.ZOMBIE: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.SKELETON: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.SKELETON_ARCHER: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.T_REX: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.FALLEN_SOLDIER: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.WHITE_DRAGON: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.FIRE_ELEMENTAL: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.WATER_ELEMENTAL: WAND_RESISTANT_MONSTER_TILE_VALUES,
    ObjectiveType.RED_DRAGON: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.GOLEM: SWORD_RESISTANT_MONSTER_TILE_VALUES,
    ObjectiveType.NINJA: WAND_RESISTANT_MONSTER_TILE_VALUES,
    ObjectiveType.REPTILIAN: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.TREANT: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.DEMON: SWORD_RESISTANT_MONSTER_TILE_VALUES,
    ObjectiveType.GHOST: SWORD_RESISTANT_MONSTER_TILE_VALUES,
    ObjectiveType.DOGGO: WAND_RESISTANT_MONSTER_TILE_VALUES,
    ObjectiveType.CHEST: GENERIC_KEY_TILE_VALUES,
    ObjectiveType.DOOR: GENERIC_KEY_TILE_VALUES,
}

ITEM_FLAT_IMPACT = {
    ItemType.LOG_TO_KEY_SCROLL: frozendict(
        {
            TileType.KEY: 10,
        }
    ),
    ItemType.LOG_TO_SWORD_SCROLL: frozendict(
        {
            TileType.SWORD: 10,
        }
    ),
    ItemType.LOG_TO_WAND_SCROLL: frozendict(
        {
            TileType.WAND: 10,
        }
    ),
    ItemType.ROCK_TO_KEY_SCROLL: frozendict(
        {
            TileType.KEY: 10,
        }
    ),
    ItemType.ROCK_TO_SWORD_SCROLL: frozendict(
        {
            TileType.SWORD: 10,
        }
    ),
    ItemType.ROCK_TO_WAND_SCROLL: frozendict(
        {
            TileType.WAND: 10,
        }
    ),
    ItemType.KEY: frozendict(
        {
            TileType.KEY: 6,
        }
    ),
    ItemType.AXE: frozendict(
        {
            TileType.SWORD: 10,
        }
    ),
    ItemType.BATTLEAXE: frozendict(
        {
            TileType.SWORD: 10,
        }
    ),
    ItemType.HALBERD: frozendict(
        {
            TileType.SWORD: 15,
        }
    ),
    ItemType.RED_ORB: frozendict(
        {
            TileType.WAND: 10,
        }
    ),
    ItemType.YELLOW_ORB: frozendict(
        {
            TileType.WAND: 10,
        }
    ),
    ItemType.GREEN_ORB: frozendict(
        {
            TileType.WAND: 10,
        }
    ),
    ItemType.PURPLE_ORB: frozendict(
        {
            TileType.WAND: 15,
        }
    ),
    ItemType.BREAD: frozendict(
        {
            TileType.SHIELD: 10,
        }
    ),
    ItemType.CHEESE: frozendict(
        {
            TileType.SHIELD: 10,
        }
    ),
    ItemType.COFFEE: frozendict(
        {
            TileType.SHIELD: 10,
        }
    ),
}


@dataclass(frozen=True)
class Move(metaclass=abc.ABCMeta):
    impact: FrozenOrderedDict[TileType, int]

    @abc.abstractmethod
    def calculate_mouse_movement(self) -> int:
        raise NotImplementedError

    def calculate_score(self, value_per_tile_type: Dict[TileType, int]) -> int:
        return reduce(
            lambda x, y: x + y,
            [self.impact[tile_type] * value_per_tile_type.get(tile_type, 0) for tile_type in self.impact],
            0,
        )


@dataclass(frozen=True)
class TileMove(Move):
    cluster: Cluster
    tile_to_move: Tile
    grid_destination: Point

    def __str__(self):
        return f"move {str(self.tile_to_move)} -> {str(self.grid_destination)} for { {str(tile_type):impact for tile_type, impact in self.impact.items()}}"

    def get_combo_type(self) -> TileType:
        return self.tile_to_move.type

    def calculate_mouse_movement(self) -> int:
        return self.tile_to_move.grid_position.distance_between(self.grid_destination)


@dataclass(frozen=True)
class ItemMove(Move):
    item: Item

    def __str__(self):
        return f"use {str(self.item)}"

    def calculate_mouse_movement(self) -> int:
        return 0


def create_item_move(item: Item, impact: FrozenOrderedDict[TileType, int] | None = None) -> ItemMove:
    return ItemMove(impact if impact is not None else ITEM_FLAT_IMPACT.get(item.type, frozendict()), item)


@dataclass(frozen=True)
class Objective:
    type: ObjectiveType = None
    screen_square: ScreenSquare = ScreenSquare()

    def select_best_move(self, possible_moves: Set[TileMove]) -> Tuple[TileMove, int] | None:
        value_per_tile_type = TILE_VALUES_PER_OBJECTIVE_TYPES.get(self.type, NO_OBJECTIVE_TILE_VALUES)

        best_move = max(possible_moves, key=lambda x: (x.calculate_score(value_per_tile_type), -x.calculate_mouse_movement()))
        score = best_move.calculate_score(value_per_tile_type)

        if score <= 0:
            return None

        return best_move, score if score > 0 else None
