import logging

import discord

import commands
import config
import tasks


class Client(discord.Client):
    def __init__(self, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        
    async def setup_hook(self):
        tasks.register_with_loop(self)
        commands.register_with_tree(self.tree)
        
        for i in config.debug_guild_sync_ids:
            self.tree.clear_commands(guild=discord.Object(id=i))
            await self.tree.sync(guild=discord.Object(id=i))
        
        await self.tree.sync()        


if __name__ == "__main__":
    intents = discord.Intents.default()
    # intents.message_content = True
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