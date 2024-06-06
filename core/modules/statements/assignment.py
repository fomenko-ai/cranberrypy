import logging
import ast

from core.modules.statements.base import Base


class Assignment(Base):
    def __init__(self, assign: ast.Assign):
        super().__init__(assign)
        self.targets = assign.targets
        self.variable_names = None
        self.is_constant = False

        self.__parse()

    def __parse(self):
        if self.variable_names is None:
            self.variable_names = []
        if self.call_names is None:
            self.call_names = []

        for target in self.targets:
            if isinstance(target, ast.Attribute):
                self.variable_names.append(target.attr)
        if isinstance(self.value, ast.Constant):
            self.is_constant = True
        elif isinstance(self.value, ast.Call):
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
