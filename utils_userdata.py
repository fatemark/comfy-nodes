import json
import os

def read_userdata_json(filename, default=None):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return default

def save_userdata_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def delete_userdata_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
