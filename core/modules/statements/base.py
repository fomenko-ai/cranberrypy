import ast


class Base:

    def __init__(self, statement):
        self.value = statement.value
        self.has_call = False
        self.call_names = None

    def __parse(self):
        raise NotImplementedError

    def recursion_class_call_scan(self, value):
        if isinstance(value.func, ast.Name):
            return value.func.id
        elif isinstance(value.func, ast.Attribute):
            return self.recursion_class_call_scan(value.func.value)
