import json


def write_json(json_data, filename):
    with open(filename, 'w') as outfile:
        json.dump(json_data, outfile)
        