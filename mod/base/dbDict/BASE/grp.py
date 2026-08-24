from sqlalchemy import Column, DateTime, Integer, String, Table

def get_table_schema(metadata):
   return Table(
      "grp",
      metadata,
      Column("grpid", Integer, primary_key=True),
      Column("fullname", String(255)),
      Column("name", String(255)),
      Column("modifydate", DateTime),
      extend_existing=True,
   )

