import asyncio
import datetime
import logging

import discord

import config
import game.fielddata
import game.gamedata
import game.playerdata
import gamelog.send
from tasks.asyncutil import scheduled, wait_until

_retry_interval = config.retry_interval*60
_max_tries = config.max_retries

@scheduled()
async def on_round_start(client: discord.Client):
    while True:
        utcnow = datetime.datetime.now(datetime.timezone.utc)
        utcmidnight = utcnow.replace(hour=0, minute=0, second=0, microsecond=0)
        
        offset = game.gamedata.data["offset"]
        target = utcmidnight + datetime.timedelta(hours=offset)
        
        isFirst = target == game.gamedata.start_datetime()
        
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
                
                if isFirst:
                    embed = discord.Embed(
                    colour=0xFFFF5C,
                    title="The game begins!",
                    description=f"Check your DMs this time each day to have your turn! You can have today's turn for the next {game.gamedata.data["round_period"]}h!"
                    )
                
                    await gamelog.send.log(client, embed=discord.Embed(
                        colour=0xFFFF5C,
                        title="Game begins"
                    ))
                
                else:
                    embed = discord.Embed(
                        colour=0x5CFF5C,
                        title="Turns are open for today!",
                        description=f"You can have your turn for the next {game.gamedata.data["round_period"]}h! Check your DMs!"
                    )
                
                embed.set_author(name=title)
                
                await gamelog.send.announce(client, embed=embed)
                
                await gamelog.send.log(client, embed=discord.Embed(
                        colour=0x5CFF5C,
                        title="Turns open"
                    ))
                
                for uid in game.playerdata.data:
                    player = game.playerdata.data[uid]
                    team = game.gamedata.data["teams"][player["team"]]
                    user = await client.fetch_user(uid)
                    
                    player["moves"] = 0
                    player["throws"] = 0
                    
                    player["frozen"] -= 1
                    
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
        
        isLast = target == game.gamedata.end_datetime()
        
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
            
            # so we can keep track of hits without needless iteration
            players_by_throw_target: dict[tuple[int, int], str] = {}  # pos -> uid
            players_frozen_today: dict[str, bool] = {} # uid -> boolean if it was from a player 
            
            # apply queue
            for player in game.playerdata.data.values():
                for action in player["queued_actions"]:
                    x, y = action["target"]
                    match action["name"]:
                        case "throw":
                            player["total_throws"] += 1
                            if game.fielddata.data["field"][x][y] != -1:
                                game.fielddata.data["field"][x][y] = player["team"]
                                player["total_turfed"] += 1
                                players_by_throw_target.setdefault((x, y), [])
                                players_by_throw_target[(x, y)].append(player["id"])
                                        
                        case _:
                            logging.warning(f"Unknown action type: {action["name"]}")
                player["queued_actions"] = []
                
            # see who is frozen based on turf 
            for player in game.playerdata.data.values():
                x, y = player["position"]
                if game.fielddata.data["field"][x][y] not in (player["team"], None) and not player["frozen"]:
                    # set to 2. Next day it is subtracted (= 1), so turn is missed, then day after it is set to 0, so unfrozen.
                    # also, making sure the player isn't frozen already makes sure they have a chance to escape next day
                    player["frozen"] = 2
                    
                    players_frozen_today[str(player["id"])] = False
                    for id in players_by_throw_target.get((x, y), []):
                        attacker = game.playerdata.data[str(id)]
                        if attacker["team"] != player["team"]:
                            attacker["total_hits"] += 1
                            players_frozen_today[str(player["id"])] = True
            
            if game.gamedata.is_active() or isLast:
                await gamelog.send.log(client, embed=discord.Embed(
                        colour=0xFF5C5C,
                        title="Turns close"
                    ))
                
                if isLast:
                    embed = discord.Embed(
                        colour=0xFFFF5C,
                        title="End of game!",
                        description="The final round has concluded! Thank you for playing."
                    )
                
                else:
                    embed = discord.Embed(
                        colour=0xFF5C5C,
                        title="Turns are closed for today!",
                        description=f"See you tomorrow!"
                    )
                    
                embed.set_author(name=game.gamedata.game_title())
                
                await gamelog.send.announce(client, embed=embed)
                
                if isLast:
                    await gamelog.send.log(client, embed=discord.Embed(
                            colour=0xFFFF5C,
                            title="Game ends"
                        ))