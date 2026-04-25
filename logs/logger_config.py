# logs/logger_config.py

import logging
import sys


def get_logger(name: str = "lightrag", level=logging.INFO):
    """
    Minimal logger used by LightRAG / LibraAI.
    Safe fallback when original logging module is missing.
    """

    logger = logging.getLogger(name)

    # Tránh add handler nhiều lần
    if logger.handlers:
        return logger

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

