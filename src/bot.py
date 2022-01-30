import logging
from time import sleep

from src.domain.game_state import update_game_state
from src.infra.pyautogui_impl import move_tile

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# TODO backlog
# Use items
# Use STAR
# Apply gravity when there are hole in the grid (require to take a single screenshot
# Complete missing scan with remaining of last move
# Adjust value per tile type per quest
# Lower shield value if max shield
# Move with 5+ key should have less value than 4 but more than 3


def main_loop() -> None:
    logger.info("Bot is running.")
    try:
        while True:
            logger.info("Updating game state.")

            game_state = update_game_state()
            best_move = game_state.select_best_move()

            if best_move is not None:
                move_tile(best_move)

            sleep(0.1)
    except Exception as e:
        logger.exception(e)
        raise e
    finally:
        logger.info("Bot is stopped.")
