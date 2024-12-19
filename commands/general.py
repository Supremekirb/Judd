import copy

import discord

import commands.checks
import game.fielddata
import game.gamedata
import game.playerdata


@discord.app_commands.command(description="Save all data files to disk (routinely occurs automatically)")
@discord.app_commands.guild_only()
async def save_all(interaction: discord.Interaction):
    if not await commands.checks.owner_handler(interaction): return
    
    try:
        # game.fielddata.save()
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
        await interaction.response.send_message("Reset successfully!")
    except Exception as e:
        await interaction.response.send_message(f"Something went wrong when resetting! Error was {str(e)}!")
        raise