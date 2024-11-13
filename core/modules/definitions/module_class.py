import ast

from core.modules.definitions.base import Base
from core.modules.statements.assignment import Assignment
from core.modules.definitions.class_method import ClassMethod


class ModuleClass(Base):
    excluded_keys = 'definition', 'body', 'name', 'bases'

    def __init__(self, definition: ast.ClassDef):
        super().__init__(definition)
        self.bases = definition.bases
        self.attributes = None
        self.methods = None
        self.inheritance = None
        self.compositions = None
        self.calls = None
        self.usages = None

        self._parse()

    def _parse(self):
        self.attributes = []
        self.methods = []
        self.inheritance = []
        self.compositions = set()
        self.calls = set()
        self.usages = []

        if self.bases:
            for base in self.bases:
                if isinstance(base, ast.Name) and \
                   isinstance(base.ctx, ast.Load):
                    self.inheritance.append(base.id)
                elif (
                    isinstance(base, ast.Attribute)
                    and hasattr(base, "value")
                    and hasattr(base.value, "id")
                ):
                    self.inheritance.append(base.value.id)
        if self.body:
            for _def in self.body:
                if isinstance(_def, (ast.Assign, ast.AnnAssign)):
                    assignment = Assignment(_def)
                    self.attributes.append(assignment.to_dict())
                elif isinstance(_def, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method = ClassMethod(_def)
                    if _def.name == '__init__':
                        if method.assignments:
                            self.attributes.extend(method.assignments)
                        if method.compositions:
                            for compos in method.compositions:
                                self.compositions.add(compos)
                    if method.name:
                        self.methods.append(method.to_dict())
                    if method.calls:
                        for call in method.calls:
                            if call != 'super':
                                self.calls.add(call)
        self.compositions = list(self.compositions)
        self.calls = list(self.calls)

    def to_dict(self):
        return {
            k: v for k, v in self.__dict__.items()
            if not (k in self.excluded_keys or k.startswith('_'))
        }
