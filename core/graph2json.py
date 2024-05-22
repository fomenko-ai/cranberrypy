from pydeps.depgraph import DepGraph

from core.models import SourceModule, ImportModule


def graph2json(graph: DepGraph, file_path: str):
    module = SourceModule(file_path)
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
        return module.imports
    else:
        return None
