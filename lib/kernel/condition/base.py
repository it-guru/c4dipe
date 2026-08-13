import re
import json
from typing import Dict, List, Tuple, Any, Union, Optional
from kernel.field import *
import weakref

# =========================================================================
# 1. AST / Intermediate Representation (Language-Agnostic Tree)
# =========================================================================


class ConditionASTNode:
   def to_dict(self):
      raise NotImplementedError()


class ConditionExprNode(ConditionASTNode):
   def __init__(self,
                field: str, 
                operator:str, 
                value: str,
                fldobj:Dict, 
                is_literal:bool = False,
                negation:bool = False
      ):
      self.fldobj = fldobj
      self.field = field
      self.operator = operator  # "=" or "LIKE"
      self.negation = negation 
      self.value = value
      self.is_literal = is_literal 

   def to_dict(self):
      return({
         "type": "Condition",
         "field": self.field,
         "fldobj": self.fldobj,
         "operator": self.operator,
         "value": self.value,
         "is_literal": self.is_literal,
         "negation": self.negation
      })


class ConditionLogicalNode(ConditionASTNode):
   def __init__(self, op: str, children: List[ConditionASTNode]):
      self.op = op.upper()  # "AND" or "OR"
      self.children = children

   def to_dict(self):
      return {
         "type": "Logical",
         "op": self.op,
         "children": [child.to_dict() for child in self.children]
      }



# =========================================================================
# 2. Parsing Logic (Input Data -> AST)
# =========================================================================

_WLD_CHUNK_RE=re.compile(r'(\\\\|\\\*|\\\?|\\%|\\_|\*|\?|%|_|\\|.)',re.DOTALL)
_TOKEN_STR_RE=re.compile(r"'[^']*'|\"[^\"]*\"|\S+")


def _apply_wildcard_rules(raw_val: str) -> Tuple[str, str, bool]:
   """
   Rules:
   - Unescaped '*' converts to '%' (triggers LIKE)
   - Unescaped '?' converts to '_' (triggers LIKE)
   - Escaped wildcards (\*, \?, \%, \_) are treated as literal characters
   - Unescaped % and _ are escaped to \% and \_ for SQL LIKE safety
   """
   compop="="

   negation=False

   if raw_val.startswith("!"):
      negation=True
      raw_val=re.sub(r"^.\s*","",raw_val)

   if raw_val.startswith("="):
      compop="="
      raw_val=re.sub(r"^.\s*","",raw_val)
   if raw_val.startswith(">"):
      compop=">"
      raw_val=re.sub(r"^.\s*","",raw_val)
   elif raw_val.startswith("<"):
      compop="<"
      raw_val=re.sub(r"^.\s*","",raw_val)

   chunks = _WLD_CHUNK_RE.findall(raw_val)
   has_active_wildcard = False
   like_chars = []
   eq_chars = []

   for chunk in chunks:
       if chunk == '*':
           has_active_wildcard = True
           like_chars.append('%')
       elif chunk == '?':
           has_active_wildcard = True
           like_chars.append('_')
       elif chunk == r'\*':
           like_chars.append('*')
           eq_chars.append('*')
       elif chunk == r'\?':
           like_chars.append('?')
           eq_chars.append('?')
       elif chunk == r'\%':
           like_chars.append(r'\%')
           eq_chars.append('%')
       elif chunk == r'\_':
           like_chars.append(r'\_')
           eq_chars.append('_')
       elif chunk == r'\\':
           like_chars.append(r'\\')
           eq_chars.append('\\')
       elif chunk == '%':
           like_chars.append(r'\%')
           eq_chars.append('%')
       elif chunk == '_':
           like_chars.append(r'\_')
           eq_chars.append('_')
       elif chunk == '\\':
           like_chars.append(r'\\')
           eq_chars.append('\\')
       else:
           like_chars.append(chunk)
           eq_chars.append(chunk)

   if has_active_wildcard:
       return "LIKE", "".join(like_chars), negation
   else:
       return compop, "".join(eq_chars), negation


def parse_fld_val(field:str,raw_value:Any,fldobj:Dict)->Optional[ConditionASTNode]:

   if raw_value is None:
      return None

   # Rule: Value is a List -> Process elements as constants (=), OR-connected
   if isinstance(raw_value, list):
      conds=[
         ConditionExprNode(field,"=",str(item),fldobj,is_literal=True)
         for item in raw_value if item is not None and str(item).strip() != ""
      ]
      if not conds:
         return None
      return ConditionLogicalNode("OR",conds) if len(conds)>1 else conds[0]

   # Rule: Value is a String
   value_str = str(raw_value).strip()
   if not value_str:
      return None


   if (isinstance(fldobj,FieldDate)):
      if (not value_str.startswith('"') and not value_str.startswith("'")):
         value_str='"'+value_str+'"'

   tokens = _TOKEN_STR_RE.findall(value_str)
   conds = []

   for token in tokens:
      # Single-quoted string -> Exact match (=), no wildcard processing
      if token.startswith("'") and token.endswith("'") and len(token) >= 2:
         clean_val = token[1:-1]
         conds.append(ConditionExprNode(field,"=",clean_val,fldobj,is_literal=True))
      else:
         # Double-quoted or unquoted token -> Process wildcards
         if token.startswith('"') and token.endswith('"') and len(token) >= 2:
             raw_token_val = token[1:-1]
         else:
             raw_token_val = token

         sql_op, param_val, negation = _apply_wildcard_rules(raw_token_val)
         conds.append(ConditionExprNode(field,sql_op,
                                    param_val,
                                    fldobj,
                                    is_literal=False,
                                    negation=negation)
         )

   if not conds:
       return None

   return ConditionLogicalNode("OR",conds) if len(conds) > 1 else conds[0]


def parse_dict(d: Dict[str, Any],fldmap: Dict) -> Optional[ConditionASTNode]:
    fld_nodes = []
    for fld,raw_val in d.items():
       if (not fld in fldmap): 
          fldmap[fld]={"type":"String"}
       node=parse_fld_val(fld,raw_val,fldmap[fld])
       if node:
          fld_nodes.append(node)

    if not fld_nodes:
       return None

    return ConditionLogicalNode("AND",fld_nodes) if len(fld_nodes)>1 else fld_nodes[0]


def build_ast(
    criteria:Union[Dict[str,Any],List[Dict[str,Any]],List[List[Dict[str,Any]]]],
    fieldmap:Dict[str,Dict]
   ) -> Optional[ConditionASTNode]:
    """
    Normalizes the input structure into 2D List and builds the AST:
    - Level 1 (Outer List): AND-connected
    - Level 2 (Inner List): OR-connected
    """
    if isinstance(criteria, dict):
        normalized = [[criteria]]
    elif isinstance(criteria, list):
        if not criteria:
            return None
        if isinstance(criteria[0], dict):
            normalized = [[d] for d in criteria]
        elif isinstance(criteria[0], list):
            normalized = criteria
        else:
            raise ValueError("Unsupported list element type.")
    else:
        raise ValueError("Input criteria must be a dict, " \
                         "list of dicts, or 2D list of dicts.")

    level1_nodes = []

    for level2_list in normalized:
        level2_nodes = []
        for d in level2_list:
            node = parse_dict(d,fieldmap)
            if node:
                level2_nodes.append(node)

        if level2_nodes:
            if len(level2_nodes)>1:
               group_node=ConditionLogicalNode("OR",level2_nodes)
            else:
               group_node=level2_nodes[0]
            level1_nodes.append(group_node)

    if not level1_nodes:
        return None

    if (len(level1_nodes) > 1):
       return(ConditionLogicalNode("AND",level1_nodes))

    return(level1_nodes[0])


######################################################################


class ConditionalAST():
   def __init__(self,parent,filterExpr):
      self._AST=build_ast(filterExpr,parent._Field)

   def getAST(self):
      return(self._AST)



__all__ = [k for k in locals() if k.startswith("Condition")]



