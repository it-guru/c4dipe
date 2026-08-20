import threading
import traceback
import atexit
import sys
from config import config
from sqlalchemy import create_engine

_ENGINES = {}
_ENGINES_LOCK = threading.RLock()

_thread_local = threading.local()


def get_engine(configsection: str):
    if configsection in _ENGINES:
        return _ENGINES[configsection]

    with _ENGINES_LOCK:
        # Double-checked locking
        if configsection in _ENGINES:
            return _ENGINES[configsection]
        try:
            if configsection not in config:
                raise KeyError(f"Section '{configsection}' missing in config")

            conn_str = config[configsection].get("DATAOBJCONNECT")
            if not conn_str:
                raise ValueError(
                    f"DATAOBJCONNECT key missing in section '{configsection}'"
                )

            engine = create_engine(
                conn_str,
                pool_size=10,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True
            )

            _ENGINES[configsection] = engine
            return engine

        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(
                f"Could not create engine for '{configsection}': {e}"
            ) from e


def _get_current_conns():
    if not hasattr(_thread_local, "conns"):
        _thread_local.conns = {}
    return _thread_local.conns


def get_connection(configsection: str):
    conns = _get_current_conns()

    if configsection not in conns:
        engine = get_engine(configsection)
        conn = engine.connect()
        trans = conn.begin()
        conns[configsection] = {"conn": conn, "trans": trans}

    return conns[configsection]["conn"]


def closeAllOpenTransactionsInCurrentThread(exception=None):
    #print("closeAllOpenTransactionsInCurrentThread:")
    conns = getattr(_thread_local, "conns", None)
    if not conns:
        return

    for configsection, item in list(conns.items()):
        conn = item["conn"]
        trans = item["trans"]
        try:
            if exception is not None:
                trans.rollback()
            else:
                trans.commit()
        finally:
            conn.close()

    _thread_local.conns = {}


def _auto_close_on_exit():
    exc_type, exc_val, _ = sys.exc_info()

    is_error = False
    if exc_type is not None:
        if issubclass(exc_type, SystemExit):
            is_error = exc_val.code not in (0, None)
        else:
            is_error = True

    # Wenn Fehler vorliegt -> Rollback, sonst Commit
    err = exc_val if is_error else None
    closeAllOpenTransactionsInCurrentThread(exception=err)


atexit.register(_auto_close_on_exit)
