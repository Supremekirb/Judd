import io
import random
import typing

import discord

import config
import game.fielddata
import game.fieldimage
import game.gamedata
import game.playerdata
import gamelog.send


class BaseDirectionButton(discord.ui.Button):
    def __init__(self, label: typing.Literal["left", "right", "up", "down"]):
        match label:
            case "left":
                emoji = "⬅️" # EMOJIS IN CODE WOOO
            case "right":
                emoji = "➡️"
            case "up":
                emoji = "⬆️"
            case "down":
                emoji = "⬇️"
            case _:
                raise TypeError("Must be left, right, up, or down!")
        super().__init__(style=discord.ButtonStyle.blurple, label=emoji, custom_id=label)

class MoveDirectionButton(BaseDirectionButton):
    def __init__(self, label: typing.Literal["left", "right", "up", "down"], target_pos: tuple[int, int]):
        super().__init__(label)
        self.move_name = label
        self.target_pos = target_pos
        
    async def callback(self, interaction: discord.Interaction):
        player = game.playerdata.data[str(interaction.user.id)]
        team = game.gamedata.data["teams"][player["team"]]
        chess = game.fielddata.to_chess(*self.target_pos)
        
        image = game.fieldimage.player_moved_to(player["position"], self.target_pos, team["colour"])
        with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='move.png')
            
        embed = discord.Embed(
            colour=team["colour"],
            title="Move",
            description=f"You moved {self.move_name} to **{chess}**!"
        )
        embed.set_image(url="attachment://move.png")
        embed.set_footer(text=f"This is move {player["moves"]} of {config.moves} you can do today.")
        embed.set_author(name=game.gamedata.game_title())
        
        player["position"] = self.target_pos
        
        await interaction.response.edit_message(view=None, embed=embed, attachments=[file])
        
        embed = discord.Embed(
            colour=team["colour"],
            description=f"{interaction.user.mention} of Team {team["name"]} moved {self.move_name} to {chess}",
        )
        embed.set_author(name=f"Player moved")
            
        await gamelog.send.log(interaction.client, embed=embed)

class MoveSelectView(discord.ui.View):
    def __init__(self, *, timeout = 180, positions: tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]):
        """Provide positions in the order left, right, up, down"""
        super().__init__(timeout=timeout)
        self.add_item(MoveDirectionButton('left', positions[0]))
        self.add_item(MoveDirectionButton('right', positions[1]))
        self.add_item(MoveDirectionButton('up', positions[2]))
        self.add_item(MoveDirectionButton('down', positions[3]))


@discord.app_commands.command(description="Perform your move for the day!")
@discord.app_commands.dm_only()
async def move(interaction: discord.Interaction):
    if not isinstance(interaction.channel, discord.channel.DMChannel):
        await interaction.response.send_message("You can only use this in a DM!")
    
    elif not str(interaction.user.id) in game.playerdata.data:
        await interaction.response.send_message("You didn't sign up to this game, so you cannot play!")
        
    elif not game.gamedata.is_active():
        await interaction.response.send_message("The game is not active!")
        
    elif not game.gamedata.turns_open():
        await interaction.response.send_message("Turns aren't open for today!")
        
    elif game.playerdata.data[str(interaction.user.id)]["moves"] >= config.moves:
        await interaction.response.send_message(f"You have already moved the maximum amount of times ({config.moves}) today!")
    
    elif game.playerdata.data[str(interaction.user.id)]["frozen"]:
        await interaction.response.send_message(f"You were frozen and cannot move today!")
        
    else:
        player = game.playerdata.data[str(interaction.user.id)]
        team = game.gamedata.data["teams"][player["team"]]
        spaces = random.randint(1, config.move_distance_max)
        
        player["moves"] += 1
        # a little elaboration.
        # we increment it now, else players could just use the command again for a reroll. blegh.
        
        # https://stackoverflow.com/a/63210850/15287613
        image = game.fieldimage.player_move_area(player["position"], spaces, team["colour"])
        with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename='move_preview.png')
        
        embed = discord.Embed(
            colour=team["colour"],
            title="Move",
            description=f":game_die: You rolled a **{spaces}**!\nYou're at **{game.fielddata.to_chess(*player["position"])}**!\nChoose a direction to move in!"
        )
        embed.set_image(url="attachment://move_preview.png")
        embed.set_footer(text=f"This is move {player["moves"]} of {config.moves} you can do today.\nIf you don't select within two minutes, you forfeit this move!")
        embed.set_author(name=game.gamedata.game_title())
        
        await interaction.response.send_message(
            embed=embed, file=file, view=MoveSelectView(positions=game.fielddata.move_points(player["position"], spaces)))
        
        # send a log
        embed = discord.Embed(
            colour=team["colour"],
            description=f"{interaction.user.mention} of Team {team["name"]} initialised a move!",
        )
        embed.set_author(name=f"Player initialised move")
            
        await gamelog.send.log(interaction.client, embed=embed)