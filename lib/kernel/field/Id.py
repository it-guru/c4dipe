from kernel.field.base import Field

class FieldId(Field):
   def __init__(self, **param):
      param["selectfix"]=True
      super().__init__(**param)


