import ast
import logging


class AbstractModule:
    def __init__(self, file_path):
        self.file_path = file_path
        self._ast_root = None

        self.__get_ast_root()

    def __get_ast_root(self):
        if self.file_path.endswith('.py'):
            try:
                with open(self.file_path, "r") as file:
                    self._ast_root = ast.parse(file.read())
            except FileNotFoundError:
                logging.error(f"File not found: {self.file_path}")
