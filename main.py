import logging

from core.configuration.config import Config
from core.project import Project
from core.converters.graph2imports import Graph2Imports
from core.converters.imports2exports import Imports2Exports
from core.converters.exports2diagrams import Exports2Diagrams
from core.modules.source_module import SourceModule
from core.adapter.pydeps_lib import pydeps


CONFIG = Config('/path_to/cranberrypy.ini')
LOGGER = logging.getLogger(__name__)


def main():
    project = Project(config=CONFIG)
    if project.file_paths:
        graph2imports = Graph2Imports(config=CONFIG)
        imports2exports = Imports2Exports(config=CONFIG)
        exports2diagrams = Exports2Diagrams(config=CONFIG)
        
        for file_path in project.file_paths:
            try:
                module = SourceModule(file_path)
                if module.has_imports:
                    graph = pydeps(file_path)
                    graph2imports.add(module, graph)
            except Exception as e:
                LOGGER.error(f"File path: {file_path}, error: {e}")
        graph2imports.save()

        imports2exports.add(graph2imports.data)
        imports2exports.save()

        exports2diagrams.add(imports2exports.data)
        exports2diagrams.save()


if __name__ == "__main__":
    main()
