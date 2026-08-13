import re
from typing import Dict, List, Tuple, Any, Union, Optional

from kernel.condition import *

class ConditionSQL:

    def __init__(self):
        self.params = {}
        self.param_counter = 0

    def _generate_param_name(self, field: str) -> str:
        self.param_counter += 1
        clean_field = re.sub(r'\W+', '_', field)
        return f"{clean_field}_{self.param_counter}"

    def compile(self, node: Optional[ConditionASTNode]) -> Tuple[str, Dict[str, Any]]:
        if not node:
            return "", {}

        sql_body = self._visit(node)
        if not sql_body:
            return "", {}

        return f"WHERE {sql_body}", self.params

    def _visit(self, node: ConditionASTNode) -> str:
        if isinstance(node, ConditionExprNode):
            param_name = self._generate_param_name(node.field)
            self.params[param_name] = node.value
            return f"{node.field} {node.operator} :{param_name}"

        elif isinstance(node, ConditionLogicalNode):
            child_sqls = [self._visit(child) for child in node.children]
            child_sqls = [s for s in child_sqls if s]

            if not child_sqls:
                return ""

            if len(child_sqls) == 1:
                return child_sqls[0]

            joined = f" {node.op} ".join(child_sqls)
            return f"({joined})"

        return ""


def build_where_clause(
    criteria: Union[Dict[str, Any], List[Dict[str, Any]], List[List[Dict[str, Any]]]]
) -> Tuple[str, Dict[str, Any]]:
    """Main entry point for SQL WHERE clause generation."""
    ast = build_ast(criteria)
    compiler = Compiler()
    return compiler.compile(ast)

