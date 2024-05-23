import ast
import logging

from core.modules.base import AbstractModule


class ImportModule(AbstractModule):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.type = None
        self.is_empty = True

        self.__get_type(file_path)
        self.__check_imports()

    def __get_type(self, file_path):
        if 'usr' in file_path and 'lib' in file_path and 'python' in file_path:
            self.type = 'built_in'
        elif 'site-packages' in file_path:
            self.type = 'third_party'
        else:
            self.type = None

    def __check_imports(self):
        imported_classes = 0
        if self._ast_root:
            try:
                for node in ast.walk(self._ast_root):
                    if isinstance(node, ast.ImportFrom):
                        imported_classes += 1
            except Exception as e:
                logging.error(e)
        if imported_classes:
            self.is_empty = False
