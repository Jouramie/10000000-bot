import logging
from dataclasses import dataclass
from typing import Set

from src.domain.grid import Grid, EmptyGrid
from src.domain.item import Item
from src.domain.objective import Objective, TileMove, create_item_move
from src.infra.pyautogui_impl import detect_game_state

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class GameState:
    grid: Grid = EmptyGrid()
    objective: Objective = Objective()
    items: Set[Item] = frozenset()

    def select_best_move(self) -> TileMove | None:
        possible_moves = self.grid.find_possible_moves() | {create_item_move(item) for item in self.items}

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


game_state = GameState()


def update_game_state() -> GameState:
    global game_state

    game_state = GameState(*detect_game_state())

    logger.info(f"GameState updated. {len(game_state.grid)} tiles. Objective: {game_state.objective.type}.")
    return game_state


def fetch_game_state() -> GameState:
    global game_state
    return game_state
