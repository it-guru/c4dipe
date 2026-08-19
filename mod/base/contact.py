from config import config
import json
import dbpool
from datetime import datetime, timezone

from kernel.field   import *
from kernel.dataobj import *

from kernel.condition import *
from logger import *

from pprint import pformat, pprint

class BaseContact(DataObjSQLDB):
    def __init__(self):
       super().__init__()
       self._configSection = "BASE"
       self.is_connected = False
       self._currentResultSet = None
       self.addFields(
          FieldText(
             name="fullname"
          ),
          FieldText(  
             name="name"
          ),
          FieldText(  
             name="grpid"
          ),
#          FieldURL(
#             name="urlofcurrentrec"
#          ),
          FieldMDate()
       )




