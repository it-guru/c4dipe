from config import *
from event  import event
from kernel import *
import dbpool
from logger import *
import importlib
from sqlalchemy import MetaData, inspect, text



class Event(event):
   def __init__(self):
      super().__init__()

   def run(self):
        print(f"run {__file__}")


        logger.info("Starting automatic database schema discovery and update")

        # 1. Discover all base paths from MOD_PATH config
        modpath_str = config.get("GLOBAL", {}).get("MOD_PATH", "")
        base_dir = config["GLOBAL"]["BASE_DIR"]

        raw_paths = [p.strip() for p in modpath_str.split(":") if p.strip()]
        mod_dirs = []
        for p in raw_paths:
            mod_dirs.append(
                Path(p) if p.startswith("/") else Path(base_dir) / p
            )

        section_metadata_map = {}

        for mod_dir in mod_dirs:
            dbdict_base = mod_dir / "mod/*" / "dbDict"
            for dbdict_dir in mod_dir.glob("mod/*/dbDict"):
                if not dbdict_dir.is_dir():
                    continue

                for section_dir in dbdict_dir.iterdir():
                 
                    if not section_dir.is_dir():
                        continue
                    section_name = section_dir.name

                    if section_name not in section_metadata_map:
                        section_metadata_map[section_name] = MetaData()

                    target_metadata = section_metadata_map[section_name]
                    for schema_file in section_dir.glob("*.py"):
                        if schema_file.name.startswith("__"):
                            continue
                        self._load_schema_file(
                            schema_file, section_name, target_metadata
                        )

        logger.info(
            f"Discovered schema sections: {list(section_metadata_map.keys())}"
        )

        for section_name, metadata in section_metadata_map.items():
           if not metadata.tables:
               logger.warning(
                   f"No tables registered for section "\
                    "'{section_name}', skipping."
               )
               continue

           logger.info(
               f"--- Processing database update for section: "\
                "'{section_name}' ---"
           )

           try:
               logger.info(
                   f"Completed schema sync for section "\
                    "'{section_name}' ({len(metadata.tables)} tables "\
                    "registered)"
               )
               engine = dbpool.get_engine(section_name)
               metadata.create_all(engine)
               self._sync_missing_columns(engine, metadata)


           except Exception as e:
               logger.error(
                   f"Failed to process database update for section "\
                    "'{section_name}': {e}"
               )

        return({"status": "success","exitcode": 0})

   def _load_schema_file(self, schema_file: Path, section_name: str, metadata: MetaData):
      mod_name = f"dyn_dbdict_{section_name}_{schema_file.stem}"
      try:
          spec = importlib.util.spec_from_file_location(mod_name, schema_file)
          if spec and spec.loader:
              mod = importlib.util.module_from_spec(spec)
              spec.loader.exec_module(mod)

              if hasattr(mod, "get_table_schema"):
                  mod.get_table_schema(metadata)
                  logger.debug(
                      f"[{section_name}] Registered schema from {schema_file.name}"
                  )
              else:
                  logger.warning(
                      f"Schema file {schema_file} has no get_table_schema() function"
                  )
      except Exception as e:
          logger.error(
              f"Error loading schema file {schema_file} for section '{section_name}': {e}"
          )


   def _sync_missing_columns(self, engine, metadata: MetaData):
      inspector = inspect(engine)

      with engine.begin() as conn:
         for table_name, table in metadata.tables.items():
            existing_cols = {
                col["name"] for col in inspector.get_columns(table_name)
            }

            for column in table.columns:
               if column.name not in existing_cols:
                  logger.info(
                      f"Adding missing column '{column.name}' to table '{table_name}'"
                  )
                  # Compile column type for the active DB dialect
                  col_type = column.type.compile(engine.dialect)

                  # Wrap string in text() - required for 2.0, fully supported in 1.3
                  stmt = text(
                      f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type}"
                  )
                  pprint(stmt)
                  conn.execute(stmt)





