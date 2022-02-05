import logging

from src.context import Context

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(name)s - %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Loading 10,000,000.")
        Context().start()
    except Exception as e:
        logger.exception(e)
    finally:
        logger.info("Goodbye.")
