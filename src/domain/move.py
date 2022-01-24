import abc
from dataclasses import dataclass
from typing import Tuple

from src.domain.tile import Tile, GridPosition


@dataclass(frozen=True)
class Move:
    pair: Tuple[Tile]
    tile_to_move: Tile
    destination: GridPosition
    # TODO impact


class TileMover(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self, move: Move):
        raise NotImplementedError
