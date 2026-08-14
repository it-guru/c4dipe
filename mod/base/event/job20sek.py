from config import *
from event  import event


class localEvent(event):
   def __init__(self):
      print(f"just do somethin in {__file__}")
      super().__init()







def process():
   e=localEvent()
   return(None)

process()




