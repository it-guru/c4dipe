from config import config
from datetime import datetime, timezone
from kernel.field   import *
from kernel.dataobj import *
from kernel.condition import *
from pprint import pformat, pprint

def _urlofcurrentrec_decodeRaw(self,dbRec,rawVal):
   idFldName=dbRec._parent.getIdFieldName()
   return(f"virtual val idfield={idFldName} surname={dbRec['surname']}")

class BaseContact(DataObjSQLDB):
   _configSection          = "BASE"
   _primaryBackendTable    = "contact"

   fullname         = FieldText(
      backendname          = "contact.fullname",
      label                = "fullqualified name"
   )
   surname          = FieldText(  
      backendname          = "contact.surname",
      label                = "fullqualified name"
   )
   virtual          = FieldText(  
      label                = "virtual full",
      depend               = ["surname"],
      decodeRaw            = _urlofcurrentrec_decodeRaw
   )
   groups           = FieldSubList(  
      label                = "Groups",
      vjointo              = "base.grp",
      vjoinon              = ["userid","grpid"],
      vjoindisp            = ["fullname","mdate","grpid"],
   )
   userid           = FieldId(
      backendname          = "contact.userid",
   )
   urlofcurrentrec  = FieldRecordURL()
   mdate            = FieldMDate()






