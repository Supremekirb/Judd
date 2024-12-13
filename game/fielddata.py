import copy
import json
import logging

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
            "items": {"type": ["integer", "null"]} # team id or null
            },
        },
      "tileSize": {"type": "integer"},
      "width": {"type": "integer"}, # in tile sizes
      "height": {"type": "integer"}, # in tile sizes
      "image": {"type": "string"} # path 
    },
}

default = {}
    
    
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
        logging.warning("No field data found, creating new...")
        data = copy.deepcopy(default)
        save()

load()
        
def fieldconfig(imgPath: str, tileSize: int):
    global data
    img = PIL.Image.open(imgPath)
    width = img.width // tileSize
    height = img.height // tileSize 
    
    if not (img.width % tileSize or img.height % tileSize):
        logging.warning("Tile size does not fit neatly into image size! Rounding down the invalid dimensions to fit.")
        cropped = img.crop(0, 0, width * tileSize, height * tileSize).save
        cropped.save(imgPath)
        
        
CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def toChess(x: int, y: int):
    letters = ""
    while x >= 0:
        letters = CHARS[x % len(CHARS)] + letters
        x //= 26
        x -= 1 
    
    return f"{letters}{y}"