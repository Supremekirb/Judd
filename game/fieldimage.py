from PIL import Image, ImageDraw

from game import fielddata

_im = Image.open(fielddata.data["image"])

def player_move_area(position: tuple[int, int], spaces: int, team_colour: int=0):
    image = _im.copy()  
    
    pil_team_colour = "#" + hex(team_colour).removeprefix("0x").zfill(6)
    
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
    
    left = max(0, centerX - tile_size*(spaces+1)) # one tile of border space
    right = min(_im.width-1 , centerX + tile_size*(spaces+1))
    top = max(0, centerY - tile_size*(spaces+1))
    bottom = min(_im.height-1, centerY + tile_size*(spaces+1))
    
    cropped = image.crop((left, top, right, bottom))
    
    aspect_ratio = cropped.height / cropped.width
    return cropped.resize((256, int(256*aspect_ratio)), resample=Image.Resampling.NEAREST)