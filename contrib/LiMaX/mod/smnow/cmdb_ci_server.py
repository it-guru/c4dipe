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


class SmnowCmdb_ci_server(DataObjStatic):
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
   def _replaceURLPath(self,url,newpath):
      url=re.sub(r'//([^/]+)/.*$', fr'//\1{newpath}', url)
      return(url)

   def _deriveIrisUrl(self,dataurl: str):
      irisPath="/auth/realms/default/protocol/openid-connect/token"
      dataurl=re.sub(r'stargate([\.-])', r'iris\1', dataurl)
      dataurl=self._replaceURLPath(dataurl,irisPath)
      return(dataurl)

   def _getTardisToken(self,configSection: str):
      if (not self._tardis_token is None):
         if (self._tardis_token["create_time"]+
             self._tardis_token["expires_in"]-30 >
             int(time.time())):
            return(self._tardis_token.get("Authorization"))

      dataobjconnect=config[configSection]["DATAOBJCONNECT"]
      dataobjuser=config[configSection]["DATAOBJUSER"]
      dataobjpass=config[configSection]["DATAOBJPASS"]
      #print("DATAOBJCONNECT:%s" % dataobjconnect)
      #print("DATAOBJUSER:%s" % dataobjuser)
      #print("DATAOBJPASS:%s" % dataobjpass)

      requestURL=self._deriveIrisUrl(dataobjconnect)

      req = urllib.request.Request(
         requestURL,
         method="POST",
         data="grant_type=client_credentials".encode("utf-8")
      )
      req.add_header("User-Agent", "C4Request/1.0")
      req.add_header("Content-Type", "application/x-www-form-urlencoded")

      credentials = f"{dataobjuser}:{dataobjpass}"
      b64_credentials=base64.b64encode(credentials.encode("utf-8"))\
                      .decode("utf-8")
      req.add_header("Authorization",f"Basic {b64_credentials}")

      no_proxy_handler = urllib.request.ProxyHandler({})
      opener = urllib.request.build_opener(no_proxy_handler)
      with opener.open(req, timeout=5) as response:
         charset = response.headers.get_content_charset(failobj="utf-8")
         result_text = response.read().decode(charset)
         data = json.loads(result_text)
         data["create_time"]=int(time.time())
         data["Authorization"]=\
            f'{data.get("token_type")} {data.get("access_token")}'
         #pprint(data)
         self._tardis_token=data
         return(self._tardis_token.get("Authorization"))
      return(None)




   def rawDataCollect(self):
      Authorization=self._getTardisToken(self._configSection)
      print(f"1Authorization:{Authorization}")
      print(f"1----")
      dataBuffer=[]
      pageNumber=1
      maxPages=None
      nextPage=None
      loopCount=0
      while True: 
         Authorization=self._getTardisToken(self._configSection)
         dataobjconnect=config[self._configSection]["DATAOBJCONNECT"]
         requestURL=f'{dataobjconnect}/get/{self._primaryBackendTable}'
         print(f"request {requestURL}")
         loopCount+=1
         if (loopCount>10):
            print("to many requests; break")
            break
         reqParam=urllib.parse.urlencode({
            "pageSize"   : 50,
            "pageNumber" : pageNumber
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
               break
            paging=r.get("paging",None)
            if (paging):
               nextPage=paging.get("nextPage")
               if (pageNumber==1):
                  maxPages=paging.get("maxPages")

            # prepare next request
            print("nextPage=%s" % str(nextPage))
            if (nextPage):
               pageNumber=nextPage
            else:
               break
                  



 


      #######################################################################

      pprint(dataBuffer)



      return(dataBuffer)

