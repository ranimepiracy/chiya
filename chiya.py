import glob
import logging

import discord
from discord.ext import commands

import __init__
import config
import utils.database

bot = commands.Bot(
    command_prefix=config.PREFIX,
    intents=discord.Intents(messages=True, guilds=True, members=True, bans=True),
    case_insensitive=True)
log = logging.getLogger(__name__)

@bot.event
async def on_ready():
    """Called when the client is done preparing the data received from Discord.

    For more information:
    https://discordpy.readthedocs.io/en/stable/api.html#discord.on_ready
    """
    print(f"Logged in as: {bot.user.name}#{bot.user.discriminator}")
    print(f"discord.py version: {discord.__version__}")

    # Adding in a activity message when the bot begins.
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{config.PREFIX}help"
        )
    )

    # Attempt to create the db, tables, and columns for Chiya.
    utils.database.setup_db()

@bot.event
async def on_message(message: discord.Message):
    """This event listener has been moved to message_updates.py

    Unfortuneatley, this listener has to remain and do nothing, otherwise,
    any message will be ran twice and cause issues. Lame, i know
    """
    # Do nothing

if __name__ == '__main__':
    # Recursively loads in all the cogs in the folder named cogs.
    # Skips over any cogs that start with '__' or do not end with .py.
    for cog in glob.iglob("cogs/**/[!^_]*.py", recursive=True):
        if "\\" in cog:  # Fix pathing on Windows
            bot.load_extension(cog.replace("\\", ".")[:-3])
        else:  # Fix pathing on Linux:
            bot.load_extension(cog.replace("/", ".")[:-3])

    # Finally, run the bot.
    bot.run(config.BOT_TOKEN)
