from config import *
from event  import event
from kernel import *
from logger import logger
from pathlib import Path


class Event(event):
   def run(self):
      dataobjname="smnow.cmdb_ci_server"
      o=getModuleObject(dataobjname)
      if (o is None):
         return({"status": "failed",
           "exitcode": -1,
           "exitmsg": "failed to instance "+dataobjname
         })

      o.setFilter({"name":"ip*"})
      o.setCurrentView("name,sys_id")
      if (o.query()):
         while True:
           row=o.get_next()
           if row is None: break
           print("Next Row:", end="")
           pprint(row)

      return({"status": "success","exitcode": 0})

     





