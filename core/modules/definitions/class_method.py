import ast

from core.modules.definitions.base import Base
from core.modules.statements.assignment import Assignment
from core.modules.statements.expression import Expression


class ClassMethod(Base):

    def __init__(self, definition: ast.FunctionDef):
        super().__init__(definition)
        self.assignments = None
        self.calls = None

        self.__parse()

    def __parse(self):
        if self.assignments is None:
            self.assignments = []
        if self.calls is None:
            self.calls = []

        for statement in self.body:
            if isinstance(statement, ast.Assign):
                assignment = Assignment(statement)
                self.assignments.extend(assignment.variable_names)
                if assignment.has_call:
                    self.calls.extend(assignment.call_names)
            elif isinstance(statement, ast.Expr):
                expression = Expression(statement)
                self.calls.extend(expression.call_names)
