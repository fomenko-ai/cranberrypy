import os
import ast

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
        self.has_imports = False
        self._ast_root = None
        self.is_empty = True

        self._get_ast_root()
        self._check_imports()

    def _get_ast_root(self):
        if self.file_path.endswith('.py'):
            try:
                with open(self.file_path, "r") as file:
                    self._ast_root = ast.parse(file.read())
                    if self._ast_root.body:
                        self.is_empty = False
            except FileNotFoundError:
                LOGGER.error(f"File not found: {self.file_path}.")

    def _check_imports(self):
        if self._ast_root:
            try:
                for node in ast.walk(self._ast_root):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        self.has_imports = True
                        break
            except Exception as e:
                LOGGER.error(e)
