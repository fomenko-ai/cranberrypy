import json


def write_file(data, file_path):
    with open(file_path, 'w') as file:
        file.write(data)


def read_file(file_path) -> str:
    with open(file_path, 'r') as file:
        return file.read()


def write_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file)


def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
