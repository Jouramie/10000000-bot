import logging
from time import sleep

from src.domain.game_state import update_game_state
from src.infra.pyautogui_impl import move_tile

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# TODO
# 1. Fill the grid with unknown tiles
# 2. Calculate combo effects with visible tiles
# 3. Complete missing scan with remaining of last move


def main_loop() -> None:
    logger.info("Bot is running.")
    try:
        while True:
            logger.info("Updating game state.")

            game_state = update_game_state()
            best_move = game_state.select_best_move()
            move_tile(best_move)

            # TODO find objective

            sleep(0.1)
    except Exception as e:
        logger.exception(e)
        raise e
    finally:
        logger.info("Bot is stopped.")
