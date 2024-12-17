import copy
import json
import logging

import jsonschema

DATA_FILE = "players.json"

schema = {
    "type": "object",
    "patternProperties": {
        r"^[0-9]*$": {"type": "object",
                "properties": {
                    "team": {"type": "integer"},
                    # "position": {"type": "array", "items": "integer"},
                    "frozen": {"type": "boolean"}},
                "required": ["team"]},
    },
    "additionalProperties": False
}

default = {}
    
    
def save():
    global data
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


def load():
    global data
    try:
        with open(DATA_FILE) as file:
            data = json.load(file)
            jsonschema.validate(data, schema)
    except FileNotFoundError:
        logging.warning("No player data found, creating new...")
        data = copy.deepcopy(default)
        save()

load()
 
        
def player_config(uid: str, team: int):
    global data
    data[uid] = {
        "team": team
    }

def enumerate_affilations() -> dict[int, int]:
    affiliations = {}
    
    global data
    for i in data.values():
        if not i["team"] in affiliations:
            affiliations[i["team"]] = 1
        else:
            affiliations[i["team"]] += 1
            
    return affiliations