from kernel.field.base import Field

class FieldURL(Field):
   def __init__(
                self, 
                **param
               ):
      param["backendname"]=None
      super().__init__(**param)
      self.backendname=None


