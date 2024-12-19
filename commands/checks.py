import discord

import game.gamedata


def user_is_manager(interaction: discord.Interaction):
    if interaction.user.id == interaction.client.application.owner.id: # host/owner will always be a manager
        if interaction.user.id not in game.gamedata.data["managers"]:
            game.gamedata.data["managers"].append(interaction.user.id)
            
    return (interaction.user.id in game.gamedata.data["managers"])

async def manager_handler(interaction: discord.Interaction):
    """For commands that can only be used by managers, use `if not await commands.checks.manager_handler(interaction): return`"""
    if not user_is_manager(interaction):
        await interaction.response.send_message("Only managers can use this command!", ephemeral=True)
        return False
    
    else:
        return True

async def owner_handler(interaction: discord.Interaction):
    """For commands that can only be used by the bot owner/host, use `if not await commands.checks.owner_handler(interaction): return`"""
    if interaction.user.id != interaction.client.application.owner.id:
        await interaction.response.send_message("Only the bot's host can use this command!", ephemeral=True)
        return False
    
    else:
        return True