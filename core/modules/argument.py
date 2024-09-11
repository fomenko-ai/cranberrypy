import ast

from core.modules.annotation import Annotation


class Argument:
    def __init__(self, arg: ast.arg):
        self.arg = arg
        self.name = None
        self.annotation = None

        self._parse()

    def _parse(self):
        if self.arg.arg is not None and\
           isinstance(self.arg.arg, str):
            self.name = self.arg.arg
        if self.arg.annotation is not None and\
           isinstance(self.arg.annotation, (ast.Name, ast.Subscript)):
            self.annotation = Annotation(self.arg.annotation).name

    def to_dict(self):
        return {"name": self.name, "annotation": self.annotation}
