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
    team = []
    if show_my_team:
        try:
            player = game.playerdata.data[str(interaction.user.id)]
            team = [player["team"]]
        except IndexError:
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