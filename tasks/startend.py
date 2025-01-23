import asyncio
import datetime
import logging

import discord

import config
import game.gamedata
import game.playerdata
import gamelog.send
from tasks.asyncutil import scheduled, wait_until

_retry_interval = config.retry_interval*60
_max_tries = config.max_retries

# these don't actually need a `while True:` as they will only occur once

@scheduled()
async def on_game_start(client: discord.Client):
    target = game.gamedata.start_datetime()

    if datetime.datetime.now(datetime.timezone.utc) > target:
        return logging.info("Running after game start")
    
    await wait_until(target)
    
    tries = 1
    while not client.is_ready():
        logging.warning(f"Client isn't available for game start! Waiting for {_retry_interval}s, then retrying... ({tries}/{_max_tries})")
        await asyncio.sleep(_retry_interval)
        tries += 1
        if tries > _max_tries:
            logging.warning(f"Client was not available for game start at {str(target)}!")
            break # maybe needs more than a warning? idk it's pretty bad if the game is not able to begin
        
    else:
        embed = discord.Embed(
            colour=0xFFFF5C,
            title="THE GAME BEGINS!",
            description=f"May the best team win!"
        )
        embed.set_author(name=game.gamedata.game_title())
        
        await gamelog.send.announce(embed=embed)
                
                
@scheduled()
async def on_game_end(client: discord.Client):
    target = game.gamedata.end_datetime()
    
    if datetime.datetime.now(datetime.timezone.utc) > target:
        return logging.info("Running after game end")

    await wait_until(target)
    
    tries = 1
    while not client.is_ready():
        logging.warning(f"Client isn't available for game end! Waiting for {_retry_interval}s, then retrying... ({tries}/{_max_tries})")
        await asyncio.sleep(_retry_interval)
        tries += 1
        if tries > _max_tries:
            logging.warning(f"Client was not available for game end at {str(target)}!")
            break # also pretty bad
        
    else:
        embed = discord.Embed(
            colour=0xFFFF5C,
            title="GAME!",
            description=f"Who has won...?"
        )
        embed.set_author(name=game.gamedata.game_title())
        
        await gamelog.send.announce(embed=embed)