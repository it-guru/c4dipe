from config import config
import json
import dbpool
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from dbRecord import dbRecord
from datetime import datetime, timezone

from kernel.field   import *
from kernel.dataobj import *

from kernel.condition import *
import kernel.condition.base

from pprint import pformat, pprint

class BaseContact(DataObjSQLDB):
    def __init__(self):
       super().__init__()
       self._configSection = "GLOBAL"
       self.is_connected = False
       self._currentResultSet = None
       self.addFields(
          FieldText(
             name="fullname"
          ),
          FieldText(  
             name="name"
          ),
          FieldURL(
             name="urlofcurrentrec"
          ),
          FieldText(
             name="surname",
             insertafter="name"
          ),
          FieldText(
             name="givenname",
             insertafter="xname"
          ),
          FieldMDate()
       )



#    def secureSetFilter(self,search_criteria):
#       search_criteria[0].append([{
#          "cistatus": "4"
#       }])
#       return(super().secureSetFilter(search_criteria))


    def getDictList(self,view:str="ALL",filterExpr=None):

       self._CurrentAST=ConditionalAST(self,self._CurrentFilterExpr)
       ASTprocessor=ConditionSQL()
       wherestr,qparam=ASTprocessor.compile(self._CurrentAST.getAST())

       self._lastSQL="select * from grp "+wherestr+" limit 10"
       result={}
       result["data"]=[]
     
       if (self.sql_do(self._lastSQL,qparam)):
          while True:
            row=self.get_next()
            if row is None: break
            result["data"].append(dict(row))
       else:
          print("DB Error: %s" % o.lastError())

       return(result["data"])



    def _connect(self):
       if (not self.is_connected):
          self.db=dbpool.get_engine(self._configSection) 
          self.is_connected = True
       return(self.is_connected)
       
#       print("init in BaseUserContact %s" % json.dumps(config[self._configSection]))

#       self.records = {}


    def sql_do(self,cmd,param):
       if (self._connect()):
          try:
             query=text(cmd)
             self._currentResultSet = self.db.execute(query,param)
             self._lastError=None
             self._RECNO=0
             return(True)
          except DBAPIError as e:
             self._lastError=e.orig
             if hasattr(self._lastError,'args') and len(self._lastError.args)>1:
                self._lastError=self._lastError.args[1]
          except SQLAlchemyError as e:
             self._lastError=str(e)

       else:
          self._lastError="Backend not connected"

       return(False)

    def lastError(self):
       return(self._lastError)


    def sql_get_next(self):
       if (not self._currentResultSet is None):
          row = self._currentResultSet.fetchone()
          self._RECNO+=1
          return(row)
       else:
          print("ERROR: call sql_get_next without self._currentResultSet")
       return(None)

    def get_next(self):
       row=self.sql_get_next()
       if not row is None:
          mrow={}
          for k,v in dict(row._mapping).items():
             if isinstance(v, datetime):
                if v is None:
                   mapped_row[k]=v
                elif v.tzinfo is None:
                   mrow[k]=v.replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                else:
                   mrow[k]=v.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
             elif isinstance(v, bytes):
                mrow[k]="[bytes]"
             else:
                mrow[k]=v
          # add some internal _ Entries
          mrow["_RECNO"]=self._RECNO

          # pack it in a dbRecord
          dbRow=dbRecord(mrow)
          return(dbRow)

       return(None)


    def insert_record(self, record_id: int, data: dict) -> bool:
        if record_id in self.records:
            print(f"Fehler: Datensatz {record_id} existiert bereits.")
            return False

        self.records[record_id] = data
        print(f"Datensatz {record_id} erfolgreich eingefuegt.")
        return True

    def update_record(self, record_id: int, new_data: dict) -> bool:
        if record_id not in self.records:
            print(f"Fehler: Datensatz {record_id} nicht gefunden.")
            return False

        # Aktualisiert die Werte im Dictionary
        self.records[record_id].update(new_data)
        print(f"Datensatz {record_id} erfolgreich aktualisiert.")
        return True

    def delete_record(self, record_id: int) -> bool:
        if record_id not in self.records:
            print(f"Fehler: Datensatz {record_id} existiert nicht.")
            return False

        del self.records[record_id]
        print(f"Datensatz {record_id} erfolgreich geloescht.")
        return True

