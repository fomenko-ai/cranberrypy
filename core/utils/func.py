import os
import json
from typing import Dict, List


def _check_dirs(file_path):
    if "/temp/" in file_path:
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
    else:
        raise Exception("Write path is not inside 'temp' dir.")


def write_file(data, file_path):
    _check_dirs(file_path)
    with open(file_path, 'w') as file:
        file.write(data)


def read_file(file_path) -> str:
    with open(file_path, 'r') as file:
        return file.read()


def write_json(data, file_path):
    _check_dirs(file_path)
    with open(file_path, 'w') as file:
        json.dump(data, file)


def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def is_used_by_class(
    identifier_name: str,
    class_structure: Dict[str, List]
) -> bool:
    if identifier_name in class_structure['inheritance']:
        return True
    if identifier_name in class_structure['compositions']:
        return True
    if identifier_name in class_structure['calls']:
        return True
    if identifier_name in class_structure['usages']:
        return True
    return False


def get_dependency_type(
    identifier_name: str,
    class_structure: Dict[str, List]
) -> str:
    if identifier_name in class_structure['inheritance']:
        return 'inheritance'
    if identifier_name in class_structure['compositions']:
        return 'composition'
    if identifier_name in class_structure['calls']:
        return 'call'
    if identifier_name in class_structure['usages']:
        return 'usage'
    return 'undefined'


def deep_dict_compare(d1, d2, excluded_keys=None) -> bool:
    if excluded_keys is None:
        excluded_keys = []
    for k in d1:
        if k in excluded_keys:
            continue
        if k not in d2:
            return False
        else:
            if isinstance(d1[k], dict) and isinstance(d2[k], dict):
                if deep_dict_compare(d1[k], d2[k], excluded_keys):
                    continue
                else:
                    return False
            if d1[k] == d2[k]:
                continue
            else:
                if isinstance(d1[k], list) and isinstance(d2[k], list):
                    if deep_list_compare(d1[k], d2[k], excluded_keys):
                        continue
                    else:
                        return False
    return True


def deep_list_compare(l1, l2, excluded_keys=None) -> bool:
    if len(l1) == len(l2):
        for i in range(len(l1)):
            if len(l1[i]) == len(l2[i]):
                if isinstance(l1[i], dict) and isinstance(l2[i], dict):
                    if deep_dict_compare(l1[i], l2[i], excluded_keys):
                        continue
                    else:
                        return False
                elif isinstance(l1[i], list) and isinstance(l2[i], list):
                    if deep_list_compare(l1[i], l2[i], excluded_keys):
                        continue
                    else:
                        return False
            if (
                l1[i] in l2
                or list(l1[i]) in l2
                or tuple(l1[i]) in l2
            ) and (
                l2[i] in l1
                or list(l2[i]) in l1
                or tuple(l2[i]) in l1
            ):
                continue
            else:
                return False
    else:
        return False
    return True
