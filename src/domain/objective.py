import abc
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Callable, Set, List

from src.domain.move import Move
from src.domain.tile import ScreenSquare, TileType


class ObjectiveType(Enum):
    ZOMBIE = auto()
    SKELETON = auto()
    SKELETON_ARCHER = auto()
    T_REX = auto()
    FALLEN_SOLDIER = auto()
    WHITE_DRAGON = auto()
    FIRE_ELEMENTAL = auto()
    CHEST = auto()
    DOOR = auto()

    def __str__(self):
        return self.name


def select_best_move(tile_types: List[TileType], possible_moves: Set[Move]):
    ordered_moves = sorted(
        [move for move in possible_moves],
        key=lambda move: max([move.calculate_impact(tile_type) for tile_type in tile_types]),
        reverse=True,
    )
    return ordered_moves[0]


@dataclass(frozen=True)
class Objective(metaclass=abc.ABCMeta):
    type: ObjectiveType = None
    screen_square: ScreenSquare = ScreenSquare()

    @abc.abstractmethod
    def select_best_move(self, possible_moves: Set[Move]):
        raise NotImplementedError()


class MonsterObjective(Objective):
    def select_best_move(self, possible_moves: Set[Move]):
        return select_best_move([TileType.SWORD, TileType.WAND], possible_moves)


class KeyObjective(Objective):
    def select_best_move(self, possible_moves: Set[Move]):
        return select_best_move([TileType.KEY], possible_moves)


class NoObjective(Objective):
    def select_best_move(self, possible_moves: Set[Move]):
        return select_best_move([TileType.SHIELD, TileType.CHEST, TileType.ROCKS, TileType.LOGS], possible_moves)


OBJECTIVE_CLASS_PER_TYPE: Dict[ObjectiveType, Callable[[ObjectiveType, ScreenSquare], Objective]] = {
    ObjectiveType.ZOMBIE: MonsterObjective,
    ObjectiveType.SKELETON: MonsterObjective,
    ObjectiveType.SKELETON_ARCHER: MonsterObjective,
    ObjectiveType.T_REX: MonsterObjective,
    ObjectiveType.FALLEN_SOLDIER: MonsterObjective,
    ObjectiveType.WHITE_DRAGON: MonsterObjective,
    ObjectiveType.FIRE_ELEMENTAL: MonsterObjective,
    ObjectiveType.CHEST: KeyObjective,
    ObjectiveType.DOOR: KeyObjective,
}


def create_objective(objective_type: ObjectiveType = None, screen_position: ScreenSquare = ScreenSquare()) -> Objective:
    clazz = OBJECTIVE_CLASS_PER_TYPE.get(objective_type)
    if clazz is None:
        return NoObjective()
    return clazz(objective_type, screen_position)
