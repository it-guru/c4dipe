from .base import DataObj

from .SQLDB   import DataObjSQLDB
from .Static  import DataObjStatic
from .Rest    import DataObjRest
from .Tardis  import DataObjTardis
from .Elastic import DataObjElastic

__all__ = [k for k in locals() if k.startswith("DataObj")]



