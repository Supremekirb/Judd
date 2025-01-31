import asyncio
import datetime
import io
import logging

import discord

import config
import game.fielddata
import game.fieldimage
import game.gamedata
import game.playerdata
import gamelog.send
from game import fieldimage
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
                    # this one is actually sent later
                    
                    
                    # randomise player start positions
                    for uid in game.playerdata.data:
                        player = game.playerdata.data[uid]
                        team = game.gamedata.data["teams"][player["team"]]                        
                        player["position"] = game.fielddata.random_open_space(*team["start_range"])
                
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
                    if player["frozen"] < 0: player["frozen"] = 0
                    
                    if "frozen" in player and player["frozen"]: # god I LOVE python
                        embed = discord.Embed(color = 0x44EEEE,
                                          title = f"Team {team["name"]}",
                                          description = f"You were {config.frozen_name} yesterday! You've lost your turn for this day.")
                    else:
                        embed = discord.Embed(color = team["colour"],
                                            title = f"Turns are open!",
                                            description = f"Time for a turn! You're at {game.fielddata.to_chess(*player["position"])}. You can use `/move` (x{config.moves})  and `/throw` (x{config.throws}) today.")

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
        
        #### DEBUG ####
        # target = utcnow + datetime.timedelta(seconds=15)
        # isLast = True
        # print(target)
        # print(utcnow)
        ###############
        
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
            for uid in game.playerdata.data:
                player = game.playerdata.data[uid]
                for action in player["queued_actions"]:
                    x, y = action["target"]
                    match action["name"]:
                        case "throw":
                            player["total_throws"] += 1
                            if game.fielddata.data["field"][x][y] != -1:
                                if game.fielddata.data["field"][x][y] != player["team"]:
                                    player["total_turfed"] += 1
                                game.fielddata.data["field"][x][y] = player["team"]
                                players_by_throw_target.setdefault((x, y), [])
                                players_by_throw_target[(x, y)].append(str(uid))
                                        
                        case _:
                            logging.warning(f"Unknown action type: {action["name"]}")
                player["queued_actions"] = []
                
            # see who is frozen based on turf 
            for uid in game.playerdata.data:
                player = game.playerdata.data[uid]
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
                            
            # update the paint overlay
            # VERY IMPORTANT
            game.fieldimage.update_paint_overlay()
            
            # DEBUG #
            # if True:
            #########
            
            if game.gamedata.is_active() or isLast:
                await gamelog.send.log(client, embed=discord.Embed(
                        colour=0xFF5C5C,
                        title="Turns close"
                    ))
                
                if isLast:
                    embed = discord.Embed(
                        colour=0xFFFF5C,
                        title="End of the game!",
                        description="The final round has concluded! Thank you for playing."
                    )
                    embed.set_author(name=game.gamedata.game_title())
                    await gamelog.send.announce(client, embed=embed)
                    
                    
                    embed = discord.Embed()
                    embed.set_author(name="Final results")
                    
                    scores = game.fielddata.turf_scores()
                    sorted_team_scores = []
                    for t, score in scores.items():
                        team = game.gamedata.data["teams"][t]                        
                        sorted_team_scores.append({"team": team, "score": score})
                    
                    sorted_team_scores.sort(key=lambda x: x["score"]["points"], reverse=True)
                            
                    embed.title = f"**Team {sorted_team_scores[0]["team"]["name"]} wins!**"
                    embed.description = f"{sorted_team_scores[0]["score"]["percentage"]}% of the map claimed!"
                    embed.colour = sorted_team_scores[0]["team"]["colour"]
                    
                    scores_str = ""
                    for place, team_score in enumerate(sorted_team_scores):
                        scores_str += f"{place+1}. Team {team_score["team"]["name"]} - {team_score["score"]["points"]}p ({team_score["score"]["percentage"]}%)\n"
                    
                    embed.add_field(name="Scores", value=scores_str)
                    
                    image = fieldimage.overview(paint=True, grid=False, collision=False,
                                              teams=list(range(len(game.gamedata.data["teams"]))))
                    with io.BytesIO() as image_binary:
                        image.save(image_binary, 'PNG')
                        image_binary.seek(0)
                        file = discord.File(fp=image_binary, filename='final.png')
                    embed.set_image(url="attachment://final.png")
                    
                    await gamelog.send.announce(client, embed=embed, file=file)
                    
                    embed = discord.Embed()
                    embed.set_author(name="Best players")
                    
                    mvps = game.playerdata.mvps()
                    
                    turf_str = ""
                    hits_str = ""
                    hit_ratio_str = ""
                    for i in range(0, 3): # only the top three in each category
                        try:
                            turf = mvps["turf"][i]
                            hits = mvps["hits"][i]
                            hit_ratio = mvps["hit_ratio"][i]
                            turf_str += f"{i+1}. {(await client.fetch_user(int(turf["player"]))).mention} - {turf["stats"]["total_turfed"]}p\n"
                            hits_str += f"{i+1}. {(await client.fetch_user(int(hits["player"]))).mention} - {hits["stats"]["total_hits"]} hits\n"
                            try:
                                hit_ratio_str += f"{i+1}. {(await client.fetch_user(int(hit_ratio["player"]))).mention} - {round((hit_ratio["stats"]["total_throws"]/hit_ratio["stats"]["total_hits"])*100, 2)}%\n"
                            except ZeroDivisionError: # some of the top three had no hits
                                # hit_ratio_str += f"{i+1}. {(await client.fetch_user(int(hit_ratio["player"]))).mention} - 0%\n"
                                pass # after consideration, I think it's easier to just skip them, since the sorting doesn't imply any actual info here
                        except IndexError: # less than three players
                            pass
                    
                    embed.add_field(name="Best turfers", value=turf_str, inline=True)
                    embed.add_field(name="Best attackers", value=hits_str, inline=True)
                    embed.add_field(name="Best hit accuracy", value=hit_ratio_str, inline=True)
                    
                    await gamelog.send.announce(client, embed=embed)
                        
                else:
                    embed = discord.Embed(
                        colour=0xFF5C5C,
                        title="This day's turns have ended!",
                    )
                    
                    frozen_msg = ""
                    uids_frozen = players_frozen_today.keys()
                    if uids_frozen:
                        for frozen in uids_frozen:
                            frozen_msg += f"{await client.fetch_user(int(frozen)).mention}\n"
                    else:
                        frozen_msg = "Nobody"
                        
                    
                    embed.add_field(name="**Players frozen today**", value=frozen_msg)
                    
                    image = fieldimage.overview(paint=True, grid=False, collision=False,
                                              teams=list(range(len(game.gamedata.data["teams"]))), only_frozen=True)
    
                    with io.BytesIO() as image_binary:
                        image.save(image_binary, 'PNG')
                        image_binary.seek(0)
                        file = discord.File(fp=image_binary, filename='map.png')
                    embed.set_image(url="attachment://map.png")
                    
                    
                    embed.set_author(name=game.gamedata.game_title())
                    await gamelog.send.announce(client, embed=embed, file=file)               
                
                
                if isLast:
                    await gamelog.send.log(client, embed=discord.Embed(
                            colour=0xFFFF5C,
                            title="Game ends"
                        ))
                    
                await asyncio.sleep(120) # sleep for a minute plus another minute for safety (otherwise may spam)