import logging
from time import sleep

from src.domain.game_state import update_game_state
from src.infra.pyautogui_impl import do_move

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

MOVEMENT_ENABLED = True

TILE_THRESHOLD = 50

RETRY_DELAY = 0
WAIT_AFTER_COMBO = 0.5

# TODO backlog
# Use STAR
# Adjust value per tile type per quest
# Lower shield value if max shield
# Move with 5+ key should have less value than 4 but more than 3


def main_loop() -> None:
    logger.info("Bot is running.")
    try:
        while True:
            logger.info("Updating game state.")

            game_state = update_game_state()

            while len(game_state.grid) <= TILE_THRESHOLD:
                logger.warning(f"Found only {len(game_state.grid)} tiles. Reloading game state in {RETRY_DELAY*1000}ms.")
                sleep(RETRY_DELAY)
                game_state = update_game_state()

            best_move = game_state.select_best_move()

            if MOVEMENT_ENABLED and best_move is not None:
                do_move(best_move)

            sleep(0.8)
    except Exception as e:
        logger.exception(e)
        raise e
    finally:
        logger.info("Bot is stopped.")
