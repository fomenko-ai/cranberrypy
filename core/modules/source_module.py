import ast
from typing import Set, List, Dict

from core.modules.base import AbstractModule
from core.modules.definitions.module_class import ModuleClass
from core.modules.statements.call import Call
from core.utils.func import read_file, is_used_by_class
from main import LOGGER


class SourceModule(AbstractModule):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.imports = None
        self.classes = None
        self.all_imports = None
        self._class_nodes = None

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

    def _module(self, node: ast.Module):
        for definition in node.body:
            if isinstance(definition, ast.ClassDef):
                module_class = ModuleClass(definition)
                self.classes[module_class.name] = module_class.to_dict()
                self._class_nodes[module_class.name] = definition

    def _check_node(self, node):
        if isinstance(node, ast.Import):
            self._import(node)
        elif isinstance(node, ast.ImportFrom):
            self._import_from(node)
        elif isinstance(node, ast.Module):
            self._module(node)

    def parse(self):
        self.imports = {}
        self.classes = {}
        self.all_imports = {}
        self._class_nodes = {}
        if self._ast_root:
            try:
                for node in ast.walk(self._ast_root):
                    self._check_node(node)
            except Exception as e:
                LOGGER.error(f"FILE PATH: {self.file_path}. MESSAGE: {e}.")

    def select_import(self, module_name):
        if module_name in self.all_imports:
            self.imports[module_name] = self.all_imports[module_name]

    def _filter_class_names(self, class_name):
        class_names = set()
        class_names.update(
            set(v for _, values in self.all_imports.items() for v in values)
        )
        class_names.update(
            set(key for key in self.classes.keys() if key != class_name)
        )
        return class_names

    def _recursion_class_usage_scan(self, node, class_names: Set[str]) -> Set[str]:
        """Scan class usage as call, argument and annotation"""
        used_classes = set()

        for child_node in ast.iter_child_nodes(node):
            if isinstance(child_node, ast.Call):
                call = Call(child_node)
                if call.name in class_names:
                    used_classes.add(call.name)
                if isinstance(child_node.args, list):
                    for arg in child_node.args:
                        if isinstance(arg, ast.Name) and hasattr(arg, 'id'):
                            if arg.id in class_names:
                                used_classes.add(arg.id)
            if isinstance(child_node, ast.arguments) and isinstance(child_node.args, list):
                for arg in child_node.args:
                    if isinstance(arg, ast.arg):
                        if isinstance(arg.annotation, ast.Name) and hasattr(arg.annotation, 'id'):
                            if arg.annotation.id in class_names:
                                used_classes.add(arg.annotation.id)

            used_classes.update(
                self._recursion_class_usage_scan(child_node, class_names)
            )

        return used_classes

    @staticmethod
    def _filter_usages(
        structure: Dict[str, List[str]],
        usages: Set[str]
    ) -> List[str]:
        result = []
        for class_name in usages:
            if not is_used_by_class(class_name, structure):
                result.append(class_name)
        return result

    def check_usages(self):
        if self._class_nodes:
            for name, node in self._class_nodes.items():
                class_names = self._filter_class_names(name)
                usages = self._recursion_class_usage_scan(
                    node, class_names
                )
                self.classes[name]['usages'] = self._filter_usages(
                    self.classes[name], usages
                )

    @property
    def code(self) -> str:
        return read_file(self.file_path)
