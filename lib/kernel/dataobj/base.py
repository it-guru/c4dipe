import weakref
import re
from kernel.field import *
from kernel.condition import *
from pprint import pprint, pformat
from logger import logger

import http.client
import socket
import resource
import urllib.request
import urllib.error
import json

from flask import g, has_request_context

import copy

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
      self._CurrentAST=None
      self._CurrentView=[]
      self._CurrentOrder=[]

      self._lastError=None

      self._limitResult=0
      self._limitStart=0
      self._limitSoft=False   # False means limit by backend

      if (hasattr(self, "_class_fields")):
         self.addFields(*self._class_fields)
      super().__init__()


   def __init_subclass__(cls, **kwargs):
      super().__init_subclass__(**kwargs)
      
      cls._class_fields = []

      for attr_name, attr_value in list(cls.__dict__.items()):
         if isinstance(attr_value, Field):
            if not getattr(attr_value, "name", None):
                attr_value.name = attr_name
            cls._class_fields.append(attr_value)


   def setFilter(self,filterExpr):
      logger.debug("base: setFilter: "+pformat(filterExpr))
      if (isinstance(filterExpr,dict)):
         self._CurrentFilterExpr=[[filterExpr]]
      elif (isinstance(filterExpr,list)):
         haveSubDict=False
         for subEnt in filterExpr:
            if (isinstance(subEnt,dict)):
               haveSubDict=True
         if (haveSubDict):
            self._CurrentFilterExpr=[filterExpr]
         else:
            self._CurrentFilterExpr=filterExpr
      else:
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
            if (re.match(r"^\(.+\)$",order)):
               self._CurrentOrder=order.strip("()").split(",")
            elif (re.match(r",",order)):
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

   # Delete Validation

   def validateDelete(self,oldrec: dict):
      return(False)


   # Update/Insert Validation

   def preValidate(self,oldrec: dict, newrec: dict, orgRec: dict):
      # validate BEFORE fieldValidate
      return(False)

   def validate(self,oldrec: dict, newrec: dict, orgRec: dict):
      # validate AFTER fieldValidate
      return(False)



   def insertRecord(self,newrec: dict) -> str:
       return True

   def validatedInsertRecord(self, newrec: dict) -> str:
      orgNewRec=copy.deepcopy(newrec)
      
      # do field validate (with posible field-value changes)

      # check security
      if (has_request_context() and \
          g.getattr("isWebUIRequest",False)):
         print("WebUI validatedInsertRecord")

      if (self.validate(None,newrec,orgNewRec)):
         return(self.insertRecord(newrec,orgNewRec))
      return(None)



   def updateRecord(self, oldrec: dict, newrec: dict, orgRec: dict):
       return True

   def validatedUpdateRecord(self, oldrec: dict,newrec: dict, filter: dict) -> str:
      orgNewRec=copy.deepcopy(newrec)
      
      # do field validate (with posible field-value changes)

      # check security
      if (has_request_context() and \
          g.getattr("isWebUIRequest",False)):
         print("WebUI validatedInsertRecord")

      if (self.validate(oldrec,newrec,orgNewRec)):
         return(self.updateRecord(oldrec,newrec,orgNewRec))
      return(None)


   def finishUpdateRecord(self, oldrec: dict, newrec: dict, orgRec: dict):
       return True




   def deleteRecord(self, oldrec: dict) -> bool:
       # do validateDelete
       return True




   def lastError(self):
      return(self._lastError)

   def createUniqueId(self):
      logger.debug(f"[createUniqueId] start")
      proxy_handler=urllib.request.ProxyHandler({})
      HttpAgent=urllib.request.build_opener(proxy_handler)

      target=f"http://127.0.0.1:8081"
      result=None

      max_retries = 15 
      retry_delay = 2 
 
      for attempt in range(1, max_retries + 1): 
         try:
            url=f"{target}/config/app/rpcCreateUniqueId"
            req=urllib.request.Request(url,method="GET")
            with HttpAgent.open(req,timeout=3) as response:
                status_code=response.status
                if status_code != 200:
                   self.logger.info(f"[createUniqueId] fail retry")
                   time.sleep(retry_delay)
                   continue
                result=response.read().decode('utf-8')
                break

         except (urllib.error.URLError,
                 http.client.HTTPException,
                 socket.error,
                 ConnectionResetError) as e:
            result = '{"status": "network_error","exitcode": 500}'

         except Exception as e:
            result = '{"status": "unexpected_error","exitcode": 500}'

      r=json.loads(result)
      if r["exitcode"]==0 :
         return(r["UniqueID"])
      else:
         return(None)
      


