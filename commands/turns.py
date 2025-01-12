import discord

import game.fielddata
import game.gamedata
import game.playerdata

import gamelog.send

@discord.app_commands.command(description="Perform your move for the day!")
@discord.app_commands.dm_only()
async def move(interaction: discord.Interaction):
    if not game.gamedata.is_active():
        await interaction.response.send_message("The game is not active!")
        
    elif not game.gamedata.turns_open():
        await interaction.response.send_message("Turns aren't open for today!")
    
    elif not isinstance(interaction.channel, discord.channel.DMChannel):
        await interaction.response.send_message("You can only use this in a DM!")
        
    elif not str(interaction.user.id) in game.playerdata.data:
        await interaction.response.send_message("You didn't sign up to this game, so you cannot play!")
        
    else:
        await interaction.response.send_message("You can do this!")
        
        team = game.gamedata.data["teams"][game.playerdata.data[str(interaction.user.id)]["team"]]
        
        embed = discord.Embed(
            colour=team["colour"],
            description=f"{interaction.user.mention} of Team {team["name"]} moved!",
        )
        embed.set_author(name=f"Player moved")
            
        await gamelog.send.log(interaction.client, embed=embed)