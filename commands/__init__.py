import importlib
import os
from inspect import getmembers

import discord


def register_with_tree(tree: discord.app_commands.CommandTree):
    for module in os.listdir(os.path.dirname(__file__)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        imported = importlib.import_module(f"{__name__}.{module[:-3]}")
        for _, member in getmembers(imported):
            if isinstance(member, discord.app_commands.commands.Command):
                tree.add_command(member)