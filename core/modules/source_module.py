import ast
import logging

from core.modules.base import AbstractModule


class SourceModule(AbstractModule):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.imports = None

    def parse_imports(self, module_name):
        imports = []
        if self._ast_root:
            try:
                for node in ast.walk(self._ast_root):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name == module_name:
                                imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module == module_name:
                            imports.extend(alias.name for alias in node.names)
            except Exception as e:
                logging.error(e)
        if imports:
            if self.imports is None:
                self.imports = {}
            self.imports[module_name] = imports
