from core.configuration.config import Config
from core.logger import Logger
from core.project import Project


CONFIG = Config('cranberrypy.ini')

LOGGER = Logger(config=CONFIG)
LOGGER.setup_logger()


def main():
    LOGGER.info('Cranberrypy start')
    from core.modules.source_module import SourceModule
    from core.converters.graph2imports import Graph2Imports
    from core.converters.imports2exports import Imports2Exports
    from core.converters.exports2diagrams import Exports2Diagrams

    project = Project(config=CONFIG)
    if project.file_paths:
        LOGGER.info('Initializing converters')
        graph2imports = Graph2Imports(config=CONFIG)
        imports2exports = Imports2Exports(config=CONFIG)
        exports2diagrams = Exports2Diagrams(config=CONFIG)

        LOGGER.info('Creating graph')
        from core.adapter.pydeps_lib import pydeps
        graph = pydeps(config=CONFIG, workdir=project.path)

        LOGGER.info('Graph -> Import')
        for file_path in project.file_paths:
            try:
                module = SourceModule(file_path)
                if module.has_imports:
                    graph2imports.add(module, graph)
            except Exception as e:
                LOGGER.error(f"FILE PATH: {file_path}. MESSAGE: {e}.")
        graph2imports.save()

        LOGGER.info('Import -> Export')
        imports2exports.add(graph2imports.data)
        imports2exports.save()

        LOGGER.info('Export -> Diagrams')
        exports2diagrams.add(imports2exports.data)
        exports2diagrams.save()
    else:
        LOGGER.error(f"File paths not found: {project.path}.")
    LOGGER.info('Cranberrypy finish')


if __name__ == "__main__":
    main()
