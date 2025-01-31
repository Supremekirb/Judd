import discord

import game.fielddata
import game.gamedata
import game.playerdata
import gamelog.send

# NOT scheduled, just in its own file bc the code was getting too long

async def on_game_start(client: discord.Client):
    embed = discord.Embed(
    colour=0xFFFF5C,
    title="The game begins!",
    description=f"Check your DMs this time each day to have your turn! You can have today's turn for the next {game.gamedata.data["round_period"]}h!"
    )
    embed.set_author(name=game.gamedata.game_title())
    await gamelog.send.announce(client, embed=embed)
    
    
    # randomise player start positions
    for uid in game.playerdata.data:
        player = game.playerdata.data[uid]
        team = game.gamedata.data["teams"][player["team"]]                        
        player["position"] = game.fielddata.random_open_space(*team["start_range"])

    await gamelog.send.log(client, embed=discord.Embed(
        colour=0xFFFF5C,
        title="Game begins"
    ))