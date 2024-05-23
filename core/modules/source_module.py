import ast
import logging

from core.modules.base import AbstractModule


class SourceModule(AbstractModule):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.imports = {
            "built_in": [],
            "third_party": []
        }

    def parse_class_imports(self, import_name):
        classes = []
        if self._ast_root:
            try:
                for node in ast.walk(self._ast_root):
                    if isinstance(node, ast.ImportFrom):
                        if node.module == import_name:
                            classes.extend(alias.name for alias in node.names)
            except Exception as e:
                logging.error(e)
        if classes:
            self.imports[import_name] = classes
