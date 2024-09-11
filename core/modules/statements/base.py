import ast


class Base:

    def __init__(self, statement):
        self.statement = statement
        self.value = statement.value
        self.has_call = False
        self.call_names = None

    def _parse(self):
        raise NotImplementedError

    def recursion_class_call_scan(self, value, count=0):
        if count == 20:
            return None
        else:
            count += 1
        if isinstance(value, ast.Name):
            return value.id
        elif hasattr(value, 'value') and isinstance(value.value, ast.Name):
            return value.value.id
        elif hasattr(value, 'func'):
            if isinstance(value.func, ast.Name):
                return value.func.id
            elif isinstance(value.func, ast.Attribute) and\
                    hasattr(value.func, 'value'):
                return self.recursion_class_call_scan(value.func.value, count)
