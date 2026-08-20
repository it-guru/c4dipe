from config import config
import json
import dbpool
from datetime import datetime, timezone

from kernel.field   import *
from kernel.dataobj import *

from kernel.condition import *
from logger import *

from pprint import pformat, pprint


def _urlofcurrentrec_decodeRaw(self,dbRec,rawVal):
   idFldName=dbRec._parent.getIdFieldName()
   return(f"virtual val idfield={idFldName}")

class BaseContact(DataObjSQLDB):
   def __init__(self):
      super().__init__()
      self._configSection       = "BASE"
      self._primaryBackendTable = "contact"

      self.addFields(
         FieldText(
            name      = "fullname",
            label     = "fullqualified name"
         ),
         FieldText(  
            name      = "surname",
            label     = "fullqualified name"
         ),
         FieldText(  
            name      = "virtual",
            label     = "virtual full",
            decodeRaw = _urlofcurrentrec_decodeRaw
         ),
         FieldSubList(  
            name      = "groups",
            label     = "Groups",
            vjointo   = "base.grp",
            vjoinon   = ["userid","grpid"],
            vjoindisp = ["fullname","mdate","grpid"],
         ),
         FieldId(  
            name      = "userid"
         ),
         FieldRecordURL(),
         FieldMDate()
      )






