import logging
import os
import sys

__all__ = ['logger']

LOGGER_NAME = 'c4dipe'

def _setup_logger():
    logger = logging.getLogger(LOGGER_NAME)
    
    if getattr(logger, "_is_configured", False):
        return logger

    env_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, env_level, logging.INFO)
    logger.setLevel(log_level)

    is_gunicorn = "gunicorn" in sys.modules or os.environ.get("SERVER_SOFTWARE", "").startswith("gunicorn")

    if is_gunicorn:
        gunicorn_logger = logging.getLogger("gunicorn.error")
        logger.handlers = gunicorn_logger.handlers
        logger.setLevel(gunicorn_logger.level)
        logger.propagate = False
    else:
        if not logger.handlers:
            stderr_handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(
                fmt="[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S %z",
            )
            stderr_handler.setFormatter(formatter)
            logger.addHandler(stderr_handler)
            logger.propagate = False

    logger._is_configured = True
    return logger

logger = _setup_logger()

