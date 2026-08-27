import weakref
import re
from kernel.field import *
from kernel.condition import *
from pprint import pprint

#  general:
#   addFields
#
#  primary operations:
#   query,countRecords
#      base:
#        - setFilter
#        - limit
#        - setCurrentView
#        -setCurrentOrder)
#
#   insertRecord
#   updateRecord
#   deleteRecord
#   validatedInsertRecord
#   validatedUpdateRecord
#   validatedDeleteRecord
#
#  in User-Context:
#
#   query   (secureSetFilter based)
#   secureValidatedInsertRecord
#   secureValidatedUpdateRecord
#   secureValidatedDeleteRecord
#

class DataObj:
   def __init__(self, db_connection_string: str = None):
      self._Field={}
      self._FieldOrder=[]
      self._GroupOrder=[]

      self._CurrentFilterExpr=[[]]
      self._CurrentView=[]
      self._CurrentOrder=[]

      self._limitResult=0
      self._limitStart=0
      self._limitSoft=False   # False means limit by backend

      if (hasattr(self, "_class_fields")):
         self.addFields(*self._class_fields)

   def __init_subclass__(cls, **kwargs):
      super().__init_subclass__(**kwargs)
      
      cls._class_fields = []

      for attr_name, attr_value in list(cls.__dict__.items()):
         if isinstance(attr_value, Field):
            if not getattr(attr_value, "name", None):
                attr_value.name = attr_name
            cls._class_fields.append(attr_value)


   def setFilter(self,filterExpr):
      if (isinstance(filterExpr,dict)):
         self._CurrentFilterExpr=[[filterExpr]]
         return(True) 
      if (isinstance(filterExpr,list)):
         haveSubDict=False
         for subEnt in filterExpr:
            if (isinstance(subEnt,dict)):
               haveSubDict=True
         if (haveSubDict):
            self._CurrentFilterExpr=[filterExpr]
            return(True) 
        
      self._CurrentFilterExpr=filterExpr
      self._CurrentAST=ConditionalAST(self._CurrentFilterExpr,self._Field)


      return(True) 

   def secureSetFilter(self,filterExpr):
      return(self.setFilter(filterExpr))

   def limit(self,
             limitResult: int=0,
             limitStart:  int=0,
             limitSoft:   bool=False) -> int:
      self._limitResult=limitResult       
      self._limitStart=limitStart       
      self._limitSoft=limitSoft       
      
      return(self._limitResult)

       
   def setCurrentView(self,view): 
      if (isinstance(view,list)):
         self._CurrentView=view
      if (isinstance(view,str)):
         if (view == "(ALL)"):
            self._CurrentView=self._FieldOrder
         else:
            if (re.match(r"^\(.?\)$",view)):
               self._CurrentView=view.strip("()").split(",")
            elif (re.match(r".*,.*",view)):
               self._CurrentView=view.split(",")
      return(self._CurrentView)

   def setCurrentOrder(self,order): 
      if (isinstance(order,list)):
         self._CurrentOrder=order
      if (isinstance(order,str)):
         if (order == "(NONE)"):
            self._CurrentOrder="[NONE]"
         else:
            if (re.match(r"^\(.?\)$",order)):
               self._CurrentOrder=order.strip("()").split(",")
            elif (re.match(r".*,.*",view)):
               self._CurrentOrder=order.split(",")
      return(self._CurrentOrder)

   def addFields(self,*fldObjList): 
      for fldObj in fldObjList:
         fldObj._parent=weakref.ref(self)
         name=fldObj.name
         if (name in self._Field):
            raise ValueError(
               f"ERROR: field name={name} already registered"
            )
         else:
            self._Field[name]=fldObj
            if ("insertafter" in fldObj._initParam and 
                fldObj._initParam["insertafter"] in self._FieldOrder):
               idx = self._FieldOrder.index(fldObj._initParam["insertafter"])
               self._FieldOrder.insert(idx + 1, name)
            else:
               self._FieldOrder.append(name)
            for group in fldObj.group:
               if group not in self._GroupOrder:
                  self._GroupOrder.append(group)
      for fldObj in fldObjList:
         fldObj.__2nd__init__()

   def getIdField(self):
      for fldObj in self._Field.values():
          if (fldObj["type"] == "FieldId"):
             return(fldObj)
      return(None) 

   def getIdFieldName(self):
      fldObj=self.getIdField()
      return(fldObj.name if (fldObj) else None)

   def do():
       print("WARN: not derevied method call do():")
       return(False)

   def getDictList(self,view=None,filterExpr=None):

      if (not view is None):
         self.setCurrentView(view) 
      if (len(self._CurrentOrder) == 0): # means no order defined
         self.setCurrentOrder(self._CurrentView)
      if (not filterExpr is None):
         self.setFilter(filterExpr)

      result={}
      result["data"]=[]
    
      if (self.query()):
         while True:
           row=self.get_next()
           if row is None: break
           #result["data"].append(dict(row))
           result["data"].append(row)
      else:
         print("DB Error: %s" % self.lastError())

      return(result["data"])

   def countRecords(self) -> int:
      return(self.countRecordsSoft())

   def countRecordsSoft(self) -> int:
      n=0
      if (self.query()):
         while True:
           row=self.get_next()
           if row is None: break
           n+=1
      return(n)

   def insertRecord(self, record_id: int, data: dict) -> bool:
       return True

   def updateRecord(self, record_id: int, new_data: dict) -> bool:
       self.records[record_id].update(new_data)
       print(f"Datensatz {record_id} erfolgreich aktualisiert.")
       return True

   def deleteRecord(self, record_id: int) -> bool:
       print(f"Datensatz {record_id} erfolgreich geloescht.")
       return True

   def lastError(self):
      return(self._lastError)


