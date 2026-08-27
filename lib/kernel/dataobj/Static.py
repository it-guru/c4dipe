from .base import DataObj
from rawRec import rawRec
from kernel.condition import *
from logger import *

from datetime import datetime, timezone

from pprint import pformat, pprint

class _ReverseStaticOrder:
    def __init__(self, obj):
        self.obj = obj
        
    def __lt__(self, other):
        return self.obj > other.obj

def parse_typed_value(val: str):
    if not isinstance(val, str):
        return val
    
    # 1. Versuche Integer / Float
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
        
    # 2. Versuche Datum (optional, Format anpassen falls nötig)
    # try:
    #     return datetime.fromisoformat(val)
    # except ValueError:
    #     pass

    return val





class DataObjStatic(DataObj):
    def __init__(self):
       super().__init__()
       self._rawData=[] 

    def rawDataCollect(self):
       return([])


    def query(self):
       print("Static: do query()")
       self._rawData=self.rawDataCollect()  # entspricht dem SQL Kommando
       #logger.debug("Static: _rawData: "+pformat(self._rawData,width=99999))
       self._rawList=[]

       for rawDataRec in self._rawData:
          stRow=rawRec(rawDataRec,self._Field,self._CurrentView)
          stRow._parent=self
          self._rawList.append(stRow)

       ####################################################################
       if (not self._CurrentOrder):
          self._CurrentOrder=self._CurrentView
       if (self._CurrentOrder):
          if (not ["(NONE)"] == self._CurrentOrder):
             logger.debug("Static: COrder: \n"+pformat(self._CurrentOrder))
             sort_key=self.make_sort_key(self._CurrentOrder)
             self._rawList=sorted(self._rawList,key=sort_key)
       ####################################################################

       self._RECNO=0
       for stRec in self._rawList:
          stRec._raw["_RECNO"]=self._RECNO
          self._RECNO+=1


       temp_rawList=[]
       for stRec in self._rawList:
          if (stRec._raw["_RECNO"]<self._limitStart):
             continue
          temp_rawList.append(stRec)
       self._rawList=temp_rawList

       return(True) 



    def get_next(self):
       if (not self._rawList):
          return(None)
       curRec=self._rawList.pop(0)
       if (self._limitResult>0):
          if (curRec._raw["_RECNO"]+1>self._limitResult+self._limitStart):
             self._rawList=[]
             return(None)

       return(curRec)


#
#    def get_next_sql(self):
#       if (not self._currentResultSet is None):
#          row = self._currentResultSet.fetchone()
#          if (not row is None):
#             self._RECNO+=1
#             if hasattr(row, "_mapping"):
#                return dict(row._mapping)
#             return(dict(row))
#          else:
#             return(None)
#       else:
#          print("ERROR: call get_next_sql without self._currentResultSet")
#       return(None)
#
#
#
#    def get_next(self):
#       row=self.get_next_sql()
#       if (row is not None):
#          mrow={}
#          for k,v in row.items():
#             if isinstance(v, datetime):
#                if v is None:
#                   mapped_row[k]=v
#                elif v.tzinfo is None:
#                   mrow[k]=v.replace(tzinfo=timezone.utc).strftime(
#                             "%Y-%m-%d %H:%M:%S")
#                else:
#                   mrow[k]=v.astimezone(timezone.utc).strftime(
#                             "%Y-%m-%d %H:%M:%S")
#             elif isinstance(v, bytes):
#                mrow[k]="[bytes]"
#             else:
#                mrow[k]=v
#          # add some internal _ Entries
#          mrow["_RECNO"]=self._RECNO
#
#          # pack it in a rawRec
#          dbRow=rawRec(mrow,self._Field,self._CurrentView)
#          dbRow._parent=self
#          return(dbRow)
#
#       return(None)



    def insertRecord(self, record_id: int, data: dict) -> bool:
        return False

    def updateRecord(self, record_id: int, new_data: dict) -> bool:
        return False

    def deleteRecord(self, record_id: int) -> bool:
        return False


    def make_sort_key(self,current_order: list):
       parsed_order = []
       
       for field in current_order:
           if field.startswith("-"):
               parsed_order.append((field[1:], True))
           elif field.startswith("+"):
               parsed_order.append((field[1:], False))
           else:
               parsed_order.append((field, False))
      
       def key_func(rec: dict):
           key_tuple = []
           for field, is_reverse in parsed_order:
               val = rec.get(field, "")
               typed_val = parse_typed_value(val)
               
               if is_reverse:
                   # Absteigende Behandlung je nach Typ:
                   if isinstance(typed_val, (int, float)):
                       key_tuple.append(-typed_val)
                   else:
                       key_tuple.append(ReverseOrder(typed_val))
               else:
                   key_tuple.append(typed_val)
                   
           return tuple(key_tuple)
      
       return key_func

