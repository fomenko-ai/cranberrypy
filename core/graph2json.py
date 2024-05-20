from pydeps.depgraph import DepGraph

from core.models import ImportModule


def graph2json(graph: DepGraph):
    imports = []
    for module_name, source in graph.sources.items():
        if module_name.endswith('.py'):
            continue
        if not source.path.endswith('.py'):
            continue
        module = ImportModule(module_name, source.path)
        if module.is_empty:
            continue
        if module.type in ['built_in', 'third_party']:
            continue
        for import_name in source.imports:
            if import_name.endswith('.py'):
                continue
            if import_name in graph.sources:
                if graph.sources[import_name].path.endswith('.py'):
                    import_type = ImportModule.get_type(graph.sources[import_name].path)
                    if import_type:
                        module.imports[import_type].append(import_name)
                    else:
                        module.parse_class_imports(
                            graph.sources[import_name].name
                        )
        imports.append(module)

    return {
        "imports": {module.name: module.imports for module in imports}
    }
