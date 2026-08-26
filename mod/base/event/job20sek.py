from config import *
from event  import event
from kernel import *


class Event(event):
   def run(self):
      o=getModuleObject("base.contact")
      if (o is None):
         return({"status": "failed",
           "exitcode": -1,
           "exitmsg": "failed to instance base.contact"
         })

      min_search_crit={
        "surname": "vog*",
        "givenname": "h*",
        "cistatusid": [3,4,5]
      }

#      search_criteria=[[ min_search_crit]]

#      o.setFilter([min_search_crit])
      o.limit(5)

      result=o.getDictList(
          "fullname,mdate,name,surname,givenname,urlofcurrentrec,virtual,groups",
          min_search_crit
      )

      return({"status": "success","exitcode": 0,"result": result})

     





