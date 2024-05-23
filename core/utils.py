import json


def write_json(json_data, filename='data.json'):
    with open(filename, 'w') as outfile:
        json.dump(json_data, outfile)


def read_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data
