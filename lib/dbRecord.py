import json

class dbRecord(dict):
   def __init__(self,initraw=None):
      super().__init__()
      self._raw={}
      self._keys=['fullname','modifydate']

      if (initraw):
         self._raw=initraw

   def _generate(self, key):
      if key in self._raw:
         return(self._raw[key])
      raise KeyError(key)

   def __getitem__(self, key):
       return self._generate(key)

   def __contains__(self, key):
       return key in self._keys

   def __iter__(self):
       return iter(self._keys)

   def __len__(self):
       return len(self._keys)

   def get(self, key, default=None):
       if key in self:
           return self[key]
       return default

   def keys(self):
       return list(self._keys)

   def values(self):
       return [self[k] for k in self._keys]

   def items(self):
       return [(k, self[k]) for k in self._keys]
      
