import abc
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Callable

from src.domain.tile import ScreenSquare


class ObjectiveType(Enum):
    ZOMBIE = auto()
    SKELETON = auto()
    SKELETON_ARCHER = auto()
    FALLEN_SOLDIER = auto()
    WHITE_DRAGON = auto()
    FIRE_ELEMENTAL = auto()
    CHEST = auto()
    DOOR = auto()

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Objective(metaclass=abc.ABCMeta):
    type: ObjectiveType = None
    screen_square: ScreenSquare = ScreenSquare()

    @abc.abstractmethod
    def find_best_combo_to_fulfill_objective(self):
        raise NotImplementedError()


class MonsterObjective(Objective):
    def find_best_combo_to_fulfill_objective(self):
        # SWORD or WAND
        pass


class KeyObjective(Objective):
    def find_best_combo_to_fulfill_objective(self):
        # KEY
        pass


class NoObjective(Objective):
    def find_best_combo_to_fulfill_objective(self):
        # SHIELD, CHEST, ROCKS, LOGS
        pass


OBJECTIVE_CLASS_PER_TYPE: Dict[ObjectiveType, Callable[[ObjectiveType, ScreenSquare], Objective]] = {
    ObjectiveType.ZOMBIE: MonsterObjective,
    ObjectiveType.SKELETON: MonsterObjective,
    ObjectiveType.SKELETON_ARCHER: MonsterObjective,
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
