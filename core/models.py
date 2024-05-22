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
