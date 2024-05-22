from core.configuration.config import CONFIG
from core.project import Project
from core.graph2json import Graph2Json
from core.adapter.pydeps_lib import pydeps


def main():
    project = Project(config=CONFIG)
    if project.file_paths:
        graph2json = Graph2Json(config=CONFIG)
        for file_path in project.file_paths:
            graph = pydeps(file_path)
            graph2json.add(graph)
        graph2json.save()


if __name__ == "__main__":
    main()
