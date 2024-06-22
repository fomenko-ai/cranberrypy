import os
import ast
import logging

from pydeps.target import Target


class AbstractModule:
    def __init__(self, file_path):
        self.file_path = file_path
        self.target = Target(file_path)
        self.dirname = os.path.dirname(self.target.relpath)
        self.has_imports = False
        self._ast_root = None

        self.__get_ast_root()
        self.__check_imports()

    def __get_ast_root(self):
        if self.file_path.endswith('.py'):
            try:
                with open(self.file_path, "r") as file:
                    self._ast_root = ast.parse(file.read())
            except FileNotFoundError:
                logging.error(f"File not found: {self.file_path}")

    def __check_imports(self):
        if self._ast_root:
            try:
                for node in ast.walk(self._ast_root):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        self.has_imports = True
                        break
            except Exception as e:
                logging.error(e)
