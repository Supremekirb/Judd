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


def field_ready():
    # all keys in dict
    if not all(key in data for key in ["tile_size", "image", "width", "height", "field"]):
        return False
    # the image also has to exist
    elif not os.path.exists(data["image"]):
        return False
    else:
        return True
    
def move_points(position: tuple[int, int], spaces: int):
    """Get a list of points which can be travelled to in `spaces` in a straight line.\nReturns left, right, up, down"""
    x, y = position
    
    left = x
    while left > 0 and x-left < spaces and data["field"][left-1][y] != -1:
        left -= 1
        
    right = x
    while right < data["width"]-1 and right-x < spaces and data["field"][right+1][y] != -1:
        right += 1
        
    up = y
    while up > 0 and y-up < spaces and data["field"][x][up-1] != -1:
        up -= 1
        
    down = y
    while down < data["height"]-1 and down-y < spaces and data["field"][x][down+1] != -1:
        down += 1
        
    return (left, y), (right, y), (x, up), (x, down)
        
        
CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def to_chess(x: int, y: int):
    letters = ""
    while x >= 0:
        letters = CHARS[x % len(CHARS)] + letters
        x //= 26
        x -= 1 
    
    return f"{letters}{y}"

def from_chess(chess: str):
    if not chess.isalnum():
        raise ValueError(f"String {chess} is not alphanumeric!")
    
    if not chess[0].isalpha():
        raise ValueError(f"String {chess} does not start with an alphabetic character!")
    
    alpha = ""
    index = 0
    while len(chess) > index and chess[index].isalpha():
        alpha += chess[index]
        index += 1

    numeric = chess[index:]
    if not numeric.isnumeric():
        raise ValueError(f"String {chess} is not letters followed by numbers only!")
    
    x: int = 0
    values = list(CHARS.index(char)+1 for char in alpha.upper())
    values.reverse()
    for index, val in enumerate(values):
        x += 26**index * val

    return (x, int(numeric))