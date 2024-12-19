import copy
import datetime
import json
import logging

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
        "managers": {"type": "array", "items": {"type": "integer"}},
        "announcement_channel": {"type": "integer"},
        "logs_channel": {"type": "integer"},
    },
    "required": ["managers", "teams", "voting_open", "offset", "round_period"]
}

default = {"teams": [], "voting_open": False, "offset": 0, "round_period": 20}
    
    
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


def start_datetime():
    return (datetime.datetime.fromisoformat(data["start"]).replace(tzinfo=datetime.timezone.utc)
    + datetime.timedelta(hours=data["offset"]))

def end_datetime():
    return (datetime.datetime.fromisoformat(data["end"]).replace(tzinfo=datetime.timezone.utc)
    + datetime.timedelta(hours=data["offset"])) + datetime.timedelta(hours=data["round_period"])

def is_active():
    # TODO test these
    if not data["start"] or not data["end"]:
        return False # game dates not configured
    
    utcnow = datetime.datetime.now(datetime.timezone.utc)
    
    return (start_datetime() <= utcnow < end_datetime())

def is_before():
    if not data["start"]:
        return False
    
    utcnow = datetime.datetime.now(datetime.timezone.utc)
    return start_datetime() < utcnow

def is_after():
    if not data["end"]:
        return False
    
    utcnow = datetime.datetime.now(datetime.timezone.utc)
    return end_datetime() <= utcnow

def turns_open():
    if not is_active():
        return False
    
    utcnow = datetime.datetime.now(datetime.timezone.utc)
    
    # specific to today
    start = (utcnow.replace(hour=0, minute=0, second=0, microsecond=0)
             + datetime.timedelta(hours=data["offset"]))
    end = start + datetime.timedelta(hours=data["round_period"])
    
    return start <= utcnow < end
    
    

def game_title():
    title = ""
    if len(data["teams"]) > 0:          
        for i in data["teams"]:
            title += f"{i["name"]} vs "
        return title[:-4] # slice trailing " vs "
    else:
        return "No teams set!"