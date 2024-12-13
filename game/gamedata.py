import json
import logging
import copy

import jsonschema

DATA_FILE = "game.json"

schema = {
    "type": "object",
    "properties": {
        "teams": {"type": "array",
                  "items": {"type": "object",
                            "properties": {
                                "name": {"type": "string"}, # display name
                                "colour": {"type": "integer"}, # hex code (but in decimal)
                            },
                  },
        },
        "start": {"type": ["string", "null"]}, # ISO date format
        "end": {"type": ["string", "null"]}, # ditto
        "voting_open": {"type": "boolean"},
        "offset": {"type": "integer"},
        "round_period": {"type": "integer"},
    },
    "required": ["teams", "voting_open", "offset", "round_period"]
}

default = {"teams": [], "voting_open": False, "offset": 0, "round_period": 20}
    
    
def save():
    global data
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)
        
def load():
    global data
    try:
        with open(DATA_FILE) as file:
            data = json.load(file)
            jsonschema.validate(data, schema)
    except FileNotFoundError:
        logging.warning("No game data found, creating new...")
        data = copy.deepcopy(default)
        save()

load()
        
def new_team(name: str, colour: int) -> int:
    """Create a new team (returns team ID)"""
    global data
    data["teams"].append({
        "name": name,
        "colour": colour
    })
    return len(data["teams"])-1