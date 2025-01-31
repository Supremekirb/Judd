import asyncio
import logging

import discord

import config
import game.fielddata
import game.gamedata
import game.playerdata
from tasks.asyncutil import scheduled

_interval = config.save_interval*60

@scheduled()
async def auto_save(client: discord.Client):
    while True:
        await asyncio.sleep(_interval)
        
        game.fielddata.save()
        game.gamedata.save()
        game.playerdata.save()
        logging.info("Autosaved game data!")
        