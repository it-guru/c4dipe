import re
from kernel.field.base import Field

class FieldDate(Field):
   def __init__(self, **param):
      super().__init__(**param)

   def prepConditionBlock(self,condStr: str) -> str :
      dx=re.compile(r"^(\d{1,2}).(\d{1,2}).(\d{2,4})\s+(\d{2}):(\d{2}):(\d{2})$")
      match=dx.match(condStr)
      if (match):
         condStr="%04d-%02d-%02d %02d:%02d:%02d" % (
                   int(match.group(3)),
                   int(match.group(2)),
                   int(match.group(1)),
                   int(match.group(4)),
                   int(match.group(5)),
                   int(match.group(6)))
      
      return(condStr)



