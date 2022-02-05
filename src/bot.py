import logging
from time import sleep

from src import properties
from src.domain.game_state import GameState
from src.infra.pyautogui_impl import do_move, detect_game_state

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# TODO backlog
# If last move was item move, don't screenshot before next move
# Auto replay
# Add items in UI
# Give proper value to scrolls
# Handle status effects
# Adjust value per tile type per quest
# Lower shield value if max shield
# Move with 5+ key should have less value than 4 but more than 3

running = True

game_state = GameState()


def fetch_game_state() -> GameState:
    global game_state
    return game_state


def main_loop() -> None:
    global running
    global game_state

    logger.info("Bot is running.")
    try:
        while running:
            logger.info("Updating game state.")

            game_state = detect_game_state()
            logger.info(f"GameState updated. {len(game_state.grid)} tiles. Objective: {game_state.objective.type}.")

            best_move = game_state.select_best_move()

            if properties.MOVEMENT_ENABLED and best_move is not None:
                move_delay = do_move(best_move)
            else:
                move_delay = 0

            sleep(move_delay)
    except Exception as e:
        logger.exception(e)
        raise e
    finally:
        logger.info("Bot is stopped.")
