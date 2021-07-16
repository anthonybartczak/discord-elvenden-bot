from typing import Text
import discord
from discord.ext import commands
from os import environ

bot = commands.Bot(command_prefix='>')

BOT_TOKEN = environ.get('BOT_TOKEN')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def clear(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"Deleted {len(deleted)} messages")

bot.run(BOT_TOKEN)