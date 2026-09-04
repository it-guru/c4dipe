from kernel.field   import *
from kernel.dataobj import *

from httpAuth.Tardis import HttpAuthTardis

import re
from pprint import pprint, pformat
from logger import logger


class SmnowCmdb_ci_server(DataObjServiceNow, HttpAuthTardis):
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


