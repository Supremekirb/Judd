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
                    "position": {"type": "array", "items": {"type": "integer"}},
                    "frozen": {"type": "integer"},
                    "moves": {"type": "integer"}, # moves USED, not remaining
                    "throws": {"type": "integer"}, # same
                    "queued_actions": {"type": "array", # actions to apply at the end of the round. Note that movement is applied instantly - it does not affect the map
                                       "items": {"type": "object",
                                                 "properties": {
                                                     "name": {"type": "string"},
                                                     "target": {"type": "array", "items": {"type": "integer"}}}}},
                    "total_hits": {"type": "integer"},
                    "total_turfed": {"type": "integer"},
                    "total_throws": {"type": "integer"},
                    },
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
 
        
def new_player(uid: str, team: int):
    global data 
    data[uid] = { # inits everything but position, since that is assigned at game start
        "team": team,
        "frozen": 0,
        "moves": 0,
        "throws": 0,
        "queued_actions": [],
        "total_hits": 0,
        "total_turfed": 0,
        "total_throws": 0,
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