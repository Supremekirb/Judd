import io

import discord
import PIL
import PIL.Image

import commands.checks
import game.fielddata


@discord.app_commands.command(description="Set up the map")
@discord.app_commands.guild_only()
@discord.app_commands.describe(
    map = "Display image of the game map",
    collision_mask = "Collision overlay of the map. A grid cell with ANY non-transparent pixels will be considered solid",
    tile_size = "Pixel size of each tile. If this does not align with the map size, the map image will be trimmed down."
)
async def setup_map(interaction: discord.Interaction, map: discord.Attachment, collision_mask: discord.Attachment, tile_size: int):
    if not await commands.checks.manager_handler(interaction): return
    
    # check attachment mimetype
    if not map.content_type.startswith("image/") or not collision_mask.content_type.startswith("image/"):
        await interaction.response.send_message(f"Attachments must be image files! Recieved `{map.content_type}` for the map and `{collision_mask.content_type}` for the collision mask.")
        return
    
    # getting images
    buffer = io.BytesIO()
    try:
        await map.save(buffer)
        map_img = PIL.Image.open(buffer)
    except Exception:
        await interaction.response.send_message("Failed to get map image!")
        raise
    
    buffer = io.BytesIO()
    try:
        await collision_mask.save(buffer)
        mask_img = PIL.Image.open(buffer)
    except Exception:
        await interaction.response.send_message("Failed to get collision mask image!")
        raise

    # check dimensions
    if map_img.size != mask_img.size:
        await interaction.response.send_message("Map and collision mask must have the same dimensions!")

    # creating the mask array
    try:       
        pixels: list[tuple[int]] = list(mask_img.getdata())
        width_tiles = mask_img.width//tile_size
        height_tiles = mask_img.height//tile_size
        mask_array = [[None for _ in range(0, height_tiles)] for _ in range(0, width_tiles)] # index first by x, then by y
        
        # iterate over image pixels, step per tile
        # for each tile, check if any pixels in it are opaque
        for y in range(0, mask_img.height, tile_size):
            for x in range(0, mask_img.width, tile_size):
                root_index = x + y*mask_img.width
                for row in range(tile_size): # we only need to iterate over this axis since we can use a slice to check the rest
                    row_index = root_index + row*mask_img.width
                    if any(pix[-1] for pix in pixels[row_index : row_index + tile_size]): # aforementioned slice
                        mask_array[x//tile_size][y//tile_size] = -1 # set to -1 for "solid"
                        break # and we don't need to do this anymore
    except Exception:
        await interaction.response.send_message("Failed to calculate collision mask!")
        raise
    
    # save map
    try: 
        map_img.save("map.png")
    except Exception:
        await interaction.response.send_message("Failed to save map image to disk!")
        raise
    # we don't need to save the mask though
    
    try:
        game.fielddata.field_config("map.png", tile_size, mask_array)
        
    except Exception: # shouldn't ever trigger? but just in case I sup[pose]
        await interaction.response.send_message("Failed to apply new map config to game!")
        raise
    
    await interaction.response.send_message("Map setup complete!")