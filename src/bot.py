import logging
from time import sleep
from typing import Callable

from src.domain.game_state import GameState

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Bot:
    def __init__(self, update_game_state: Callable[[], GameState]) -> None:
        self.update_game_state = update_game_state

    def main_loop(
        self,
    ) -> None:
        logger.info("Bot is running.")
        try:
            while True:
                sleep(0.1)
                logger.info("Updating game state.")
                game_state = self.update_game_state()
                possible_moves = game_state.find_possible_moves()
                for possible_move in possible_moves:
                    logger.debug(tuple(str(tile) for tile in possible_move))
        except Exception as e:
            logger.exception(e)
        finally:
            logger.info("Bot is stopped.")

    def find_best_move(self, game_state):
        pass

    def perform_best_move(self):
        pass
