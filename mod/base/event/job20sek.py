from config import *
from event  import event
from kernel import *


class Event(event):
   def __init__(self):
      #print(f"Construct Event in {__file__}")
      super().__init__()

   def run(self):
      #print(f"run {__file__}")
      o=getModuleObject("base.contact")
      if (o is None):
         return({"status": "failed",
           "exitcode": -1,
           "exitmsg": "failed to instance base.contact"
         })

      search_criteria=[
         [
           {
              "name": "a*"
           }
         ]
      ]

      #pprint(search_criteria)

      o.setFilter(search_criteria)

      result=o.getDictList("fullname,mdate,name,urlofcurrentrec,virtual,groups")

      return({"status": "success","exitcode": 0,"result": result})

     





