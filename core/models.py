import ast
import logging


class Module:
    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path
        self.imports = {
            "built_in": [],
            "third_party": []
        }
        self.type = None
        self.is_empty = True
        self._ast_root = None

        self.type = self.get_type(file_path)
        self.__get_ast_root()
        self.__check_imports()

    @staticmethod
    def get_type(file_path):
        if 'usr' in file_path and 'lib' in file_path and 'python' in file_path:
            return 'built_in'
        elif 'site-packages' in file_path:
            return 'third_party'
        else:
            return None

    def __get_ast_root(self):
        try:
            with open(self.file_path, "r") as file:
                self._ast_root = ast.parse(file.read())
        except FileNotFoundError:
            logging.error(f"File not found: {self.file_path}")

    def __check_imports(self):
        imported_classes = 0
        try:
            for node in ast.walk(self._ast_root):
                if isinstance(node, ast.ImportFrom):
                    imported_classes += 1
        except Exception as e:
            logging.error(e)
        if imported_classes:
            self.is_empty = False

    def parse_class_imports(self, import_name):
        classes = []
        try:
            for node in ast.walk(self._ast_root):
                if isinstance(node, ast.ImportFrom):
                    if node.module == import_name:
                        classes.extend(alias.name for alias in node.names)
        except Exception as e:
            logging.error(e)
        if classes:
            self.imports[import_name] = classes
