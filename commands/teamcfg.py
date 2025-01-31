import discord

import commands.checks
import game.fielddata
import game.gamedata
import game.playerdata


@discord.app_commands.command(description="Add a new team")
@discord.app_commands.describe(
    name="Team display name (please capitalise!)",
    colour="Team colour (hex code)",
    x1="Left of this team's starting area box.",
    y1="Top of this team's starting area box.",
    x2="Right of this team's starting area box.",
    y2="Bottom of this team's starting area box."
)
    
@discord.app_commands.guild_only()
async def add_team(interaction: discord.Interaction, name: str, colour: int, x1: int, y1: int, x2: int, y2: int):
    if not await commands.checks.manager_handler(interaction): return
    
    if not game.fielddata.field_ready():
        return await interaction.response.send_message("Please configure the field first! Use `/setup_map`.")
    try:
        if (x1 > x2 or
            y1 > y2 or
            any(i < 0 for i in (x1, y1, x2, y2)) or
            max(x1, x2) >= game.fielddata.data["width"] or
            max(y1, y2) >= game.fielddata.data["height"] or
            game.fielddata.all_solid(x1, y1, x2, y2)):
                return await interaction.response.send_message("Invalid starting range config! The format is: X1, Y1, X2, Y2.")
    except Exception as e:
        pass
        
    id = game.gamedata.new_team(name, colour, (x1, y1, x2, y2))
    await interaction.response.send_message(f"Created Team \"{name}\" (its ID is {id})!")


@discord.app_commands.command(description="List all teams and member counts")
@discord.app_commands.guild_only()
async def list_teams(interaction: discord.Interaction):
    if not await commands.checks.manager_handler(interaction): return
    
    affiliations = game.playerdata.enumerate_affilations()
    content = ""
    for id, i in enumerate(game.gamedata.data["teams"]): # i in team lmao
        try:
            memberCount = affiliations[id]
        except KeyError:
            memberCount = 0
        content += f"`{id}` Team {i["name"]} ({memberCount} members)\n" # backslash bc lists auto-count from 1 (bad and stinky)
    
    if content == "":
        content = f"No teams configured for this game! Use `/add_team` to add some."
        
    await interaction.response.send_message(content)
    
    
@discord.app_commands.command(description="Get detailed team info by name or ID")
@discord.app_commands.describe(
    name_or_id="Team ID (integer) or team name (string)"
)
@discord.app_commands.guild_only()
async def team(interaction: discord.Interaction, name_or_id: str):   
    if not await commands.checks.manager_handler(interaction): return
    
    affiliations = game.playerdata.enumerate_affilations()
    embed = discord.Embed()
    try:
        name_or_id = int(name_or_id)
    except ValueError:
        pass
        
    if isinstance(name_or_id, int):
        try:
            try:
                memberCount = affiliations[name_or_id]
            except KeyError:
                memberCount = 0
                
            team = game.gamedata.data["teams"][name_or_id]
            embed.title = f"Team {team["name"]}"
            embed.colour = discord.Colour(team["colour"])
            embed.description = f"ID: {name_or_id}\nColour: {hex(team["colour"])}\nMembers: {memberCount}"
        except IndexError:
            await interaction.response.send_message("No team with this ID!")
            return
    
    if isinstance(name_or_id, str):            
        for id, i in enumerate(game.gamedata.data["teams"]):
            if i["name"].lower() == name_or_id.lower():
                try:
                    memberCount = affiliations[id]
                except KeyError:
                    memberCount = 0
                embed.title = f"Team {i["name"]}"
                embed.colour = discord.Colour(i["colour"])
                embed.description = f"ID: {id}\nColour: {hex(i["colour"])}\nMembers: {memberCount}"
                break
        else:
            await interaction.response.send_message("No team with this name!")
            return
            
    await interaction.response.send_message(embed=embed)
