import ast


class Annotation:
    def __init__(self, annotation: (ast.Name or ast.Subscript)):
        self.annotation = annotation
        self.name = None

        self._parse()

    def _parse(self):
        if self.annotation is not None:
            if isinstance(self.annotation, ast.Name) and\
               isinstance(self.annotation.id, str):
                self.name = self.annotation.id
            elif isinstance(self.annotation, ast.Subscript):
                if isinstance(self.annotation.value, ast.Name) and\
                   isinstance(self.annotation.value.id, str):
                    self.name = self.annotation.value.id
