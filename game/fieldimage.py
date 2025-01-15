import math

from PIL import Image, ImageDraw

from game import fielddata

_im = Image.open(fielddata.data["image"])

# create a version with the grid overlayed on it
_grid_im = _im.copy()

_grid_draw = ImageDraw.Draw(_grid_im)
for x in range(0, _grid_im.width, fielddata.data["tile_size"]):
    _grid_draw.line(((x, 0), (x, _grid_im.height-1)), width=max(1, fielddata.data["tile_size"]*0.05), fill="black")
for y in range(0, _grid_im.height, fielddata.data["tile_size"]):
    _grid_draw.line(((0, y), (_grid_im.width-1, y)), width=max(1, fielddata.data["tile_size"]*0.05), fill="black")
del _grid_draw


STANDARDSIZE = 256
def standard_size(image: Image.Image):
    aspect_ratio = image.height / image.width
    return image.resize((STANDARDSIZE, int(STANDARDSIZE*aspect_ratio)), resample=Image.Resampling.NEAREST)

def area_image(image: Image.Image, center: tuple[int, int], padding: int):
    centerX, centerY = center
    left = max(0, centerX - padding) 
    right = min(image.width-1 , centerX + padding)
    top = max(0, centerY - padding)
    bottom = min(image.height-1, centerY + padding)
    return image.crop((left, top, right, bottom))
    
def hex_colour_to_pil(colour: int=0):
    return "#" + hex(colour).removeprefix("0x").zfill(6)


def player_move_area(position: tuple[int, int], spaces: int, team_colour: int=0):
    image = _grid_im.copy()  
    
    pil_team_colour = hex_colour_to_pil(team_colour)
    
    draw = ImageDraw.Draw(image)
    tile_size: int = fielddata.data["tile_size"]
    targets = fielddata.move_points(position, spaces)
    
    x, y = position
    
    centerX = x*tile_size + tile_size//2
    centerY = y*tile_size + tile_size//2
    
    draw.circle((centerX, centerY), radius=0.3*tile_size, fill=pil_team_colour)
    
    for t in targets:
        draw.line(((centerX, centerY), tuple((int(coord*tile_size + tile_size//2) for coord in t))),
                  fill=pil_team_colour,
                  width=int(max(1, 0.1*tile_size)))
        
        draw.circle(tuple((int(coord*tile_size + tile_size//2) for coord in t)),
                    radius=0.2*tile_size, fill=pil_team_colour)
        
    return standard_size(area_image(image, (centerX, centerY), tile_size*(spaces+1))) # one tile of extra padding


def player_moved_to(start: tuple[int, int], end: tuple[int, int], team_colour: int=0):
    image = _grid_im.copy()  
    
    pil_team_colour = hex_colour_to_pil(team_colour)
    
    draw = ImageDraw.Draw(image)
    tile_size: int = fielddata.data["tile_size"]
    
    sx, sy = start
    
    centerX = sx*tile_size + tile_size//2
    centerY = sy*tile_size + tile_size//2
    
    draw.circle((centerX, centerY), radius=0.3*tile_size, fill=pil_team_colour)
    draw.line(((centerX, centerY), tuple((int(coord*tile_size + tile_size//2) for coord in end))),
                fill=pil_team_colour,
                width=int(max(1, 0.1*tile_size)))
        
    draw.circle(tuple((int(coord*tile_size + tile_size//2) for coord in end)),
                radius=0.2*tile_size, fill=pil_team_colour)
    
    # formula for distance of line given delta x and y (Pythagoras, 1900 BC) 
    distance = math.sqrt(abs((start[0] - end[0]))**2 + abs((start[1] - end[1]))**2)
    
    return standard_size(area_image(image, (centerX, centerY), tile_size*(distance+1))) # one tile of extra padding