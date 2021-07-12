import discord
from discord.ext import commands
from os import environ

bot = commands.Bot(command_prefix='>')

BOT_TOKEN = environ.get('BOT_TOKEN')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

bot.run(BOT_TOKEN)