from pydeps.depgraph import DepGraph

from core.modules import SourceModule, ImportModule
from core.utils import write_json


class Graph2Json:
    def __init__(self, config):
        self.filename = config.filename
        self.json_data = {"modules": {}}

    def add(self, graph: DepGraph):
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
                self.json_data['modules'][graph.target.modpath] = {
                    "imports": module.imports
                }

    def save(self):
        write_json(self.json_data, self.filename)
