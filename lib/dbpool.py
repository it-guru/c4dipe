from config import config
import threading
from sqlalchemy import create_engine
import json

# 1. Globale Registry für die Engines + Lock zur Thread-Sicherung
_ENGINES = {}
_ENGINES_LOCK = threading.RLock()


def get_engine(configsection: str):
   #print(f"dbpool get_engine for '{configsection}'")
   if configsection in _ENGINES:
       return _ENGINES[configsection]

   #print(f"dbpool try to get lock '{configsection}'")
   with _ENGINES_LOCK:
       # Double-checked locking
       if configsection in _ENGINES:
           return _ENGINES[configsection]
       try:
           # 1. Validate section presence
           #print("config = %s" % json.dumps(config[configsection])) 
           if configsection not in config:
               raise KeyError(f"Section '{configsection}' missing in config")

           # 2. Extract connection string safely
           conn_str = config[configsection].get("DATAOBJCONNECT")
           if not conn_str:
               raise ValueError(f"DATAOBJCONNECT key missing in section '{configsection}'")

           #print(f"dbpool creating engine for '{configsection}'...")

           # 3. Create SQLAlchemy engine
           engine = create_engine(
               conn_str,
               pool_size=10,
               max_overflow=10,
               pool_timeout=30,
               pool_recycle=3600,
           )

           _ENGINES[configsection] = engine
           #print(f"dbpool '{configsection}' successfully created: {engine}")
           return engine

       except Exception as e:
           # Catch exceptions to prevent abrupt process termination
           print(f"ERROR in dbpool for '{configsection}': {type(e).__name__} - {e}")
           traceback.print_exc()
           raise RuntimeError(f"Could not create engine for '{configsection}': {e}") from e

