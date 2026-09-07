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


      sys=getModuleObject("lima::system")
      if (sys is None):
         return({"status": "failed",
           "exitcode": -1,
           "exitmsg": "failed to instance lima::system"
         })



      dataobjname="smnow.cmdb_ci_server"
      o=getModuleObject(dataobjname)
      if (o is None):
         return({"status": "failed",
           "exitcode": -1,
           "exitmsg": "failed to instance "+dataobjname
         })

      o.setFilter({"mdate": ">2026-06-01 18:15:03"})
      o.setCurrentView("(ALL)")
      o.setCurrentOrder(["mdate"])
      o.limit(20)
      if (o.query()):
         while True:
           row=o.get_next()
           id=o.createUniqueId()
           if row is None: break
           if (id):
              logger.info("REC: ID=%s" % str(id))
           logger.info("REC: %06d sys_id='%s' mdate='%s' name='%s'" % (int(row["recno"]),row["sysid"],row["mdate"],row["name"]))
           sys.setFilter({"sysid": [row["sysid"]]})
           r=sys.getDictList("(ALL)")
           if (not len(r)):
              print("id %s not found" % row["sysid"])
              newrec={
                 "name": row["name"],
                 "sysid": row["sysid"]
              }
              newid=sys.validatedInsertRecord(newrec)


      return({"status": "success","exitcode": 0})

     





