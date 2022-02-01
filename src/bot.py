import logging
from time import sleep

from src.domain.game_state import update_game_state
from src.domain.objective import TileMove
from src.infra.pyautogui_impl import do_move

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

MOVEMENT_ENABLED = True

TILE_THRESHOLD = 50

RETRY_DELAY = 0
WAIT_AFTER_COMBO = 0.5

# TODO backlog
# Use STAR
# Complete missing scan with remaining of last move
# - Apply gravity when there are hole in the grid (require to take a single screenshot)
# - Periodically reset without using previous scans
# Adjust value per tile type per quest
# Lower shield value if max shield
# Move with 5+ key should have less value than 4 but more than 3


def main_loop() -> None:
    logger.info("Bot is running.")
    try:
        resulting_grid = None
        while True:
            logger.info("Updating game state.")

            game_state = update_game_state()

            while len(game_state.grid) <= TILE_THRESHOLD:
                logger.warning(f"Found only {len(game_state.grid)} tiles. Reloading game state in {RETRY_DELAY*1000}ms.")
                sleep(RETRY_DELAY)
                game_state = update_game_state()

            if resulting_grid is not None:
                game_state.grid = game_state.grid.fill_with_previous_grid(resulting_grid)
            else:
                game_state.grid = game_state.grid.fill_with_unknown()

            logger.info(f"Merged grid {game_state.grid}")

            best_move = game_state.select_best_move()

            if MOVEMENT_ENABLED:
                # FIXME that's illegal
                if isinstance(best_move, TileMove):
                    resulting_grid = game_state.grid.simulate_line_shift(best_move.tile_to_move.grid_position, best_move.grid_destination)[1]
                else:
                    resulting_grid = None

                if best_move is not None:
                    do_move(best_move)

            sleep(1)
    except Exception as e:
        logger.exception(e)
        raise e
    finally:
        logger.info("Bot is stopped.")
