import asyncio
import datetime
import logging

import discord

import config
import game.gamedata
import game.playerdata
from tasks.asyncutil import scheduled, wait_until

_retry_interval = 10*60 # 10 mins
_max_tries = 12 # 2 hours

@scheduled()
async def on_round_start(client: discord.Client):
    while True:
        utcnow = datetime.datetime.now(datetime.timezone.utc)
        utcmidnight = utcnow.replace(hour=0, minute=0, second=0, microsecond=0)
        
        offset = game.gamedata.data["offset"]
        target = utcmidnight + datetime.timedelta(hours=offset)
        
        # TODO this WORKS but it's not exactly pretty
        while target < utcnow:
            target += datetime.timedelta(days=1)
        
        await wait_until(target)
        
        tries = 1
        while not client.is_ready():
            logging.warning(f"Client isn't available for round start! Waiting for {_retry_interval}s, then retrying... ({tries}/{_max_tries})")
            await asyncio.sleep(_retry_interval)
            tries += 1
            if tries > _max_tries:
                logging.warning(f"Client was not available for round start at {str(target)}!")
                break

        else: # stuff that should occur 
            if game.gamedata.is_active():
                title = game.gamedata.game_title()
                
                if "announcement_channel" in game.gamedata.data:
                    channel = client.get_channel(game.gamedata.data["announcement_channel"])
                    embed = discord.Embed(
                        colour=0x5CFF5C,
                        title="Turns are open for today!",
                        description=f"You can have your turn for the next {game.gamedata.data["round_period"]}h! Check your DMs!"
                    )
                    embed.set_author(name=title)
                    
                    await channel.send(embed=embed)
                
                for uid in game.playerdata.data:
                    player = game.playerdata.data[uid]
                    team = game.gamedata.data["teams"][player["team"]]
                    user = await client.fetch_user(uid)
                    
                    if "frozen" in player and player["frozen"]: # god I LOVE python
                        embed = discord.Embed(color = 0x44EEEE,
                                          title = f"Team {team["name"]}",
                                          description = f"You were {config.frozen_name} yesterday! You've lost your turn for this day.")
                    else:
                        embed = discord.Embed(color = team["colour"],
                                            title = f"Turns are open!",
                                            description = f"Time for a turn! You can use `/move` (x{config.moves})  and `/throw` (x{config.throws}) today.")

                    embed.set_author(name=title)
                    
                    await user.send(embed=embed)
                
                await asyncio.sleep(120) # sleep for a minute plus another minute for safety (otherwise may spam)


@scheduled()
async def on_round_end(client: discord.Client):
    while True:
        utcnow = datetime.datetime.now(datetime.timezone.utc)
        utcmidnight = utcnow.replace(hour=0, minute=0, second=0, microsecond=0)
        
        offset = game.gamedata.data["offset"]
        target = utcmidnight + datetime.timedelta(hours=offset)
        
        period = game.gamedata.data["round_period"]
        target += datetime.timedelta(hours=period)
        
        while target < utcnow:
            target += datetime.timedelta(days=1)
        
        await wait_until(target)

        
        tries = 1
        while not client.is_ready():
            logging.warning(f"Client isn't available for round end! Waiting for {_retry_interval}s, then retrying... ({tries}/{_max_tries})")
            await asyncio.sleep(_retry_interval)
            tries += 1
            if tries > _max_tries:
                logging.warning(f"Client was not available for round end at {str(target)}!")
                break

        else: # stuff that should occur
            if game.gamedata.is_active():
                if "announcement_channel" in game.gamedata.data:
                    channel = client.get_channel(game.gamedata.data["announcement_channel"])
                    embed = discord.Embed(
                        colour=0xFF5C5C,
                        title="Turns are closed for today!",
                        description=f"See you tomorrow!"
                    )
                    embed.set_author(name=game.gamedata.game_title())
                    
                    await channel.send(embed=embed)