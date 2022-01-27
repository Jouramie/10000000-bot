from dataclasses import dataclass
from functools import singledispatch
from typing import List

from src.domain.game_state import GameState
from src.domain.objective import ObjectiveType, Objective
from src.domain.tile import TileType, Grid, Tile


@dataclass(frozen=True)
class TileModel:
    type: TileType
    left: int
    top: int
    height: int
    width: int
    grid_x: int
    grid_y: int


@dataclass(frozen=True)
class ObjectiveModel:
    type: ObjectiveType


@dataclass(frozen=True)
class GameStateModel:
    tiles: List[TileModel]
    objective: ObjectiveModel


@singledispatch
def to_model(obj):
    raise NotImplementedError()


@to_model.register
def _(game_state: GameState) -> GameStateModel:
    return GameStateModel(to_model(game_state.grid), to_model(game_state.objective))


@to_model.register
def _(grid: Grid) -> List[TileModel]:
    return to_model(grid.tiles)


@to_model.register
def _(li: list) -> list:
    return [to_model(i) for i in li]


@to_model.register
def _(tile: Tile) -> TileModel:
    return TileModel(
        tile.type,
        tile.screen_square.left,
        tile.screen_square.top,
        tile.screen_square.height,
        tile.screen_square.width,
        tile.grid_position.x,
        tile.grid_position.y,
    )


@to_model.register
def _(objective: Objective) -> ObjectiveModel:
    return ObjectiveModel(objective.type)
