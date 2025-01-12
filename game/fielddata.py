import copy
import json
import logging
import os

import jsonschema
import PIL
import PIL.Image
import PIL.ImageFile

DATA_FILE = "field.json"

schema = {
    "type": "object",
    "properties": {
      "field": { # 2D array
          "type": "array",
          "items": {
            "type": "array",
            "items": {"type": ["integer", "null"]} # team id for claimed turf, -1 for solid, or null for open space
            },
        },
      "tile_size": {"type": "integer"},
      "width": {"type": "integer"}, # in tile sizes
      "height": {"type": "integer"}, # in tile sizes
      "image": {"type": "string"}, # path
      "backup_base_field": { # 2D array, just the collision (in case all turns need to be reapplied in sequence)
          "type": "array",
          "items": {
              "type": "array",
              "items": {"type": ["integer", "null"]}
            },
        }, 
    },
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
        logging.warning("No field data found, creating new...")
        data = copy.deepcopy(default)
        save()

load()
        
def field_config(imgPath: str, tile_size: int, mask: tuple[tuple[int|None]]):
    global data
    img = PIL.Image.open(imgPath)
    width = img.width // tile_size
    height = img.height // tile_size
    
    if img.width % tile_size or img.height % tile_size: # nonzero modulo means an imperfect fit
        logging.warning("Tile size does not fit neatly into image size! Rounding down the invalid dimensions to fit.")
        cropped = img.crop((0, 0, width * tile_size, height * tile_size))
        cropped.save(imgPath)
    
    data["image"] = imgPath
    data["width"] = width
    data["height"] = height
    data["tile_size"] = tile_size
    data["field"] = mask
    data["backup_base_field"] = mask


def field_ready():
    if not all(x in data for x in ["tile_size", "image", "width", "height", "field", "backup_base_field"]):
        return False
    elif not os.path.exists(data["image"]):
        return False
    else:
        return True
        
        
CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def toChess(x: int, y: int):
    letters = ""
    while x >= 0:
        letters = CHARS[x % len(CHARS)] + letters
        x //= 26
        x -= 1 
    
    return f"{letters}{y}"