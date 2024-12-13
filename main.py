# This example requires the 'message_content' intent.

import logging

import discord
import discord.ext.commands

import commands
import game.fielddata as fielddata
import game.gamedata as gamedata
import game.playerdata as playerdata


class Client(discord.Client):
    def __init__(self, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        
    async def setup_hook(self):
        commands.register_with_tree(self.tree)
        self.tree.copy_global_to(guild=discord.Object(id=1235354470951686265))
        await self.tree.sync(guild=discord.Object(id=1235354470951686265))
        


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.typing = False
    intents.presences = False

    client = Client(intents)

    @client.event
    async def on_ready():
        print(f'Logged in as {client.user}')            

    try:
        with open("token.txt") as file:
            token = file.read()
    except FileNotFoundError as e:
        raise FileNotFoundError("Please place the bot token in token.txt!") from e
    
    handler = logging.FileHandler(filename="discord.log", encoding='utf-8', mode='w')
    
    client.run(token, log_handler = handler)