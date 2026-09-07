from config import *
from event  import event
from kernel import *
from logger import logger
from pathlib import Path

from nls import NLSManager
_ = NLSManager(__file__)


class Event(event):
   def run(self):
      logger.debug("circularEvent: "+_.f("hello world"))

      dataobjname="smnow.cmdb_ci_server"
      o=getModuleObject(dataobjname)
      if (o is None):
         return({"status": "failed",
           "exitcode": -1,
           "exitmsg": "failed to instance "+dataobjname
         })

      o.setFilter({})
      o.setCurrentView("(ALL)")
      o.setCurrentOrder(["mdate"])
      o.limit(2000,140)
      if (o.query()):
         while True:
           row=o.get_next()
           if row is None: break
           logger.info("REC: %06d sys_id='%s' mdate='%s' name='%s'" % (int(row["recno"]),row["sysid"],row["mdate"],row["name"]))


      return({"status": "success","exitcode": 0})

     





