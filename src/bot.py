import logging
from time import sleep
from typing import Callable

from src.domain.game_state import GameState
from src.domain.move import Move

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Bot:
    def __init__(self, update_game_state: Callable[[], GameState], move_tile: Callable[[Move], None]) -> None:
        self.update_game_state = update_game_state
        self.move_tile = move_tile

    def main_loop(
        self,
    ) -> None:
        logger.info("Bot is running.")
        try:
            while True:
                logger.info("Updating game state.")

                game_state = self.update_game_state()
                possible_moves = game_state.find_possible_moves()

                if not possible_moves:
                    logger.warning("No moves available.")
                    continue

                best_move = game_state.objective.select_best_move(possible_moves)

                self.move_tile(best_move)

                # TODO find objective

                sleep(0.1)
        except Exception as e:
            logger.exception(e)
            raise e
        finally:
            logger.info("Bot is stopped.")

    def find_best_move(self, game_state):
        pass

    def perform_best_move(self):
        pass
