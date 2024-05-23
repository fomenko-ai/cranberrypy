from pydeps.depgraph import DepGraph

from core.converters.base import AbstractConverter
from core.modules.source_module import SourceModule
from core.modules.import_module import ImportModule
from core.utils import write_json


class Graph2Imports(AbstractConverter):

    def add(self, graph: DepGraph):
        if not self.data:
            self.data = {"modules": {}}
        module = SourceModule(graph.target.path)
        if graph and graph.sources:
            for import_name, source in graph.sources.items():
                if import_name.endswith('.py'):
                    continue
                if source.path and source.path.endswith('.py'):
                    _import = ImportModule(source.path)
                    if _import.is_empty:
                        continue
                    if _import.type:
                        module.imports[_import.type].append(import_name)
                    else:
                        module.parse_class_imports(source.name)
            if module.imports:
                self.data['modules'][graph.target.modpath] = {
                    "imports": module.imports
                }

    def save(self):
        write_json(self.data, f"{self.filename}_IMPORTS.json")
