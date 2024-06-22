from typing import Dict

from core.converters.base import AbstractConverter
from core.utils import write_json


class Imports2Exports(AbstractConverter):

    @staticmethod
    def __get_export_type(
        export_value: str,
        classes: Dict[str, dict]
    ) -> str:
        for cls, cls_structure in classes.items():
            if export_value in cls_structure['inheritance']:
                return 'is_inheritance'
            if export_value in cls_structure['calls']:
                return 'is_call'
        return 'is_undefined'

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
                        exports[value].append(
                            (module_name, self.__get_export_type(value, classes))
                        )
                self.data['classes'][module_name] = classes
            self.data['dirnames'] = modules['dirnames']

    def save(self):
        write_json(self.data, f"{self.filename}_EXPORTS.json")
