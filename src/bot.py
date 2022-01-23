import logging
from time import sleep
from typing import Callable

logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, update_game_state: Callable) -> None:
        self.update_game_state = update_game_state

    def main_loop(
        self,
    ) -> None:
        logger.info("Bot is running.")
        while True:
            sleep(0.1)
            logger.info("Updating game state.")
            self.update_game_state()

    def find_best_move(self):
        pass

    def perform_best_move(self):
        pass
