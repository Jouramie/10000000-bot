import abc
from dataclasses import dataclass
from enum import Enum, auto
from functools import reduce
from typing import Set, Dict, List, Tuple

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
    TileType.KEY: -1,
}

WAND_RESISTANT_MONSTER_TILE_VALUES = {
    TileType.SWORD: 4,
    TileType.WAND: 2,
    TileType.SHIELD: 2,
    TileType.LOGS: 1,
    TileType.CHEST: 1,
    TileType.ROCKS: 1,
    TileType.KEY: -1,
}


GENERIC_KEY_TILE_VALUES = {
    TileType.KEY: 3,
    TileType.SHIELD: 2,
    TileType.LOGS: 1,
    TileType.CHEST: 1,
    TileType.ROCKS: 1,
    TileType.SWORD: -1,
    TileType.WAND: -1,
}

NO_OBJECTIVE_TILE_VALUES = {
    TileType.SHIELD: 2,
    TileType.LOGS: 1,
    TileType.CHEST: 1,
    TileType.ROCKS: 1,
    TileType.SWORD: -2,
    TileType.WAND: -2,
    TileType.KEY: -2,
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
    ObjectiveType.REPTILIAN: SWORD_RESISTANT_MONSTER_TILE_VALUES,
    ObjectiveType.TREANT: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.DEMON: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.CHEST: GENERIC_KEY_TILE_VALUES,
    ObjectiveType.DOOR: GENERIC_KEY_TILE_VALUES,
}

ITEM_FLAT_IMPACT = {
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
}


@dataclass(frozen=True)
class Move(metaclass=abc.ABCMeta):
    impact: FrozenOrderedDict[TileType, int]

    @abc.abstractmethod
    def calculate_mouse_movement(self) -> List[Point]:
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

    def calculate_screen_destination(self) -> Point:
        """
        Should work with any size of cluster
        """
        any_pair = []
        for tile in self.cluster.tiles:
            any_pair.append(tile)
            if len(any_pair) == 2:
                break

        tile_centers = any_pair[0].screen_square.find_center(), any_pair[1].screen_square.find_center()
        pair_screen_distance = tile_centers[0].distance_between(tile_centers[1])
        pair_grid_distance = any_pair[0].grid_position.distance_between(any_pair[1].grid_position)

        unitary_distance = int(pair_screen_distance / pair_grid_distance)

        first_tile_center = any_pair[0].screen_square.find_center() - any_pair[0].grid_position * unitary_distance

        return first_tile_center + self.grid_destination * unitary_distance

    def calculate_mouse_movement(self) -> List[Point]:
        return [self.tile_to_move.screen_square.find_center(), self.calculate_screen_destination()]


@dataclass(frozen=True)
class ItemMove(Move):
    item: Item

    def __str__(self):
        return f"use {str(self.item)}"

    def calculate_mouse_movement(self) -> List[Point]:
        return [self.item.screen_square.find_center()]

    def calculate_score(self, value_per_tile_type: Dict[TileType, int]) -> int:
        return super().calculate_score(value_per_tile_type)


def create_item_move(item: Item, impact: FrozenOrderedDict[TileType, int] | None = None) -> ItemMove:
    return ItemMove(impact if impact is not None else ITEM_FLAT_IMPACT.get(item.type, frozendict()), item)


@dataclass(frozen=True)
class Objective:
    type: ObjectiveType = None
    screen_square: ScreenSquare = ScreenSquare()

    def select_best_move(self, possible_moves: Set[TileMove]) -> Tuple[TileMove, int] | None:
        value_per_tile_type = TILE_VALUES_PER_OBJECTIVE_TYPES.get(self.type, NO_OBJECTIVE_TILE_VALUES)

        best_move = max(possible_moves, key=lambda x: x.calculate_score(value_per_tile_type))
        score = best_move.calculate_score(value_per_tile_type)

        if score <= 0:
            return None

        return best_move, score if score > 0 else None
