import json
import logging

DATA_FILE = "config.json"

DEFAULT_CONFIG = {
    "debug_guild_sync_ids": [], # guilds to sync commands to for debugging purposes
    
    "projectile_name": "snowball", # singular display name of projectile
    "projectile_name_plural": "snowballs", # plural display name of projectile
    
    "frozen_name": "frozen", # adjective for frozen status
    "frozen_name_verb": "freeze", # verb for frozen status
    
    "moves": 1, # max times players can move each turn
    "throws": 3, # max times players can throw each turn
    
    "move_distance_max": 6, # highest possible roll for movement
    "move_distance_min": 1, # lowest possible roll for movement
    
    "save_interval": 15, # interval in minutes between saving
    "retry_interval": 10, # interval in minutes between trying again after a failed event
    "max_retries": 12, # maximum amount of times failed events can be retried
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
move_distance_min: int = _data["move_distance_min"]
save_interval: int = _data["save_interval"]
retry_interval: int = _data["retry_interval"]
max_retries: int = _data["max_retries"]