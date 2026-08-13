import re
from typing import Any, List, Dict, Callable, Optional, Pattern

from kernel.condition import *



def _like_to_regex(like_pattern: str) -> str:
    """Converts a SQL LIKE pattern (with % and _) into a Regex pattern string."""
    tokens = re.findall(r'(\\\\|\\%|\\_|\%|_|.)', like_pattern, re.DOTALL)
    res = []
    for t in tokens:
        if t == '%':
            res.append('.*')
        elif t == '_':
            res.append('.')
        elif t == r'\%':
            res.append(re.escape('%'))
        elif t == r'\_':
            res.append(re.escape('_'))
        elif t == r'\\':
            res.append(re.escape('\\'))
        else:
            res.append(re.escape(t))
    return '^' + ''.join(res) + '$'


class ConditionStatic:
    """Compiles an AST into a high-performance Python matching function."""

    def __init__(self, case_sensitive: bool = True):
        self.case_sensitive = case_sensitive

    def compile(self, ast: Optional[ConditionASTNode]) -> Callable[[Dict[str, Any]], bool]:
        if not ast:
            return lambda d: True

        env = {
            '_check_eq': self._check_eq,
            '_check_like': self._check_like,
            're': re
        }
        regex_counter = 0

        def _build_expr(node: ConditionASTNode) -> str:
            nonlocal regex_counter
            if isinstance(node, ConditionExprNode):
                field_repr = repr(node.field)
                val_repr = repr(node.value)

                if node.operator == "=":
                    return f"_check_eq(d.get({field_repr}), {val_repr})"

                if node.operator == ">":
                    return f"_check_gt(d.get({field_repr}), {val_repr})"

                if node.operator == "<":
                    return f"_check_lt(d.get({field_repr}), {val_repr})"

                if node.operator == ">=":
                    return f"_check_ge(d.get({field_repr}), {val_repr})"

                if node.operator == "<=":
                    return f"_check_le(d.get({field_repr}), {val_repr})"


                elif node.operator == "LIKE":
                    regex_counter += 1
                    reg_key = f"_reg_{regex_counter}"
                    pattern = _like_to_regex(node.value)
                    flags = 0 if self.case_sensitive else re.IGNORECASE
                    env[reg_key] = re.compile(pattern, re.DOTALL | flags)
                    return f"_check_like(d.get({field_repr}), {reg_key})"

            elif isinstance(node, ConditionLogicalNode):
                child_exprs = [_build_expr(child) for child in node.children]
                child_exprs = [e for e in child_exprs if e]
                if not child_exprs:
                    return "True"
                if len(child_exprs) == 1:
                    return child_exprs[0]

                op_str = " and " if node.op == "AND" else " or "
                return f"({op_str.join(child_exprs)})"

            return "True"

        body_expr = _build_expr(ast)
        func_code = f"def matcher(d):\n    return bool({body_expr})"

        # Compile code into executable python function
        exec(func_code, env)
        matcher = env['matcher']
        
        # Attach generated source code string to the function object
        matcher.__source__ = func_code
        return matcher


    @staticmethod
    def _check_eq(val: Any, target: str) -> bool:
        """Fast equality check supporting scalars, ints, and lists in target dicts."""
        if val is None:
            return False
        if val == target:
            return True
        if isinstance(val, list):
            return target in val or any(str(x) == target for x in val)
        return str(val) == target

    @staticmethod
    def _check_gt(val: Any, target: str) -> bool:
        """Greater than (>) check using string comparison."""
        if val is None:
            return False
        if isinstance(val, list):
            return any(str(x) > target for x in val if x is not None)
        return str(val) > target

    @staticmethod
    def _check_ge(val: Any, target: str) -> bool:
        """Greater or equal (>=) check using string comparison."""
        if val is None:
            return False
        if isinstance(val, list):
            return any(str(x) >= target for x in val if x is not None)
        return str(val) >= target

    @staticmethod
    def _check_lt(val: Any, target: str) -> bool:
        """Less than (<) check using string comparison."""
        if val is None:
            return False
        if isinstance(val, list):
            return any(str(x) < target for x in val if x is not None)
        return str(val) < target

    @staticmethod
    def _check_le(val: Any, target: str) -> bool:
        """Less or equal (<=) check using string comparison."""
        if val is None:
            return False
        if isinstance(val, list):
            return any(str(x) <= target for x in val if x is not None)
        return str(val) <= target

    @staticmethod
    def _check_like(val: Any, regex: Pattern) -> bool:
        """Fast LIKE regex check supporting scalars and lists in target dicts."""
        if val is None:
            return False
        if isinstance(val, list):
            return any(regex.match(str(x)) is not None for x in val)
        return regex.match(str(val)) is not None

