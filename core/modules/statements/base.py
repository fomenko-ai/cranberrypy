import ast
from typing import Any


class Base:

    def __init__(self, statement):
        self.statement = statement
        self.value = statement.value if hasattr(statement, 'value') else None
        self.has_call = False
        self.has_method_call = False
        self.has_class_call = False
        self.call_names = None

    def _parse(self):
        raise NotImplementedError

    def check_method_call(self, value):
        if hasattr(value.func, 'attr') and isinstance(value.func.attr, str):
            if value.func.attr[0].islower():
                self.has_method_call = True
            else:
                self.check_class_call(value.func.attr)

    def check_class_call(self, call: str):
        if isinstance(call, str)\
                and call[0].isupper()\
                and not self.has_method_call:
            self.has_class_call = True

    def recursion_class_call_scan(self, value: Any, count=0):
        if count == 20:
            return None
        else:
            count += 1
        if isinstance(value, ast.Name):
            return value.id
        elif hasattr(value, 'value') and isinstance(value.value, ast.Name):
            return value.value.id
        elif hasattr(value, 'func'):
            if isinstance(value.func, ast.Name) and\
                    hasattr(value.func, 'id'):
                self.check_class_call(value.func.id)
                return value.func.id
            elif isinstance(value.func, ast.Attribute) and\
                    hasattr(value.func, 'value'):
                self.check_method_call(value)
                return self.recursion_class_call_scan(value.func.value, count)
