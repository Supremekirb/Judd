import datetime

import discord

import commands.checks
import game.fielddata
import game.gamedata
import game.playerdata


@discord.app_commands.command(description="View info about the game")
async def info(interaction: discord.Interaction):
    embed = discord.Embed()
    embed.set_author(name="Game info")
    embed.title = game.gamedata.game_title()
    
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
@discord.app_commands.guild_only()
async def open_voting(interaction: discord.Interaction):
    if not await commands.checks.manager_handler(interaction): return
    
    if game.gamedata.is_active():
        await interaction.response.send_message("Can't open voting during the game!")
        
    elif game.gamedata.is_after():
        await interaction.response.send_message("Can't open voting after the game!")
        
    else:
        game.gamedata.data["voting_open"] = True
        await interaction.response.send_message("Voting is now open!")


@discord.app_commands.command(description="Stop letting people vote")
@discord.app_commands.guild_only()
async def close_voting(interaction: discord.Interaction):
    if not await commands.checks.manager_handler(interaction): return
    
    game.gamedata.data["voting_open"] = False
    await interaction.response.send_message("Voting is now closed!")
    
    
@discord.app_commands.command(description="Schedule the game, and therefore begin it.")
@discord.app_commands.describe(
    start = "Game start date (ISO 8601 format YYYY-MM-DD)",
    end = "Game end date (ISO 8601 format YYYY-MM-DD)",
    offset = "How many hours from UTC things should happen (range -12 to 12)",
    round_period = "How many hours players can cast their votes for (recommended 20, range 1 to 23)"
)
@discord.app_commands.guild_only()
async def schedule(interaction: discord.Interaction, start: str, end: str,
                   offset: discord.app_commands.Range[int, -12, 12], round_period: discord.app_commands.Range[int, 1, 23]):
    if not await commands.checks.manager_handler(interaction): return
    
    if len(game.gamedata.data["teams"]) < 2:
        await interaction.response.send_message("Cannot schedule the game until there's two or more teams!")
        return
    
    try:
        startdate = datetime.date.fromisoformat(start)
        enddate = datetime.date.fromisoformat(end)
    except ValueError:
        await interaction.response.send_message("You probably used the wrong date format! It's YYYY-MM-DD.")
        raise 

    if startdate >= enddate:
        await interaction.response.send_message("The start cannot be the same or later than the end!")
        raise ValueError("Start date greater than or equal to end date")

    if startdate <= datetime.datetime.now(datetime.timezone.utc).date():
        await interaction.response.send_message("The start date must be after today!")
        raise ValueError("Start date less than or equal to current date")
    
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
    

@discord.app_commands.command(description="Add a manager of the game. They can execute protected commands.")
@discord.app_commands.describe(
    user="User to add as a manager")
@discord.app_commands.guild_only()
async def add_manager(interaction: discord.Interaction, user: discord.User):
    if not await commands.checks.manager_handler(interaction): return
    
    if user.id not in game.gamedata.data["managers"]:
        game.gamedata.data["managers"].append(user.id)
        await interaction.response.send_message(f"{user.display_name} is now a game manager!")
    else:
        await interaction.response.send_message(f"{user.display_name} is already a manager!")
      
        
@discord.app_commands.command(description="Remove a manager of the game.")
@discord.app_commands.describe(
    user="User to remove from being a manager")
@discord.app_commands.guild_only()
async def remove_manager(interaction: discord.Interaction, user: discord.User):
    if not await commands.checks.manager_handler(interaction): return
    
    if user.id == interaction.client.application.owner.id:
        await interaction.response.send_message(f"{user.display_name} is the host of the bot and cannot be removed!")
    
    elif user.id in game.gamedata.data["managers"]:
        game.gamedata.data["managers"].pop(game.gamedata.data["managers"].index(user.id))
        await interaction.response.send_message(f"{user.display_name} is no longer a game manager!")
    else:
        await interaction.response.send_message(f"{user.display_name} is not a manager!")


@discord.app_commands.command(description="Set/unset the channel to post game-related announcements to")
@discord.app_commands.describe(
    enabled="If announcements should occur",
    channel="Channel to post to (optional, required only if `enabled` is true)"
)
@discord.app_commands.guild_only()
async def config_announcements(interaction: discord.Interaction, enabled: bool, channel: discord.TextChannel=None):
    if not await commands.checks.manager_handler(interaction): return
    
    if not enabled:
        game.gamedata.data.pop("announcement_channel", None)
        await interaction.response.send_message("No announcements will be posted!")
    
    else:
        if not channel:
            await interaction.response.send_message("If `enabled` is true, you must specify a channel!")
        else:
            game.gamedata.data["announcement_channel"] = channel.id
            await interaction.response.send_message(f"Set announcement channel to <#{channel.id}>!")


@discord.app_commands.command(description="Set/unset the channel of which to post game-related logs, such as player turns")
@discord.app_commands.describe(
    enabled="If logs should be recorded",
    channel="Channel to post to (optional, required only if `enabled` is true)"
)
@discord.app_commands.guild_only()
async def config_logs(interaction: discord.Interaction, enabled: bool, channel: discord.TextChannel=None):
    if not await commands.checks.manager_handler(interaction): return
    
    if not enabled:
        game.gamedata.data.pop("logs_channel", None)
        await interaction.response.send_message("No logs will be posted!")
    
    else:
        if not channel:
            await interaction.response.send_message("If `enabled` is true, you must specify a channel!")
        else:
            game.gamedata.data["logs_channel"] = channel.id
            await interaction.response.send_message(f"Set log channel to <#{channel.id}>!")
    