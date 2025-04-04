import ast
from typing import Union

from core.modules.annotation import Annotation
from core.modules.argument import Argument
from core.modules.definitions.base import Base
from core.modules.statements.assignment import Assignment
from core.modules.statements.expression import Expression


STOP_LIST = [None, 'self', 'cls', 'args', 'kwargs']


class ClassMethod(Base):

    def __init__(
        self,
        definition: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ):
        super().__init__(definition)
        self.arguments = None
        self.returns = None
        self.assignments = None
        self.compositions = None
        self.calls = None

        self._parse()

    def _arguments(self):
        if self.arguments is None:
            self.arguments = []

        if isinstance(self.definition.args, ast.arguments):
            if isinstance(self.definition.args.args, list):
                for arg in self.definition.args.args:
                    argument = Argument(arg)
                    if argument.name not in STOP_LIST:
                        self.arguments.append(argument.to_dict())

    def _returns(self):
        if self.definition.returns is not None:
            self.returns = Annotation(self.definition.returns).name

    def _add_composition(self, call_names: list):
        for name in call_names:
            if isinstance(name, str) and name[0].isupper():
                self.compositions.add(name)
            else:
                if name not in STOP_LIST:
                    self.calls.add(name)

    def _add_calls(self, call_names: list):
        for name in call_names:
            if name not in STOP_LIST:
                self.calls.add(name)

    def _body(self):
        if self.assignments is None:
            self.assignments = []
        if self.compositions is None:
            self.compositions = set()
        if self.calls is None:
            self.calls = set()

        for statement in self.body:
            if isinstance(statement, (ast.Assign, ast.AnnAssign)):
                assignment = Assignment(statement)
                self.assignments.append(assignment.to_dict())
                if self.name == '__init__' and assignment.has_class_call:
                    self._add_composition(assignment.call_names)
                elif assignment.has_call:
                    self._add_calls(assignment.call_names)
            elif isinstance(statement, ast.Expr):
                expression = Expression(statement)
                self._add_calls(expression.call_names)

    def _parse(self):
        self._arguments()
        self._returns()
        self._body()

    def to_dict(self):
        return {
            "name": self.name,
            "arguments": self.arguments,
            "returns": self.returns,
        }
