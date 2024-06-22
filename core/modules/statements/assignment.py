import logging
import ast

from core.modules.statements.base import Base
from core.modules.annotation import Annotation


class Assignment(Base):
    def __init__(self, assign: (ast.Assign or ast.AnnAssign)):
        super().__init__(assign)
        self.targets = None
        self.variable_names = None
        self.annotation = None
        self.is_constant = False

        self.__get_targets()
        self.__parse()

    def __get_targets(self):
        if isinstance(self.statement, ast.Assign) and\
           isinstance(self.statement.targets, list):
            self.targets = self.statement.targets
        elif isinstance(self.statement, ast.AnnAssign) and\
                isinstance(self.statement.target, list):
            self.targets = self.statement.target
        elif isinstance(self.statement, ast.AnnAssign) and\
                isinstance(self.statement.target, ast.Attribute):
            self.targets = [self.statement.target]
        else:
            self.targets = []

    def __annotation(self):
        if isinstance(self.statement, ast.AnnAssign):
            self.annotation = Annotation(self.statement.annotation).name

    def __names(self):
        if self.variable_names is None:
            self.variable_names = []
        if self.call_names is None:
            self.call_names = []

        for target in self.targets:
            if isinstance(target, ast.Attribute):
                self.variable_names.append(target.attr)
            elif isinstance(target, ast.Name):
                self.variable_names.append(target.id)
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

    def __parse(self):
        self.__annotation()
        self.__names()

    def to_dict(self):
        return {"names": self.variable_names, "annotation": self.annotation}
