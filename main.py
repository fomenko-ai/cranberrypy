from core.configuration.config import CONFIG
from core.utils import recursive_file_scan, write_json
from core.adapter.pydeps_lib import Project, pydeps
from core.graph2json import graph2json


def main():
    json_data = {"modules": {}}
    project = Project(path=CONFIG.project_path)
    excluded_folders = CONFIG.excluded_folders
    file_paths = recursive_file_scan(
        project_path=project.path,
        excluded_folders=excluded_folders
    )
    for file_path in file_paths:
        module_name, graph = pydeps(file_path)
        data = graph2json(graph, file_path)
        if data:
            json_data['modules'][module_name] = {"imports": data}
    write_json(json_data, project.filename)


if __name__ == "__main__":
    main()
