import discord
import game.gamedata


async def announce(client: discord.Client, content: str = None, embed: discord.Embed = None):
    if "announcement_channel" in game.gamedata.data:
        channel = client.get_channel(game.gamedata.data["announcement_channel"])
        
        if not content and not embed:
            raise ValueError("Must have something to send!")
        
        await channel.send(content=content, embed=embed)


async def log(client: discord.Client, content: str = None, embed: discord.Embed = None):
    if "logs_channel" in game.gamedata.data:
        channel = client.get_channel(game.gamedata.data["logs_channel"])
        
        if not content and not embed:
            raise ValueError("Must have something to send!")
        
        await channel.send(content=content, embed=embed)

