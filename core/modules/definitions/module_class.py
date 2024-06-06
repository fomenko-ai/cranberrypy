import ast

from core.modules.definitions.base import Base
from core.modules.definitions.class_method import ClassMethod


class ModuleClass(Base):
    excluded_keys = 'body', 'name', 'bases'

    def __init__(self, definition: ast.ClassDef):
        super().__init__(definition)
        self.bases = definition.bases
        self.attributes = None
        self.methods = None
        self.dependencies = None
        self.compositions = None

        self.__parse()

    def __parse(self):
        self.methods = []
        self.dependencies = []
        self.compositions = set()

        if self.bases:
            for base in self.bases:
                if isinstance(base, ast.Name) and \
                   isinstance(base.ctx, ast.Load):
                    self.dependencies.append(base.id)
        if self.body:
            for _def in self.body:
                if isinstance(_def, ast.FunctionDef):
                    method = ClassMethod(_def)
                    if _def.name == '__init__':
                        self.attributes = method.assignments
                    else:
                        self.methods.append(method.name)
                    if method.calls:
                        for call in method.calls:
                            if call != 'super':
                                self.compositions.add(call)
        self.compositions = list(self.compositions)

    def to_dict(self):
        return {
            k: v for k, v in self.__dict__.items()
            if not (k in self.excluded_keys or k.startswith('_'))
        }
