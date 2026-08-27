from config import *
from event  import event
from kernel import *
from logger import logger
from pathlib import Path


class Event(event):
   def run(self):
      dataobjname="base.cistatus"
      o=getModuleObject(dataobjname)
      if (o is None):
         return({"status": "failed",
           "exitcode": -1,
           "exitmsg": "failed to instance "+dataobjname
         })

      logger.debug(f"{Path(__file__).name}: start")

      logger.debug(f"Count(0)={str(o.countRecords())}")
      o.limit(3)
      logger.debug(f"Count(3)={str(o.countRecords())}")
      #o.setCurrentOrder("(NONE)")

      result=o.getDictList("(ALL)")

      return({"status": "success","exitcode": 0,"result": result})

     





