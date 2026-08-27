from .base import DataObj
from sqlalchemy import text,select
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from dbRecord import dbRecord
from kernel.condition import *
from logger import *

import dbpool
from datetime import datetime, timezone

from pprint import pformat, pprint


class DataObjSQLDB(DataObj):
    def __init__(self):
        super().__init__()
        self._is_connected         = False
        self._currentResultSet    = None

    def _connect(self):
       if (not self._is_connected):
          self.db=dbpool.get_connection(self._configSection) 
          self._is_connected = True
       return(self._is_connected)

    def get_from_sql(self) -> str:
       return(self._primaryBackendTable)

    def query(self):
       if (self._connect()):
          logger.debug("SQLDB: condition: "+pformat(self._CurrentFilterExpr))
          logger.debug("SQLDB: dialect: '"+self.db.dialect.name+"'")
          ASTprocessor=ConditionSQL()
          wherestr,qparam=ASTprocessor.compile(self._CurrentAST.getAST())
         
          logger.debug("SQLDB: wherestr: '"+pformat(wherestr)+"'")
         
          selLst=[]
          CurrentDepend=set()
          for fldname in self._Field:
             if (self._Field[fldname].selectfix):
                CurrentDepend.add(fldname)
          for fldname in self._CurrentView:
             if (fldname in self._Field):
                backendname=self._Field[fldname].getBackendName("select")
                if (not backendname is None):
                   aliasname=fldname
                   selLst.append(backendname+' AS "'+aliasname+'"')
                if (self._Field[fldname].depend):
                   for dfldname in self._Field[fldname].depend:
                      if (dfldname in self._Field):
                         CurrentDepend.add(dfldname)   
                      else:
                         raise(ValueError(
                            f"invalid .depend '{dfldname}' "\
                             "in field '{fldname}'")
                         )
          for dfldname in CurrentDepend:
             if (not dfldname in self._CurrentView):
                backendname=self._Field[dfldname].getBackendName("select")
                if (not backendname is None):
                   aliasname=dfldname
                   selLst.append(backendname+' AS "'+aliasname+'"')
         
          selectstr=', '.join(selLst) if (selLst) else "*"


          ####################################################################
          orderstr=None
          if (not self._CurrentOrder):
             self._CurrentOrder=self._CurrentView
          if (self._CurrentOrder):
             if (not ([self._CurrentOrder] == ["(NONE)"])):
                currentOrder=set()
                for fldname in self._CurrentOrder:
                   if (fldname in self._Field):
                      backendname=self._Field[fldname].getBackendName("order")
                      if (backendname):
                         currentOrder.add(backendname)
                if (currentOrder):
                   orderstr=",".join(currentOrder)
          ####################################################################
           
          
         

          ####################################################################
          limitAsLimit=None
          limitAsWhere=None
          if (self._limitResult>0 and not self._limitSoft):
             limitAsLimit=""+str(self._limitStart)+","+str(self._limitResult)
             limitAsWhere="(ROWNUM>="+str(self._limitStart)+\
                          " AND ROWNUM<="+str(self._limitResult)+")"

          if (self.db.dialect.name == "oracle"):
             if (not wherestr):
                wherestr=limitAsWhere
             else:
                wherestr=limitAsWhere+" AND "+wherestr
          ####################################################################

         
          sqlparts = [
              f"select {selectstr}",
              f"from {self.get_from_sql()}",
              f"where {wherestr}" if wherestr else None,
              f"order by {orderstr}" if orderstr else None,
              f"limit {limitAsLimit}" if self.db.dialect.name == "mysql" \
                                         and not limitAsLimit is None else None
          ]
         
          self._lastSQL=text(" ".join(filter(None,sqlparts)))

          logger.debug("SQLDB: cmd: '"+" ".join(filter(None,sqlparts))+"'")
          result={}
          result["data"]=[]

           
         
          if (self.do_sql(self._lastSQL,qparam)):
             return(True)
          else:
             print("DB Error:(%s) %s" % (self._lastSQL,self.lastError()))



    def do_sql(self,cmd,param):
       if (self._connect()):
          try:
             query=cmd
             #pprint(cmd)
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




    def get_next_sql(self):
       if (not self._currentResultSet is None):
          row = self._currentResultSet.fetchone()
          if (not row is None):
             self._RECNO+=1
             if hasattr(row, "_mapping"):
                return dict(row._mapping)
             return(dict(row))
          else:
             return(None)
       else:
          print("ERROR: call get_next_sql without self._currentResultSet")
       return(None)



    def get_next(self):
       row=self.get_next_sql()
       if (row is not None):
          mrow={}
          for k,v in row.items():
             if isinstance(v, datetime):
                if v is None:
                   mapped_row[k]=v
                elif v.tzinfo is None:
                   mrow[k]=v.replace(tzinfo=timezone.utc).strftime(
                             "%Y-%m-%d %H:%M:%S")
                else:
                   mrow[k]=v.astimezone(timezone.utc).strftime(
                             "%Y-%m-%d %H:%M:%S")
             elif isinstance(v, bytes):
                mrow[k]="[bytes]"
             else:
                mrow[k]=v
          # add some internal _ Entries
          mrow["_RECNO"]=self._RECNO

          # pack it in a dbRecord
          dbRow=dbRecord(mrow,self._Field,self._CurrentView)
          dbRow._parent=self
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

