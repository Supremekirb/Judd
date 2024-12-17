import discord

import game.gamedata

def user_is_manager(interaction: discord.Interaction):
    if interaction.user.id == interaction.client.application.owner.id: # host/owner will always be a manager
        if interaction.user.id not in game.gamedata.data["managers"]:
            game.gamedata.data["managers"].append(interaction.user.id)
            
    return (interaction.user.id in game.gamedata.data["managers"])