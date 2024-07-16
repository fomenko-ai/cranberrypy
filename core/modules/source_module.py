import ast

from core.modules.base import AbstractModule
from core.modules.definitions.module_class import ModuleClass
from main import LOGGER


class SourceModule(AbstractModule):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.imports = None
        self.classes = None
        self._all_imports = None

    def __get_relative_import_name(self, node: ast.ImportFrom) -> str:
        try:
            if len(self.name_list) >= node.level:
                import_name = self.name_list[:node.level*-1]
                import_name.append(node.module)
                return '.'.join(import_name)
        except Exception as e:
            LOGGER.error(
                f"FILE PATH: {self.file_path}. NODE: {node.module}. MESSAGE: {e}."
            )
        return node.module

    def __import(self, node: ast.Import):
        for alias in node.names:
            if alias.name in self._all_imports:
                self._all_imports[alias.name].append(alias.name)
            else:
                self._all_imports[alias.name] = [alias.name]

    def __import_from(self, node: ast.ImportFrom):
        if node.level:
            import_name = self.__get_relative_import_name(node)
        else:
            import_name = node.module
        if node.module in self._all_imports:
            self._all_imports[import_name].extend(
                alias.name for alias in node.names
            )
        else:
            self._all_imports[import_name] = [
                alias.name for alias in node.names
            ]

    def __module(self, node: ast.Module):
        for definition in node.body:
            if isinstance(definition, ast.ClassDef):
                module_class = ModuleClass(definition)
                self.classes[module_class.name] = module_class.to_dict()

    def __check_node(self, node):
        if isinstance(node, ast.Import):
            self.__import(node)
        elif isinstance(node, ast.ImportFrom):
            self.__import_from(node)
        elif isinstance(node, ast.Module):
            self.__module(node)

    def parse(self):
        self.imports = {}
        self.classes = {}
        self._all_imports = {}
        if self._ast_root:
            try:
                for node in ast.walk(self._ast_root):
                    self.__check_node(node)
            except Exception as e:
                LOGGER.error(f"FILE PATH: {self.file_path}. MESSAGE: {e}.")

    def select_import(self, module_name):
        if module_name in self._all_imports:
            self.imports[module_name] = self._all_imports[module_name]
