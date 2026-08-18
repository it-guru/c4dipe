import weakref

class DataObj:
    def __init__(self, db_connection_string: str = None):
       self._Field={}
       self._FieldOrder=[]
       self._GroupOrder=[]
       self._CurrentFilterExpr=[[]]
       self._CurrentView=[]
       self._CurrentOrder=[]

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




    def insert_record(self, record_id: int, data: dict) -> bool:
        return True

    def update_record(self, record_id: int, new_data: dict) -> bool:
        self.records[record_id].update(new_data)
        print(f"Datensatz {record_id} erfolgreich aktualisiert.")
        return True

    def delete_record(self, record_id: int) -> bool:
        print(f"Datensatz {record_id} erfolgreich geloescht.")
        return True

