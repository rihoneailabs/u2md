import logging
import sys
from typing import Optional


def setup_logging(
        level: int = logging.INFO,
        log_file: Optional[str] = None
) -> logging.Logger:
    logger = logging.getLogger("url_to_markdown")
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
