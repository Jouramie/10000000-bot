import logging
from dataclasses import dataclass
from typing import FrozenSet

from src.domain.grid import Grid, EmptyGrid
from src.domain.item import Item
from src.domain.objective import Objective, TileMove, create_item_move
from src.infra.pyautogui_impl import detect_game_state

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TILE_THRESHOLD = 50


@dataclass
class GameState:
    grid: Grid = EmptyGrid()
    objective: Objective = Objective()
    items: FrozenSet[Item] = frozenset()

    def select_best_move(self) -> TileMove | None:
        possible_moves = self._find_possible_move()

        if not possible_moves:
            logger.warning("No moves available.")
            return None

        str_moves = ""
        for move in possible_moves:
            str_moves += str(move) + "\n"

        logger.debug(f"Evaluating moves {str_moves[:-1]}")

        packed_move = self.objective.select_best_move(possible_moves)
        if packed_move is None:
            return None

        best_move, score = packed_move
        logger.info(f"Best move is {str(best_move)} with score {score}.")
        return best_move

    def _find_possible_move(self):
        possible_moves = {create_item_move(item) for item in self.items}

        if len(self.grid) > TILE_THRESHOLD:
            possible_moves |= self.grid.fill_with_unknown().find_possible_moves()
        else:
            logger.warning(f"Found only {len(game_state.grid)} tiles. Not counting grid in moves selection.")

        return possible_moves


game_state = GameState()


def update_game_state() -> GameState:
    global game_state

    grid, objective, items = detect_game_state()
    game_state = GameState(grid, objective, items)

    logger.info(f"GameState updated. {len(game_state.grid)} tiles. Objective: {game_state.objective.type}.")
    return game_state


def fetch_game_state() -> GameState:
    global game_state
    return game_state
