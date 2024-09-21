import os
import json


def make_dirs(file_path):
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def write_file(data, file_path):
    make_dirs(file_path)
    with open(file_path, 'w') as file:
        file.write(data)


def read_file(file_path) -> str:
    with open(file_path, 'r') as file:
        return file.read()


def write_json(data, file_path):
    make_dirs(file_path)
    with open(file_path, 'w') as file:
        json.dump(data, file)


def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
