import os
import sys
from pathlib import Path
import importlib.util
import types
from config import config

__all__ = ['funktion1', 'ist_pid_aktiv', 'importToNamespace','getModuleObject']

def funktion1():
    print("Ich wurde automatisch exportiert!")

def funktion2():
    print("Ich auch!")

def interne_funktion():
    print("Ich bleibe drauen (wie ein fehlendes Element in @EXPORT)")

def ist_pid_aktiv(pid):
   if pid <= 0:
      return False
   try:
      os.kill(pid, 0)
   except OSError:
      return False
   else:
      return True



def importToNamespace(file_path,target_namespace_str):

    if not os.path.exists(file_path):
       raise FileNotFoundError(f"The file {file_path} does not exist.")

    if target_namespace_str in sys.modules: 
       return sys.modules[target_namespace_str]


    parts = target_namespace_str.split('.')
    current_path = []
    
    for part in parts:
       current_path.append(part)
       current_ns = ".".join(current_path)
       if current_ns not in sys.modules:
          sys.modules[current_ns]=types.ModuleType(current_ns)
          if len(current_path) > 1:
             parent_ns=".".join(current_path[:-1])
             setattr(sys.modules[parent_ns],part,sys.modules[current_ns])
             
    # This is our actual target module object now
    target_namespace = sys.modules[target_namespace_str]


    module_name = os.path.basename(file_path).replace('.py', '')

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not create spec for {file_path}")

    temp_module = importlib.util.module_from_spec(spec)
    
    spec.loader.exec_module(temp_module)

    attributes = getattr(temp_module, '__all__', [attr for attr in dir(temp_module) if not attr.startswith('_')])
    
    for attr in attributes:
        #print(f"attr={attr}")
        value = getattr(temp_module, attr)
        setattr(target_namespace, attr, value)

    #print(f"target_namespace={target_namespace}")
    return target_namespace




def getModuleObject(module: str, dataobj: str):
  search_paths = [
      Path(f"/home/a295897/src/c4dipe/mod/{module}/{dataobj}.py"),
      Path(f"/opt/{module}/{dataobj}.py"),
      Path(f"/usr/{module}/{dataobj}.py"),
  ]
  # todo: Implement search path for dataobjs

  target_file = next((p for p in search_paths if p.is_file()), None)

  #print("target file=%s" % target_file)
  if not target_file:
    return None

  mod_name = f"dyn_mod_{module}_{dataobj}"
  class_name = (
      f"{module[0].upper()}{module[1:]}{dataobj[0].upper()}{dataobj[1:]}"
  )

  try:
    if mod_name in sys.modules:
       mod = sys.modules[mod_name]
       cls = getattr(mod, class_name)
       return cls()


    spec = importlib.util.spec_from_file_location(mod_name, target_file)
    if spec is None or spec.loader is None:
      return None

    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)

    cls = getattr(mod, class_name)

    return cls()

  except Exception as e:
    print(f"[ERROR] Failed to load '{class_name}' from '{target_file}': {e}")
    return None


