import weakref
from kernel.field import *

class DataObj:
   def __init__(self, db_connection_string: str = None):
      self._Field={}
      self._FieldOrder=[]
      self._GroupOrder=[]
      self._CurrentFilterExpr=[[]]
      self._CurrentView=[]
      self._CurrentOrder=[]
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
      self._CurrentFilterExpr=filterExpr
      return(True) 

   def secureSetFilter(self,filterExpr):
      return(self.setFilter(filterExpr))

       
   def setCurrentView(self,view): 
      if (isinstance(view,list)):
         self._CurrentView=list
      if (isinstance(view,str)):
         if (view == "(ALL)"):
            self._CurrentView=self._FieldOrder
         else:
            self._CurrentView=view.split(",")
      return(self._CurrentView)

   def setCurrentOrder(self,order): 
      if (isinstance(order,list)):
         self._CurrentOrder=list
      if (isinstance(order,str)):
         self._CurrentView=order.split(",")
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

#      self._CurrentAST=ConditionalAST(self._CurrentFilterExpr,self._Field)
#      ASTprocessor=ConditionSQL()
#      wherestr,qparam=ASTprocessor.compile(self._CurrentAST.getAST())
#
#      selLst=[]
#      for fldname in self._CurrentView: 
#         backendname=self._Field[fldname].backendname
#         if (not backendname is None):
#            aliasname=fldname
#            selLst.append(backendname+' AS "'+aliasname+'"')
#
#      self._lastSQL="select "+", ".join(selLst)+" "\
#                    "from grp "+\
#                    "where "+wherestr+" limit 10"
#      logger.debug("SQL: "+pformat(self._lastSQL))
      result={}
      result["data"]=[]
    
      if (self.do()):
         while True:
           row=self.get_next()
           if row is None: break
           #result["data"].append(dict(row))
           result["data"].append(row)
      else:
         print("DB Error: %s" % self.lastError())

      return(result["data"])




   def insert_record(self, record_id: int, data: dict) -> bool:
       return True

   def update_record(self, record_id: int, new_data: dict) -> bool:
       self.records[record_id].update(new_data)
       print(f"Datensatz {record_id} erfolgreich aktualisiert.")
       return True

   def delete_record(self, record_id: int) -> bool:
       print(f"Datensatz {record_id} erfolgreich geloescht.")
       return True

   def lastError(self):
      return(self._lastError)


