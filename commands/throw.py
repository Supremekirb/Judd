import io
import typing

import discord

import config
import game.fielddata
import game.fieldimage
import game.gamedata
import game.playerdata
import gamelog.send


class ThrowModal(discord.ui.Modal, title="Aim and throw!"):
    location = discord.ui.TextInput(
        label="Target location",
        placeholder="eg. B6, H23, AB3. Not sure? Use /map or /location."
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        player = game.playerdata.data[str(interaction.user.id)]
        team = game.gamedata.data["teams"][player["team"]]
        
        try:
            target = game.fielddata.from_chess(self.location.value)
        except ValueError:
            await interaction.response.send_message("You must use alphanumeric coordinates (eg. B6, H23, AB3). If you're not sure, use `/map` or `/location` to find a target!")
            return
        if target[0] >= game.fielddata.data["width"] or target[1] >= game.fielddata.data["height"]:
            await interaction.response.send_message(f"{self.location.value} would be out of bounds!")
            return
        
        # TODO raycast check
        # TODO send image
        player["queued_actions"].append({"name": "throw", "target": target})
        
        embed = discord.Embed(
            colour=team["colour"],
            title="Throw",
            description=f":boom: You threw a {config.projectile_name} to **{self.location.value}**!"
        )
        embed.set_footer(text=f"This is throw {player["throws"]} of {config.throws} you can do today.")
        embed.set_author(name=game.gamedata.game_title())
        
        await interaction.response.send_message(embed=embed)
        
        # send a log
        embed = discord.Embed(
            colour=team["colour"],
            description=f"{interaction.user.mention} of Team {team["name"]} threw to {self.location.value}!",
        )
        embed.set_author(name=f"Player threw {config.projectile_name}")
        await gamelog.send.log(interaction.client, embed=embed)

@discord.app_commands.command(description=f"Throw a {config.projectile_name} at any location!")
# @discord.app_commands.dm_only()
async def throw(interaction: discord.Interaction):
    # if not isinstance(interaction.channel, discord.channel.DMChannel):
    #     await interaction.response.send_message("You can only use this in a DM!")
    
    # elif not str(interaction.user.id) in game.playerdata.data:
    #     await interaction.response.send_message("You didn't sign up to this game, so you cannot play!")
        
    # elif not game.gamedata.is_active():
    #     await interaction.response.send_message("The game is not active!")
        
    # elif not game.gamedata.turns_open():
    #     await interaction.response.send_message("Turns aren't open for today!")
        
    if game.playerdata.data[str(interaction.user.id)]["throws"] >= config.throws:
        await interaction.response.send_message(f"You have already thrown {config.projectile_name_plural} the maximum amount of times ({config.throws}) today!")
    
    elif game.playerdata.data[str(interaction.user.id)]["frozen"]:
        await interaction.response.send_message(f"You were {config.frozen_name} and cannot throw today!")

    else:
        player = game.playerdata.data[str(interaction.user.id)]
        team = game.gamedata.data["teams"][player["team"]]
        
        await interaction.response.send_modal(ThrowModal())