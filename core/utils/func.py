import json


def write_json(json_data, filename='data.json'):
    with open("./temp/" + filename, 'w') as outfile:
        json.dump(json_data, outfile)


def read_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def read_file(filename) -> str:
    with open(filename, 'r') as file:
        return file.read()
