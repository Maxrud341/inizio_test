import json
from typing import Set, Tuple
import threading

file_lock = threading.Lock()
JSON_FILE = "data.json"


def json_reset():
    """Clear the JSON file."""
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)



def json_add(data: set):
    """Add a set of tuples to JSON file safely in multithreading."""
    data_dict = {k: v for k, v in data}

    with file_lock:
        with open(JSON_FILE, "a", encoding="utf-8") as f:  
            f.write(json.dumps(data_dict, ensure_ascii=False) + "\n")