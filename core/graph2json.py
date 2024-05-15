from pydeps.depgraph import DepGraph

from core.utils import write_json


def _get_module_type(path):
    if 'usr' in path and 'lib' in path and 'python' in path:
        return 'built_in'
    elif 'site-packages' in path:
        return 'third_party'
    else:
        return None


def graph2json(graph: DepGraph, filename: str = 'graph.json'):
    json_data = {
        "modules": {}
    }
    for module_name, source in graph.sources.items():
        json_data["modules"][module_name] = {
            "imports": {
                "built_in": [],
                "third_party": []
            }
        }
        for _import in source.imports:
            if _import in graph.sources:
                module_type = _get_module_type(graph.sources[_import].path)
                if module_type:
                    json_data["modules"][
                        module_name
                    ]["imports"][module_type].append(_import)
                else:
                    json_data["modules"][module_name]["imports"][_import] = []

    write_json(json_data, filename)
