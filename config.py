import json
import logging

DATA_FILE = "config.json"

DEFAULT_CONFIG = {
    "debug_guild_sync_ids": [],
    
    "projectile_name": "snowball",
    "projectile_name_plural": "snowballs",
    
    "frozen_name": "frozen",
    "frozen_name_verb": "freeze",
    
    "moves": 1,
    "throws": 3,
    
    "move_distance_max": 6,
}

try:
    with open(DATA_FILE) as file:
        _data = json.load(file)
except FileNotFoundError:
    logging.warning("No config found, creating new...")
    _data = DEFAULT_CONFIG
    with open(DATA_FILE, "w") as file:
        json.dump(DEFAULT_CONFIG, file, indent=4)

debug_guild_sync_ids: list[int] = _data["debug_guild_sync_ids"]
projectile_name: str = _data["projectile_name"]
projectile_name_plural: str = _data["projectile_name_plural"]
frozen_name: str = _data["frozen_name"]
frozen_name_verb: str = _data["frozen_name_verb"]
moves: int = _data["moves"]
throws: int = _data["throws"]
move_distance_max: int = _data["move_distance_max"]