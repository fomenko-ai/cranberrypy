from unittest.mock import patch

from core.project import Project
from core.utils.func import deep_dict_compare, deep_list_compare
from tests.example_data import IMPORTS, EXPORTS, DIAGRAMS, ASSISTANT
from tests.example_data import get_config


def test_main():
    config = get_config()
    with patch('core.logger.Logger'):
        from core.modules.source_module import SourceModule
        from core.converters.graph2imports import Graph2Imports
        from core.converters.imports2exports import Imports2Exports
        from core.converters.exports2diagrams import Exports2Diagrams
        from core.converters.diagrams2assistant import Diagrams2Assistant

        project = Project(config=config)
        if project.file_paths:
            graph2imports = Graph2Imports(config=config)
            imports2exports = Imports2Exports(config=config)
            exports2diagrams = Exports2Diagrams(config=config)
            diagrams2assistant = Diagrams2Assistant(config=config)

            from core.adapter.pydeps_lib import pydeps
            graph = pydeps(config=config, workdir=config.project_path)

            for file_path in project.file_paths:
                try:
                    module = SourceModule(file_path)
                    if not module.is_empty:
                        graph2imports.add(module, graph)
                except Exception as e:
                    print(e)

            assert graph2imports.data['modules']
            assert deep_dict_compare(
                IMPORTS['modules'],
                graph2imports.data['modules'],
                ['file_path']
            )

            imports2exports.add(graph2imports.data)
            assert imports2exports.data['modules']
            assert deep_dict_compare(
                EXPORTS['modules'],
                imports2exports.data['modules']
            )

            exports2diagrams.add(imports2exports.data)
            assert exports2diagrams.data['nodes']
            assert deep_list_compare(
                DIAGRAMS['nodes'],
                exports2diagrams.data['nodes']
            )
            assert deep_list_compare(
                DIAGRAMS['links'],
                exports2diagrams.data['links'],
                ['fullInfo']
            )
            assert deep_list_compare(
                DIAGRAMS['group_keys'],
                exports2diagrams.data['group_keys']
            )
            assert deep_dict_compare(
                DIAGRAMS['group_dict'],
                exports2diagrams.data['group_dict']
            )

            diagrams2assistant.add(graph2imports.data, exports2diagrams.data)
            assert diagrams2assistant.data['dependencies']
            assert deep_list_compare(
                ASSISTANT['dependencies'],
                diagrams2assistant.data['dependencies'],
                ['source']
            )
