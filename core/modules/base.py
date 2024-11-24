import os
import ast
from typing import List

from pydeps.target import Target

from main import LOGGER


class AbstractModule:
    def __init__(self, file_path):
        self.file_path = file_path
        self.target = Target(file_path)
        self.workdir = self.target.workdir
        self.name = self.target.modpath
        self.name_list = self.target.modpath.split('.')
        self.dirname = os.path.dirname(self.target.relpath)
        self.is_empty = True
        self.all_imports = None
        self._ast_root = None
        self._identifiers = None

        if self.file_path.endswith('.py'):
            self._get_ast_root()
        elif 'cpython' in self.file_path and self.file_path.endswith('.so'):
            self.is_empty = False

    def _get_ast_root(self):
        try:
            with open(self.file_path, "r") as file:
                self._ast_root = ast.parse(file.read())
                if self._ast_root.body:
                    self.is_empty = False
        except FileNotFoundError:
            LOGGER.error(f"File not found: {self.file_path}.")

    def _get_relative_import_name(self, node: ast.ImportFrom) -> str:
        try:
            if len(self.name_list) >= node.level:
                import_name = self.name_list[:node.level*-1]
                if node.module is not None:
                    import_name.append(node.module)
                return '.'.join(import_name)
        except Exception as e:
            LOGGER.error(
                f"FILE PATH: {self.file_path}. NODE: {node.module}. MESSAGE: {e}."
            )
        return node.module

    def _import(self, node: ast.Import):
        for alias in node.names:
            if alias.name in self.all_imports:
                self.all_imports[alias.name].append(alias.name)
            else:
                self.all_imports[alias.name] = [alias.name]
            self._identifiers.add(alias.name)

    def _import_from(self, node: ast.ImportFrom):
        import_name = node.module
        if node.level:
            import_name = self._get_relative_import_name(node)
        if import_name in self.all_imports:
            self.all_imports[import_name].extend(
                alias.name for alias in node.names
            )
        else:
            self.all_imports[import_name] = [
                alias.name for alias in node.names
            ]
        self._identifiers.update(alias.name for alias in node.names)

    def _module(self, node: ast.Module):
        for definition in node.body:
            if isinstance(
                definition,
                (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                if hasattr(definition, 'name') and definition.name:
                    self._identifiers.add(definition.name)

    def _check_node(self, node):
        if isinstance(node, ast.Import):
            self._import(node)
        elif isinstance(node, ast.ImportFrom):
            self._import_from(node)
        elif isinstance(node, ast.Module):
            self._module(node)

    def walk_root(self):
        if self._ast_root:
            try:
                for node in ast.walk(self._ast_root):
                    self._check_node(node)
            except Exception as e:
                LOGGER.error(
                    f"FILE PATH: {self.file_path}. MESSAGE: {e}."
                )

    def parse(self):
        self.all_imports = {}
        self._identifiers = set()

        self.walk_root()

    @property
    def identifiers(self) -> List[str]:
        if self._identifiers is None:
            return []
        elif isinstance(self._identifiers, set):
            return list(self._identifiers)
        return self._identifiers
