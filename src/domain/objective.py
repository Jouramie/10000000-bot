from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Set, List, Tuple

from src.domain.grid import ScreenSquare, TileType, Move


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
    CHEST = auto()
    DOOR = auto()

    def __str__(self):
        return self.name


GENERIC_MONSTER_TILE_VALUES = {
    TileType.SWORD: 3,
    TileType.WAND: 3,
    TileType.SHIELD: 2,
    TileType.LOGS: 1,
    TileType.CHEST: 1,
    TileType.ROCKS: 1,
}

GENERIC_KEY_TILE_VALUES = {
    TileType.KEY: 3,
    TileType.SHIELD: 2,
    TileType.LOGS: 1,
    TileType.CHEST: 1,
    TileType.ROCKS: 1,
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
    ObjectiveType.WATER_ELEMENTAL: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.RED_DRAGON: GENERIC_MONSTER_TILE_VALUES,
    ObjectiveType.CHEST: GENERIC_KEY_TILE_VALUES,
    ObjectiveType.DOOR: GENERIC_KEY_TILE_VALUES,
}


def _move_comparator(prioritized_tiles: List[TileType]) -> Callable[[Move], Tuple[int, ...]]:
    return lambda move: tuple(move.calculate_impact(tile_type) for tile_type in prioritized_tiles)


def select_best_move(prioritized_tiles: List[TileType], possible_moves: Set[Move]):
    ordered_moves = sorted(
        [move for move in possible_moves],
        key=_move_comparator(prioritized_tiles),
        reverse=True,
    )
    return ordered_moves[0]


@dataclass(frozen=True)
class Objective:
    type: ObjectiveType = None
    screen_square: ScreenSquare = ScreenSquare()

    def select_best_move(self, possible_moves: Set[Move]) -> Move | None:
        value_per_tile_type = TILE_VALUES_PER_OBJECTIVE_TYPES.get(self.type, NO_OBJECTIVE_TILE_VALUES)

        best_move = max(possible_moves, key=lambda x: x.calculate_value(value_per_tile_type))
        return best_move if best_move.calculate_value(value_per_tile_type) > 0 else None
