import copy
import io
import os

import discord

import commands.checks
import game.fielddata
import game.fieldimage
import game.gamedata
import game.playerdata


@discord.app_commands.command(description="Get an image of the whole map")
@discord.app_commands.describe(
    show_grid = "Show the grid on this image",
    show_terrain = "Show solid tiles on this image",
    show_my_team = "If you're participating, show the members of your team. The message will only show to you."
)
async def map(interaction: discord.Interaction, show_grid: bool=False, show_terrain: bool=False, show_my_team: bool=False):
    if not game.fielddata.field_ready():
        return await interaction.response.send_message("There is no map to display! Set one up with /setup_map!")
    
    team = []
    if show_my_team:
        try:
            player = game.playerdata.data[str(interaction.user.id)]
            team = [player["team"]]
        except KeyError:
            return await interaction.response.send_message("You can only use `show_my_team` if you are participating!")
    
    image = game.fieldimage.overview(grid=show_grid, collision=show_terrain, teams=team)
    
    with io.BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename='map.png')
    
    embed = discord.Embed(
        title="Game Map",
        description=f"Use `/location` for a close-up of an area!"
    )
    embed.set_image(url="attachment://map.png")
    embed.set_author(name=game.gamedata.game_title())
    
    await interaction.response.send_message(embed=embed, file=file, ephemeral=show_my_team)


@discord.app_commands.command(description="Get a close-up of an area")
@discord.app_commands.describe(
    location = "Chess notation (eg. B6, H23, AB3)",
    zoom_out = "How many tiles around here you want to see",
    show_indicator = "Show a dot on this tile",
    show_grid = "Show the grid on this image",
    show_terrain = "Show solid tiles on this image",
    show_my_team = "If you're participating, show the members of your team. The message will only show to you."
)
async def location(interaction: discord.Interaction, location: str, zoom_out: int=5, show_indicator: bool=True, show_grid: bool=True, show_terrain: bool=False, show_my_team: bool=False):
    if not game.fielddata.field_ready():
        return await interaction.response.send_message("There is no map to display! Set one up with /setup_map!")
    
    try:
        target = game.fielddata.from_chess(location)
    except ValueError:
        await interaction.response.send_message("You must use alphanumeric coordinates (eg. B6, H23, AB3)!")
        return
    if target[0] >= game.fielddata.data["width"] or target[1] >= game.fielddata.data["height"]:
        await interaction.response.send_message(f"{location} would be out of bounds!")
        return
    
    team = []
    if show_my_team:
        try:
            player = game.playerdata.data[str(interaction.user.id)]
            team = [player["team"]]
        except KeyError:
            return await interaction.response.send_message("You can only use `show_my_team` if you are participating!")
    
    image = game.fieldimage.location(target, zoom_out, indicator=show_indicator, grid=show_grid, collision=show_terrain, teams=team)
    
    with io.BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename='location.png')
    
    embed = discord.Embed(
        title="Location Map",
        description=f"Use `/map` for a view of the whole game!"
    )
    embed.set_image(url="attachment://location.png")
    embed.set_author(name=game.gamedata.game_title())
    
    await interaction.response.send_message(embed=embed, file=file, ephemeral=show_my_team)
    

@discord.app_commands.command(description="Save all data files to disk (routinely occurs automatically)")
@discord.app_commands.guild_only()
async def save_all(interaction: discord.Interaction):
    if not await commands.checks.owner_handler(interaction): return
    
    try:
        game.fielddata.save()
        game.gamedata.save()
        game.playerdata.save()
        await interaction.response.send_message("Saved successfully!")
    except Exception as e:
        await interaction.response.send_message(f"Something went wrong when saving! Error was {str(e)}!")
        raise
    
@discord.app_commands.command(description="Reload from data on disk")
@discord.app_commands.guild_only()
async def load_all(interaction: discord.Interaction):
    if not await commands.checks.owner_handler(interaction): return
    
    try:
        game.fielddata.load()
        game.gamedata.load()
        game.playerdata.load()
        await interaction.response.send_message("Loaded successfully!")
    except Exception as e:
        await interaction.response.send_message(f"Something went wrong when loading! Error was {str(e)}!")
        raise
    
@discord.app_commands.command(description="Reset ALL data to defaults. The bot may need to be rebooted for scheduled things to work.")
@discord.app_commands.guild_only()
async def reset_all(interaction: discord.Interaction):
    if not await commands.checks.owner_handler(interaction): return
    
    try:
        game.fielddata.data = copy.deepcopy(game.fielddata.default)
        game.gamedata.data = copy.deepcopy(game.gamedata.default)
        game.playerdata.data = copy.deepcopy(game.playerdata.default)
        if os.path.exists("map.png"): os.remove("map.png")
        
        await interaction.response.send_message("Reset successfully!")
    except Exception as e:
        await interaction.response.send_message(f"Something went wrong when resetting! Error was {str(e)}!")
        raise