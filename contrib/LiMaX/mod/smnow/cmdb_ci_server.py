from kernel.field   import *
from kernel.dataobj import *


# fuer den Web-Request
from config import config
import http.client
import json
import urllib.error
import urllib.request
import base64
import time

import re
from pprint import pprint


class SmnowCmdb_ci_server(DataObjTardis):
   _configSection          = "SMNOW"
   _primaryBackendTable    = "cmdb_ci_server"
 
   _tardis_token           = None

   name             = FieldText(
      backendname          = "name",
      label                = "name"
   )
   sys_id           = FieldId(
      backendname          = "sys_id",
      label                = "SYSID"
   )


   def rawDataCollect(self):
      Authorization=self._getTardisToken(self._configSection)
      dataBuffer=[]

      Authorization=self._getTardisToken(self._configSection)
      dataobjconnect=config[self._configSection]["DATAOBJCONNECT"]
      requestURL=f'{dataobjconnect}/get/{self._primaryBackendTable}'
      #print(f"request {requestURL}")
      self._subDataCollectLoopCount+=1
      if (self._subDataCollectLoopCount>10):
         print("to many requests; break")
         return([])
      reqParam=urllib.parse.urlencode({
         "pageSize"   : 50,
         "pageNumber" : self._pageNumber
      })
      requestURL=requestURL+'?'+reqParam
      print("requestURL=%s" % requestURL)
      req = urllib.request.Request(
         requestURL,
         method="GET",
         data="grant_type=client_credentials".encode("utf-8")
      )
      req.add_header("Authorization", Authorization)
      req.add_header("User-Agent",    "C4Request/1.0")
      req.add_header("Content-Type",  "application/x-www-form-urlencoded")
      
      no_proxy_handler = urllib.request.ProxyHandler({})
      opener = urllib.request.build_opener(no_proxy_handler)
      with opener.open(req, timeout=5) as response:
         charset = response.headers.get_content_charset(failobj="utf-8")
         result_text = response.read().decode(charset)
         r = json.loads(result_text)
         data=r.get("data",[])
         dataBuffer.extend(data)
         if (len(data)==0):
            print("no records in data")
            return([])
         paging=r.get("paging",None)
         if (paging):
            self._nextPage=paging.get("nextPage")
            if (self._pageNumber==1):
               maxPages=paging.get("maxPages")

         # prepare next request
         if (self._nextPage):
            self._pageNumber=self._nextPage
         else:
            return([])
                  
      return(dataBuffer)

