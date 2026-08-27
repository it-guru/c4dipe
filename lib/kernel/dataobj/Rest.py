from .Static import DataObjStatic
from rawRec import rawRec
from kernel.condition import *
from logger import *

from datetime import datetime, timezone

from pprint import pformat, pprint

class DataObjRest(DataObjStatic):
    def __init__(self):
       super().__init__()
       self._rawData=[] 

    def rawDataCollect(self):
       return([])


