import playlists
import discord
from discord.ext import commands
from os import environ
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from json import load
import random


client = commands.Bot(command_prefix='>')
client.remove_command('help')

BOT_TOKEN = environ.get('BOT_TOKEN')

@client.command()
async def help(ctx):
    embed=discord.Embed(title='Help', description='A short list of currently available commands:', color=0xb44141)
    embed.add_field(name=">source", value='Display the source code.', inline=True)
    embed.add_field(name=">clear [value]", value='Clear [value] text messages.', inline=True)
    embed.add_field(name=">play [url]", value='Play music from a YouTube video.', inline=True)
    embed.add_field(name=">playlist [list]", value='Roll a random track from [list].', inline=True)
    embed.add_field(name=">resume", value='Resume the music.', inline=True)
    embed.add_field(name=">pause", value='Pause the music.', inline=True)
    embed.add_field(name=">stop", value='Stop the music.', inline=True)
    await ctx.send(embed=embed)

@client.command()
async def source(ctx):
    source_code = 'https://github.com/anthonybartczak/elvenden-bot'
    embed=discord.Embed(title='Source code', description='You can check the source code here:\n' + source_code, color=0xb44141)
    await ctx.send(embed=embed)

@client.command()
async def clear(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"Deleted {len(deleted)} messages")

@client.command()
async def talent(ctx, talent_name: str):
    with open('talents.json') as jf:
        json_data = load(jf)
    if talent_name in json_data:
        talent = json_data[talent_name]
        await ctx.send('Talent name found!')
        embed=discord.Embed(title=talent['name'], description=talent['description'], color=0x007bff)
        embed.add_field(name="Maksimum", value=talent['max'], inline=True)
        embed.add_field(name="Testy", value=talent['tests'], inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send('Couldn\'t find the talent name.')


@client.command()
async def play(ctx, url: str):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice.is_playing()
        await ctx.send('Bot is playing')

    else:
        await ctx.send("Bot is already playing")
        return

@client.command()
async def playlist(ctx, choice: str):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    voice = get(client.voice_clients, guild=ctx.guild)

    if choice == 'town':
        chosen_list = playlists.TOWN_AMBIENCE
    elif choice == 'day':
        chosen_list = playlists.DAY_AMBIENCE
    elif choice == 'dark':
        chosen_list = playlists.DARK_AMBIENCE
    elif choice == 'fight':
        chosen_list = playlists.FIGHT_AMBIENCE
    elif choice == 'night':
        chosen_list = playlists.NIGHT_AMBIENCE
    elif choice == 'emotional':
        chosen_list = playlists.EMOTIONAL_AMBIENCE
    elif choice == 'random':
        chosen_list = playlists.RANDOM_MUSIC

    url = random.choice(chosen_list)

    if not voice.is_playing():
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['url']
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice.is_playing()
        title = 'Playing the ' + choice + ' playlist'
        vid_name = info.get('title', None)
        vid_id = info.get('id', None)
        vid_info = '**Current track name:** \n' + vid_name + '\n\n' + '**URL**:\nhttps://www.youtube.com/watch?v=' + vid_id
        embed=discord.Embed(title=title, description=vid_info, color=0xb44141)
        await ctx.send(embed=embed)
        
    else:
        await ctx.send("Bot is already playing")
        return


@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Bot is resuming')


@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Bot has been paused')


@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        await ctx.send('Stopping...')

client.run(BOT_TOKEN)