import os
import re
import json


def write_json(json_data, filename):
    with open(filename, 'w') as outfile:
        json.dump(json_data, outfile)


def __check_cache_folder(path):
    if '__pycache__' in path or '.pytest_cache' in path:
        return True
    else:
        return False


def recursive_file_scan(project_path: str, excluded_folders: str) -> list:
    file_paths = []
    stop_root = 'stop_root'
    for root, dirs, files in os.walk(project_path):
        if stop_root in root or __check_cache_folder(root):
            continue
        if root != project_path and root in excluded_folders:
            stop_root = root
            continue
        for file in files:
            if file.endswith('.py'):
                file_paths.append(os.path.join(root, file))
    return file_paths
