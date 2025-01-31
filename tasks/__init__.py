import importlib
import inspect
import os
import asyncio

import discord

tasks: set[asyncio.Task] = set()

def register_with_loop(client: discord.Client):
    for module in os.listdir(os.path.dirname(__file__)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        imported = importlib.import_module(f"{__name__}.{module[:-3]}")
        for _, member in inspect.getmembers(imported):
            if hasattr(member, "_judd_scheduled"): # kinda janky - see asyncutil.py for the meaning of this
                # TODO better way to check if it's wrapped by a specific thing
                task = client.loop.create_task(member(client))
                tasks.add(task)
                task.add_done_callback(tasks.discard) # do not keep unnecessary references
