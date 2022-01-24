from dataclasses import dataclass
from typing import Tuple

from src.domain.tile import Tile, GridPosition


@dataclass(frozen=True)
class Movement:
    pair: Tuple[Tile]
    tile_to_move: Tile
    destination: GridPosition
    # TODO impact
