import json


def write_json(data, path):
    with open(path, "w") as f:
        f.write(json.dumps(data, indent=4))


def read_json(path):
    with open(path, "r") as f:
        data = json.loads(f.read())
    return data
