from pydeps.depgraph import DepGraph

from core.converters.base import AbstractConverter
from core.modules.source_module import SourceModule
from core.modules.import_module import ImportModule
from core.utils.func import write_json


class Graph2Imports(AbstractConverter):

    def add(self, module: SourceModule, graph: DepGraph):
        if not self.data:
            self.data = {"modules": {}, "dirnames": {}}
        if graph and graph.sources and graph.sources.get(module.name):
            module.parse()
            imports = graph.sources[module.name].imports
            if imports:
                for import_name in imports:
                    source = graph.sources[import_name]
                    if import_name.endswith('.py'):
                        continue
                    if source.path and source.path.endswith('.py'):
                        _import = ImportModule(source.path)
                        if not _import.is_empty:
                            if _import.type:
                                self.data["dirnames"][
                                    import_name
                                ] = _import.type
                            else:
                                self.data["dirnames"][
                                    import_name
                                ] = _import.dirname
                            module.select_import(source.name)
            if module.imports:
                self.data['modules'][module.name] = {
                    "imports": module.imports,
                    "classes": module.classes,
                    "file_path": module.file_path
                }
                self.data["dirnames"][module.name] = module.dirname

    def save(self):
        write_json(
            self.data,
            f"./temp/saved/{self.save_dir}/imports.json"
        )
