from typing import Dict, List

from core.converters.base import AbstractConverter
from core.utils.func import get_dependency_type, write_json


class Imports2Exports(AbstractConverter):

    @staticmethod
    def _get_exports(
        export_value: str,
        module_name: str,
        classes: Dict[str, dict]
    ) -> List:
        exports = []
        if classes:
            for cls, structure in classes.items():
                exports.append(
                    (
                        module_name,
                        cls,
                        get_dependency_type(export_value, structure)
                    )
                )
        else:
            exports.append(
                (
                    module_name,
                    None,
                    'undefined'
                )
            )
        return exports

    def add(self, modules: dict):
        if not self.data:
            self.data = {"modules": {}, "dirnames": {}, "classes": {}}
        if 'modules' in modules:
            for module_name, module_structure in modules['modules'].items():
                imports = module_structure['imports']
                classes = module_structure['classes']
                for import_name, values in imports.items():
                    if import_name not in self.data['modules']:
                        self.data['modules'][import_name] = {
                            'exports': {}
                        }
                    exports = self.data['modules'][import_name]['exports']
                    for value in values:
                        if value not in exports:
                            exports[value] = []
                        exports[value].extend(
                            self._get_exports(value, module_name, classes)
                        )
                self.data['classes'][module_name] = classes
            self.data['dirnames'] = modules['dirnames']

    def save(self):
        write_json(
            self.data,
            f"./temp/saved/{self.save_dir}/exports.json"
        )
