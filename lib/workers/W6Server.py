import json
import ctypes
import os
import sys
import time
import threading
from kernel import *
from logger import *
from setproctitle import setproctitle

from config import config

from kernel.condition import *
import kernel.condition.base

from pprint import pformat, pprint





from W6Flask import W6Flask, jsonify, request, current_app, abort

class W6FlaskServer(W6Flask):
   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.UniqueID_rec={
         "counter": 0,
         "UniqueIdPool": [],
         "timer": time.time()
      }
      self.UniqueID_lck=threading.Lock()



app = W6FlaskServer(__name__)
app.plugdir="event"

@app.route('/<AppConfig>/internalTimer')
def internalTimer(AppConfig):
   auth_key = request.headers.get('X-AUTHKEY')
   if not auth_key or auth_key != current_app.W6InternalKey:
      abort(403, description="Access denied. Invalid X-AUTHKEY token.")
   #runTask1(AppConfig) # ensure Task1 is running

#   func=current_app.view_functions["event.runTask1"]
#   with current_app.test_request_context(headers={'X-AUTHKEY': current_app.W6InternalKey}):
#      result = func(AppConfig)
 
   return jsonify({"status":"success","exitcode": 0})


@app.route('/<AppConfig>/getConfig')
def getConfig(AppConfig):
   auth_key = request.headers.get('X-AUTHKEY')
   if not auth_key or auth_key != current_app.W6InternalKey:
      abort(403, description="Access denied. Invalid X-AUTHKEY token.")
 
   return jsonify({
       "status":"success",
       "exitcode": 0,
       "result": config,
   })


@app.route('/<AppConfig>/<module>/event/<evname>/<any(sync,async):mode>', 
           methods=['GET','POST'])
def runEvent(AppConfig,module,evname,mode):
   dataobjname=f"{module}.{evname}"
   auth_key = request.headers.get('X-AUTHKEY')
   print("Got X-AUTHKEY=%s" % auth_key);
   if not auth_key or auth_key != current_app.W6InternalKey:
      abort(403, description="Access denied. Invalid X-AUTHKEY token.")


   return jsonify({"status":"success","exitcode": 0})



@app.route('/<AppConfig>/<module>/<dataobj>/<method>', methods=['GET', 'POST'])
def do_dbcall(AppConfig,module,dataobj,method):
   dataobjname=f"{module}.{dataobj}"
   logger.info(f"call {method} to {dataobjname}")

   o=getModuleObject(module,dataobj)
   if (o is None):
      return jsonify({
                       "status":"failed",
                       "exitcode": -1, 
                       "exitmsg": "ERROR: dataobj {method}/{dataobjname} "\
                                  "failed to instance"
      })

   auth_key = request.headers.get('X-AUTHKEY')

   param=request.values.to_dict()
   search_criteria=[
      [
        param 
      ] 
   ]

   if (not auth_key or auth_key != current_app.W6InternalKey):
      o.secureSetFilter(search_criteria)
   else:
      o.setFilter(search_criteria)

  
   result=o.getDictList() 
                   
   return jsonify({"status":"success","exitcode": 0, "result" : result})









@app.route('/<AppConfig>/info')
def run_fork(AppConfig):
   current_app.logger.info("/info call.")
   W5Shm=None

   for rule in current_app.url_map.iter_rules():
      methoden = ",".join(rule.methods - {'HEAD', 'OPTIONS'})
      # rule.rule = Die URL (z.B. /internal/internalTimer)
      # rule.endpoint = Der Name (z.B. mein_blueprint.internal_timer_func)
      print(f"URL: {rule.rule:<30} | Methoden: {methoden:<15} | Endpoint: {rule.endpoint}")
   print("fifi 01")
   importToNamespace("/home/a295897/src/SNowRepl/xx/test.py","w6base.mymod.test")
   print("fifi 02")



   

   return jsonify({"status":"success","exitcode": 0})
#   with current_app.W6ShmLock:
#      W5Shm=getW6Shm(current_app.W6Shm,current_app.W6ShmSize)
#   return jsonify(W5Shm)

@app.route('/<AppConfig>/rpcGetUniqueId')
def rpcGetUniqueId(AppConfig):
   self=current_app._get_current_object()
   current_app.logger.info("/rpcGetUniqueId call.")
   newID=None
   with self.UniqueID_lck:
     if len(self.UniqueID_rec["UniqueIdPool"])==0 :
        for i in range(9999):
            self.UniqueID_rec["UniqueIdPool"].append("%d09-%04d" % (time.time(),i))
     newID=self.UniqueID_rec["UniqueIdPool"].pop(0)
   return jsonify({"status":"success","exitcode": 0, "UniqueID": newID})


@app.route('/<AppConfig>/runProc')
def runProc(AppConfig):
   self=current_app._get_current_object()
   self.logger.info("/runProc call.")
   try:
       pid = os.fork()
   except OSError as e:
       sys.exit(f"Fork failed: {e}")

   if pid > 0:
       print(f"[Parent] PID {pid} created.")
   else:
       self.post_fork_child_cleanup()
       setproctitle("W6Server: runProc")
       print(f"[Child] PID {os.getpid()} running.")
       try:
           # Hier kommt deine eigentliche Hintergrundarbeit hin
           print("[Child] start async job.")


           ns=importToNamespace("/home/a295897/src/SNowRepl/src/mod/base/contact/__init__.py","BaseContact")


           db=ns.BaseContact("GLOBAL")
           if (db.sql_do("select fullname,grpid from grp limit 10",{})):
              while True:
                row=db.get_next()
                if row is None: break
                print(f"fullname={row['fullname']} row=%s" % json.dumps(row, default=str))
           else:
              print("DB Error: %s" % db.lastError())

           for i in range(10):
              print(f"[Child] job t={i}.")
              if not self.isParentRunning(): 
                 print(f"[Child] Parent died")
                 os._exit(0)
              time.sleep(1) 
           print("[Child] done async job.")
       except Exception as e:
           print(f"[Child] Fehler: {e}")
       finally:
           os._exit(0)



   return jsonify({"status":"success","exitcode": 0})



if __name__ == '__main__':
    app.run(port=8081)


