import logging
from dataclasses import dataclass

from src.domain.grid import Grid, InconsistentGrid, Move
from src.domain.objective import NoObjective, Objective
from src.infra.pyautogui_impl import detect_game_state

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class GameState:
    grid: Grid = InconsistentGrid()
    objective: Objective = NoObjective()

    def select_best_move(self) -> Move | None:
        possible_moves = self.grid.find_possible_moves()

        if not possible_moves:
            logger.warning("No moves available.")
            return None

        logger.debug(f"Movements found {possible_moves}")

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
