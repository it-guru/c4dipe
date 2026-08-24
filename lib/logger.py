import logging
import os
import sys

__all__ = ['logger']


gunicorn_logger = logging.getLogger('gunicorn.error')

logger = gunicorn_logger

if not logger.handlers:
    env_level = os.environ.get("LOG_LEVEL", "warn").upper()
    log_level = getattr(logging, env_level, logging.INFO)
    logger.setLevel(log_level)

    stderr_handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)
    logger.propagate = False

