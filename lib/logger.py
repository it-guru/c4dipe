import logging
import os
import sys

__all__ = ['logger']

# Ein eigener, klar definierter Logger-Name für dein Framework
LOGGER_NAME = 'c4dipe'

def _setup_logger():
    logger = logging.getLogger(LOGGER_NAME)
    
    # Verhindert Mehrfach-Initialisierung, falls das Modul mehrfach geladen wird
    if getattr(logger, "_is_configured", False):
        return logger

    # Log-Level aus Umgebung lesen
    env_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, env_level, logging.INFO)
    logger.setLevel(log_level)

    # Prüfen, ob wir innerhalb eines Gunicorn-Workers laufen
    is_gunicorn = "gunicorn" in sys.modules or os.environ.get("SERVER_SOFTWARE", "").startswith("gunicorn")

    if is_gunicorn:
        # Im Gunicorn-Kontext leiten wir Logs an den Gunicorn-Error-Logger weiter,
        # damit Formate, Output-Streams und Log-Level zentral von Gunicorn verwaltet werden.
        gunicorn_logger = logging.getLogger("gunicorn.error")
        logger.handlers = gunicorn_logger.handlers
        logger.setLevel(gunicorn_logger.level)
        logger.propagate = False
    else:
        # In der normalen Shell / CLI: Eigenen Handler erzeugen
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

