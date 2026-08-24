from sqlalchemy import Column, DateTime, Integer, String, Table

def get_table_schema(metadata):
   return Table(
      "contact",
      metadata,
      Column("userid", Integer, primary_key=True),
      Column("fullname", String(255)),
      Column("surname", String(255)),
      Column("modifydate", DateTime),
      extend_existing=True,
   )

