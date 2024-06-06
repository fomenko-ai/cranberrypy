import ast
import logging

from core.modules.base import AbstractModule
from core.modules.definitions.module_class import ModuleClass


class SourceModule(AbstractModule):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.imports = None
        self.classes = None
        self._all_imports = None

    def __check_node(self, node):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in self._all_imports:
                    self._all_imports[alias.name].append(alias.name)
                else:
                    self._all_imports[alias.name] = [alias.name]
        elif isinstance(node, ast.ImportFrom):
            if node.module in self._all_imports:
                self._all_imports[node.module].extend(
                    alias.name for alias in node.names
                )
            else:
                self._all_imports[node.module] = [
                    alias.name for alias in node.names
                ]
        elif isinstance(node, ast.Module):
            for definition in node.body:
                if isinstance(definition, ast.ClassDef):
                    module_class = ModuleClass(definition)
                    self.classes[module_class.name] = module_class.to_dict()

    def parse(self):
        self.imports = {}
        self.classes = {}
        self._all_imports = {}
        if self._ast_root:
            try:
                for node in ast.walk(self._ast_root):
                    self.__check_node(node)
            except Exception as e:
                logging.error(e)

    def select_import(self, module_name):
        if module_name in self._all_imports:
            self.imports[module_name] = self._all_imports[module_name]
