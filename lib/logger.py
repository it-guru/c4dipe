import logging

__all__ = ['logger']


gunicorn_logger = logging.getLogger('gunicorn.error')

logger = gunicorn_logger

#def logger():
#   return(gunicorn_logger)
