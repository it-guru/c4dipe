class Field(dict):
   def __init__(self, **param):
      self.name=param["name"]
      if "backendname" not in param: param["backendname"]=param["name"]
      if "group" not in param:       param["group"]="default"
      if not isinstance(param["group"],list): param["group"]=[param["group"]]

      self.backendname=param["backendname"]
      self.group=param["group"]
      self._initParam=param
      self._parent=None
      self["name"]=self.name
      self["type"]=type(self).__name__


