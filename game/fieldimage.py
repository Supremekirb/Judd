import math

from PIL import Image, ImageDraw

from game import fielddata, gamedata, playerdata

# TODO caching for a lot of this stuff. It doesn't make sense to re-composite some of these
# every time they are called. However as turf changes the cache will need to be purged

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


_im = Image.open(fielddata.data["image"])


# create a version with the grid overlayed on it
_grid_im = _im.copy()
_grid_draw = ImageDraw.Draw(_grid_im)
for x in range(0, _grid_im.width, fielddata.data["tile_size"]):
    _grid_draw.line(((x, 0), (x, _grid_im.height-1)), width=max(1, fielddata.data["tile_size"]*0.05), fill="black")
for y in range(0, _grid_im.height, fielddata.data["tile_size"]):
    _grid_draw.line(((0, y), (_grid_im.width-1, y)), width=max(1, fielddata.data["tile_size"]*0.05), fill="black")
del _grid_draw


# create an overlay just for paint colours. use alpha composite
_paint_im = Image.new(mode="RGBA", size=_im.size, color=(0, 0, 0, 0))

def update_paint_overlay():
    paint_draw = ImageDraw.Draw(_paint_im)
    for x, col in enumerate(fielddata.data["field"]):
        for y, cell in enumerate(col):
            if cell in (-1, None):
                continue
            colour = hex_colour_to_pil(gamedata.data["teams"][cell]["colour"])
            colour += "7F"
            size = fielddata.data["tile_size"]
            cx = x*size
            cy = y*size
            paint_draw.rectangle(((cx, cy), (cx+size-1, cy+size-1)), fill=colour)
    del paint_draw
    
update_paint_overlay()
    

# create an overlay just for solid objects. use alpha composite
_solid_im = Image.new(mode="RGBA", size=_im.size, color=(0, 0, 0, 0))
_solid_draw = ImageDraw.Draw(_solid_im)
for x, col in enumerate(fielddata.data["field"]):
    for y, cell in enumerate(col):
        if cell == -1:
            size = fielddata.data["tile_size"]
            cx = x*size
            cy = y*size
            _solid_draw.rectangle(((cx, cy), (cx+size-1, cy+size-1)), fill="#0000007F")
del _solid_draw


def player_move_area(position: tuple[int, int], spaces: int, team_colour: int=0):
    image = _grid_im.copy()
    image.alpha_composite(_paint_im)
    image.alpha_composite(_solid_im)
    
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
    image.alpha_composite(_paint_im)
    image.alpha_composite(_solid_im)
    
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


def overview(paint: bool=True, grid: bool=True, collision: bool=True, teams: list[int]=[], only_frozen: bool=False):
    if grid:
        image = _grid_im.copy()
    else:
        image = _im.copy()
        
    if paint:
        image.alpha_composite(_paint_im)
    
    if collision:
        image.alpha_composite(_solid_im)
    
    if teams:
        occupied = {}
        draw = ImageDraw.Draw(image)
        for uid in playerdata.data:
                player = playerdata.data[uid]
                if player["team"] in teams:
                    if (only_frozen and player["frozen"]) or not only_frozen:
                        colour = hex_colour_to_pil(gamedata.data["teams"][player["team"]]["colour"])
                        
                        tile_size: int = fielddata.data["tile_size"]
                        centerX = player["position"][0]*tile_size + tile_size//2
                        centerY = player["position"][1]*tile_size + tile_size//2
                        
                        # this is a little weird but it works
                        # tuple necessary for hashing..?
                        here = occupied.setdefault(tuple(player["position"]), 1)
                        occupied[tuple(player["position"])] += 1
                        
                        if here > 1:
                            draw.circle((centerX, centerY), radius=0.6*tile_size, fill="black")
                            draw.text((centerX, centerY), text=str(here), align="center", fill="white")
                        else:
                            draw.circle((centerX, centerY), radius=0.3*tile_size, fill=colour)
        
    return image


def location(location_tile: tuple[int, int], padding: int=5, indicator: bool=True, paint: bool=True, grid: bool=True, collision: bool=True, teams: list[int]=[], only_frozen: bool=False):
    image = overview(paint, grid, collision, teams, only_frozen)
    tile_size: int = fielddata.data["tile_size"]
    location = (location_tile[0]*tile_size + tile_size//2, location_tile[1]*tile_size + tile_size//2)
    
    if indicator:
        draw = ImageDraw.Draw(image)
        draw.circle(location, 0.4*tile_size, fill="white")
        draw.circle(location, 0.3*tile_size, fill="black")
    
    return standard_size(area_image(image, location, tile_size*padding))