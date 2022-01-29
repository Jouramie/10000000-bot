import logging
from dataclasses import dataclass

from src.domain.grid import Grid, InconsistentGrid, Move
from src.domain.objective import NoObjective, Objective
from src.infra.pyautogui_impl import detect_game_state

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class GameState:
    grid: Grid = InconsistentGrid()
    objective: Objective = NoObjective()

    def select_best_move(self) -> Move | None:
        possible_moves = self.grid.find_possible_moves()

        if not possible_moves:
            logger.warning("No moves available.")
            return None

        str_moves = ""
        for move in possible_moves:
            str_moves += str(move) + "\n"

        logger.debug(f"Evaluating moves {str_moves[:-1]}")

        return self.objective.select_best_move(possible_moves)


game_state = GameState()


def update_game_state() -> GameState:
    global game_state

    game_state = GameState(*detect_game_state())

    logger.info(f"GameState updated. {len(game_state.grid)} tiles. Objective: {game_state.objective.type}.")
    return game_state


def fetch_game_state() -> GameState:
    global game_state
    return game_state
