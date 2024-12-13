import datetime

import discord

import game.fielddata
import game.gamedata
import game.playerdata


@discord.app_commands.command(description="View info about the game")
async def info(interaction: discord.Interaction):
    embed = discord.Embed()
    embed.set_author(name="Game info")
    title = ""
    if len(game.gamedata.data["teams"]) > 0:          
        for i in game.gamedata.data["teams"]:
            title += f"{i["name"]} vs "
        title = title[:-4] # slice trailing " vs "
    else:
        title = "No teams set!"
    embed.title = title
    
    if "start" in game.gamedata.data and "end" in game.gamedata.data:
        embed.add_field(name="Start", value=game.gamedata.data["start"], inline=True)
        embed.add_field(name="End", value=game.gamedata.data["end"], inline=True)
        
    if game.gamedata.data["voting_open"]:
        embed.add_field(name="Voting", value="Open", inline=False)
    else:
        embed.add_field(name="Voting", value="Closed", inline=False)
        
    embed.add_field(name="UTC offset", value=game.gamedata.data["offset"], inline=False)
    embed.add_field(name="Round period", value=f"{game.gamedata.data["round_period"]}h", inline=False)
    
    await interaction.response.send_message(embed=embed)

@discord.app_commands.command(description="Begin letting people vote!")
async def open_voting(interaction: discord.Interaction):
    game.gamedata.data["voting_open"] = True
    await interaction.response.send_message("Voting is now open!")


@discord.app_commands.command(description="Stop letting people vote")
async def close_voting(interaction: discord.Interaction):
    game.gamedata.data["voting_open"] = False
    await interaction.response.send_message("Voting is now closed!")
    
    
@discord.app_commands.command(description="Schedule the game, and therefore begin it.")
@discord.app_commands.describe(
    start = "Game start date (ISO 8601 format YYYY-MM-DD)",
    end = "Game end date (ISO 8601 format YYYY-MM-DD)",
    offset = "How many hours from UTC things should happen. Range: -12 to 14",
    round_period = "How many hours players can cast their votes for. Range: 1 to 23."
)
async def schedule(interaction: discord.Interaction, start: str, end: str, offset: int, round_period: int):
    try:
        startdate = datetime.date.fromisoformat(start)
        enddate = datetime.date.fromisoformat(end)
    except ValueError:
        await interaction.response.send_message("You probably used the wrong date format! It's YYYY-MM-DD.")
        raise 

    if startdate >= enddate:
        await interaction.response.send_message("The start cannot be the same or later than the end!")
        raise ValueError("Start date greater than end date")
    
    if offset < -12 or offset > 14:
        await interaction.response.send_message("The offset must be in range -12 to 14!")
        raise ValueError(f"Invalid game event offset {offset}")

    if round_period < 1 or round_period > 23:
        await interaction.response.send_message("The round period must be in range 1 to 23!")
        raise ValueError(f"Invalid game round period {round_period}")
    
    game.gamedata.data["start"] = start
    game.gamedata.data["end"] = end
    game.gamedata.data["offset"] = offset
    game.gamedata.data["round_period"] = round_period
    
    await interaction.response.send_message("This game has been scheduled! It will proceed automatically at the start time + offset.\nTo cancel, use `/reset_all`.")
    