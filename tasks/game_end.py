import io

import discord

import game.fielddata
import game.fieldimage
import game.gamedata
import game.playerdata
import gamelog.send

# NOT scheduled, just in its own file bc the code was getting too long

async def on_game_end(client: discord.Client):
    embed = discord.Embed(
        colour=0xFFFF5C,
        title="End of the game!",
        description="The final round has concluded! Thank you for playing."
    )
    embed.set_author(name=game.gamedata.game_title())
    await gamelog.send.announce(client, embed=embed)
    
    
    # calculate results
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
    
    image = game.fieldimage.overview(paint=True, grid=False, collision=False,
                                teams=list(range(len(game.gamedata.data["teams"]))))
    with io.BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename='final.png')
    embed.set_image(url="attachment://final.png")
    
    await gamelog.send.announce(client, embed=embed, file=file)
    
    # do mvp stats
    
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
    
    await gamelog.send.log(client, embed=discord.Embed(
                            colour=0xFFFF5C,
                            title="Game ends"
                        ))