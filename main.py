from core.configuration.config import Config
from core.project import Project
from core.converters.graph2imports import Graph2Imports
from core.converters.imports2exports import Imports2Exports
from core.adapter.pydeps_lib import pydeps


CONFIG = Config('/path_to/cranberrypy.ini')


def main():
    project = Project(config=CONFIG)
    if project.file_paths:
        graph2imports = Graph2Imports(config=CONFIG)
        imports2exports = Imports2Exports(config=CONFIG)

        for file_path in project.file_paths:
            graph = pydeps(file_path)
            graph2imports.add(graph)
        graph2imports.save()

        imports2exports.add(graph2imports.data)
        imports2exports.save()


if __name__ == "__main__":
    main()
