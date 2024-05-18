from pydeps.depgraph import DepGraph

from core.models import Module


def graph2json(graph: DepGraph):
    modules = []
    for module_name, source in graph.sources.items():
        if module_name.endswith('.py'):
            continue
        if not source.path.endswith('.py'):
            continue
        module = Module(module_name, source.path)
        if module.is_empty:
            continue
        if module.type in ['built_in', 'third_party']:
            continue
        for import_name in source.imports:
            if import_name.endswith('.py'):
                continue
            if import_name in graph.sources:
                if graph.sources[import_name].path.endswith('.py'):
                    import_type = Module.get_type(graph.sources[import_name].path)
                    if import_type:
                        module.imports[import_type].append(import_name)
                    else:
                        module.parse_class_imports(
                            graph.sources[import_name].name
                        )
        modules.append(module)

    return {
        "modules": {module.name: module.imports for module in modules}
    }
