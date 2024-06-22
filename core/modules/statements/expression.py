import logging
import ast

from core.modules.statements.base import Base


class Expression(Base):
    def __init__(self, expr: ast.Expr):
        super().__init__(expr)
        self.__parse()

    def __parse(self):
        if self.call_names is None:
            self.call_names = []

        if isinstance(self.value, ast.Call):
            self.has_call = True
            if isinstance(self.value.func, ast.Name):
                self.call_names.append(self.value.func.id)
            elif isinstance(self.value.func, ast.Attribute):
                try:
                    self.call_names.append(
                        self.recursion_class_call_scan(self.value)
                    )
                except Exception as e:
                    logging.error(e)
