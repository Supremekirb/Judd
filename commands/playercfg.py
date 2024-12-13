import discord

import game.gamedata
import game.playerdata


class BaseTeamSelect(discord.ui.Select):
    def __init__(self):        
        options = []
        for id, i in enumerate(game.gamedata.data["teams"]):
            options.append(discord.SelectOption(label=i["name"], value=id))
        super().__init__(placeholder="Choose a team! No changing your mind!", options=options)        
        
class TeamJoinSelect(BaseTeamSelect):
    async def callback(self, interaction: discord.Interaction):
        game.playerdata.player_config(str(interaction.user.id), int(self.values[0]))
        await interaction.response.edit_message(content=f"You have joined Team {game.gamedata.data["teams"][int(self.values[0])]["name"]}!", view=None)
        
class TeamJoinView(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout=timeout)
        self.add_item(TeamJoinSelect())


@discord.app_commands.command()
@discord.app_commands.describe(
    user="User to get team of"
)
async def member_of(interaction: discord.Interaction, user: discord.User):
    """Get the team affiliation of a user"""
    try:
        data = game.playerdata.data[str(user.id)]
        embed = discord.Embed(
            colour = game.gamedata.data["teams"][data["team"]]["colour"],
            title = user.display_name,
            description = f"On Team {game.gamedata.data["teams"][data["team"]]["name"]}"
        ).set_author(name=user.global_name, icon_url=user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
        
    except KeyError:
        await interaction.response.send_message("This user has not signed up to any team!")
        
        
@discord.app_commands.command(description="Choose a team and join the game!")
async def signup(interaction: discord.Interaction):
    if len(game.gamedata.data["teams"]) == 0:
        await interaction.response.send_message("There are no teams to join! Add some with `/add_team`!")
    else:
        if game.gamedata.data["voting_open"]:
            if str(interaction.user.id) in game.playerdata.data:
                await interaction.response.send_message(f"You're already on Team {game.gamedata.data["teams"][game.playerdata.data[str(interaction.user.id)]["team"]]["name"]}!",
                                                        ephemeral=True)
            else:
                await interaction.response.send_message("Pick a team to join! There's no going back on your choice!", view=TeamJoinView(), ephemeral=True)
        else:
            await interaction.response.send_message("Voting is not open!")
    
        
@discord.app_commands.command(description="Remove a player from the game")
@discord.app_commands.describe(
    user="User to remove"
)
async def remove_player(interaction: discord.Interaction, user: discord.User):
    if str(user.id) in game.playerdata.data:
        del game.playerdata.data[str(user.id)]
        await interaction.response.send_message(f"{user.display_name} has been removed from the game.")
    else:
        await interaction.response.send_message(f"{user.display_name} is not in the game to begin with!")