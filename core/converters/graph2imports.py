from pydeps.depgraph import DepGraph

from core.converters.base import AbstractConverter
from core.modules.source_module import SourceModule
from core.modules.import_module import ImportModule
from core.utils import write_json


class Graph2Imports(AbstractConverter):

    def add(self, module: SourceModule, graph: DepGraph):
        if not self.data:
            self.data = {"modules": {}, "dirnames": {}}
        if graph and graph.sources:
            module.parse()
            for import_name, source in graph.sources.items():
                if import_name.endswith('.py'):
                    continue
                if source.path and source.path.endswith('.py'):
                    _import = ImportModule(source.path)
                    if _import.has_imports:
                        if _import.type:
                            self.data["dirnames"][import_name] = _import.type
                        else:
                            self.data["dirnames"][import_name] = _import.dirname
                        module.select_import(source.name)
            if module.imports:
                self.data['modules'][graph.target.modpath] = {
                    "imports": module.imports, "classes": module.classes
                }
                self.data["dirnames"][graph.target.modpath] = module.dirname

    def save(self):
        write_json(self.data, f"{self.filename}_IMPORTS.json")
