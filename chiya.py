import asyncio
import glob
import logging

import discord
from discord.ext import commands

import background
import config
import embeds
from utils import contains_link, has_attachment

cogs = ["cogs.settings"]
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='?', intents=intents)


@bot.event
async def on_ready():
    print(f"\n\nLogged in as: {bot.user.name} - {bot.user.id}\nDiscord.py Version: {discord.__version__}\n")
    print(f"Successfully logged in and booted...!")

    # Recursively going though cogs folder and loading them in.
    print("Loading Cogs:")
    for cog in glob.iglob("cogs/**/[!^_]*.py", recursive=True): # filtered to only load .py files that do not start with '__'
        print("  -> " + cog.rsplit('\\', 1)[-1][:-3])
        bot.load_extension(cog.replace("\\", ".")[:-3])
    print("Done Loading Cogs:")


async def on_member_join(self, member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = 'Welcome {0.mention} to {1.name}!'.format(member, guild)
        await guild.system_channel.send(to_send)

@bot.event
async def on_message(ctx):
    # Remove messages that don't contain links or files from our submissions only channels
    if ctx.channel.id in config.SUBMISSION_CHANNEL_IDs and not (contains_link(ctx) or has_attachment(ctx)):
        # Ignore messages from self or bots to avoid loops and other oddities
        if ctx.author.id == bot.user.id or ctx.author.bot is True:
            return

        # Deletes message and send self-destructing warning embed
        await ctx.delete()
        warning = await ctx.channel.send(embed=embeds.files_and_links_only(ctx))
        await asyncio.sleep(10)
        await warning.delete()

    # If message does not follow with the above code, treat it as a potential command.
    await bot.process_commands(ctx)   

if __name__ == '__main__':
    bot.loop.create_task(background.check_for_posts(bot))
    bot.run(config.BOT_TOKEN)
