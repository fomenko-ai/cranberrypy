from core.configuration.main import MainConfig
from core.logger import Logger
from core.project import Project


CONFIG = MainConfig('cranberrypy.ini')
LOGGER = Logger(config=CONFIG)
LOGGER.setup_logger()


def main():
    LOGGER.info('Cranberrypy start')
    from core.modules.source_module import SourceModule
    from core.converters.graph2imports import Graph2Imports
    from core.converters.imports2exports import Imports2Exports
    from core.converters.exports2diagrams import Exports2Diagrams
    from core.converters.diagrams2assistant import Diagrams2Assistant

    project = Project(config=CONFIG)
    if project.file_paths:
        LOGGER.info('Initializing converters')
        graph2imports = Graph2Imports(config=CONFIG)
        imports2exports = Imports2Exports(config=CONFIG)
        exports2diagrams = Exports2Diagrams(config=CONFIG)
        diagrams2assistant = Diagrams2Assistant(config=CONFIG)

        LOGGER.info('Creating graph')
        from core.adapter.pydeps_lib import pydeps
        graph = pydeps(config=CONFIG, workdir=project.path)

        LOGGER.info('... -> Imports')
        for file_path in project.file_paths:
            try:
                module = SourceModule(file_path)
                if not module.is_empty:
                    graph2imports.add(module, graph)
            except Exception as e:
                LOGGER.error(f"FILE PATH: {file_path}. MESSAGE: {e}.")
        graph2imports.save()

        LOGGER.info('... -> Exports')
        imports2exports.add(graph2imports.data)
        imports2exports.save()

        LOGGER.info('... -> Diagrams')
        exports2diagrams.add(imports2exports.data)
        exports2diagrams.save()

        LOGGER.info('... -> Assistant')
        diagrams2assistant.add(graph2imports.data, exports2diagrams.data)
        diagrams2assistant.save()
    else:
        LOGGER.error(f"File paths not found: {project.path}.")
    LOGGER.info('Cranberrypy finish')


if __name__ == "__main__":
    main()
