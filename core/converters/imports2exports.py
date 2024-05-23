from core.converters.base import AbstractConverter
from core.utils import write_json


class Imports2Exports(AbstractConverter):
    def add(self, modules: dict):
        if not self.data:
            self.data = {}
        if 'modules' in modules:
            for module_name, _imports in modules['modules'].items():
                imports = _imports['imports']
                for import_name, values in imports.items():
                    if import_name not in self.data:
                        self.data[import_name] = {'exports': {}}
                    exports = self.data[import_name]['exports']
                    for value in values:
                        if value not in exports:
                            exports[value] = []
                        exports[value].append(module_name)

    def save(self):
        write_json(self.data, f"{self.filename}_EXPORTS.json")
