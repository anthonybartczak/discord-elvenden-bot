import playlists
import discord
from discord.ext import commands
from os import environ
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from json import load
import random


client = commands.Bot(command_prefix='.')
client.remove_command('help')

def displayEmbedVideoInfo(name, id, thumbnail):
    vid_info = '**Current track name:** \n' + name + '\n\n' + '**URL**:\nhttps://www.youtube.com/watch?v=' + id
    embed=discord.Embed(title='Playing', description=vid_info, color=0xb44141)
    embed.set_image(url=thumbnail)
    return embed

BOT_TOKEN = environ.get('BOT_TOKEN')

@client.event
async def on_ready():
    activity = discord.Game(name=".help")
    await client.change_presence(status=discord.Status.online, activity=activity)

@client.command()
async def help(ctx):
    calc_help = \
         'Poniżej krótka instrukcja dotycząca użytkowania polecenia **advance**:\n\n'\
         'Format polecenia: \n\n'\
         '**>advance** [c lub u] [wartość_początkowa] [wartość_docelowa] [talent*]\n\n\n'\
         'c lub u ->  wybór pomiędzy rozwojem cechy lub umiejętności\n\n'\
         'wartość_początkowa ->  początkowa wartość umiejętności lub cechy\n\n'\
         'wartość_docelowa ->  docelowa wartość umiejętności lub cechy\n\n'\
         'talent (opcjonalne) ->  jeśli któryś z talentów postaci obniża koszt rozwoju o 5 PD\n\n'\
         'Przykłady:\n\n>advance c 5 12\n\n>advance u 12 16 t'

    embed=discord.Embed(title='Help', description='A short list of currently available commands:', color=0xb44141)
    embed.add_field(name=".advance [c/u] [x] [y] [t*]", value='Oblicz koszt rozwoju [od x do y] cechy [c] lub umiejętności [u]. Np.\n.advance c 12 15\n.advance u 5 14 t\n\nArgument t obniża koszt o 5 PD.', inline=False)
    embed.add_field(name=".clear [value]", value='Wyczyść x wiadomości.', inline=False)
    embed.add_field(name=".play [URL]", value='Odtwórz muzkę z YouTube (URL).', inline=False)
    embed.add_field(name=".pause / .stop / .resume", value='Zapauzuj/zatrzymaj/wznów muzykę.', inline=False)

    await ctx.send(embed=embed)

@client.command()
async def source(ctx):
    source_code = 'https://github.com/anthonybartczak/elvenden-bot'
    embed=discord.Embed(title='Source code', description='You can check the source code here:\n' + source_code, color=0xb44141)
    await ctx.send(embed=embed)
    
@client.command()
async def reaction(ctx):
    zus = {
        'https://i.imgur.com/lxBQV76.png':'shocked!',
        'https://i.imgur.com/RBTMA0J.jpg':'not amused!',
        'https://i.imgur.com/s8L0leY.png':'bored!',
        'https://i.imgur.com/rbBa0p8.png':'hungry!',
        'https://i.imgur.com/w7B3BwT.png':'thirsty!'
    }
    zus_choice = random.choice(list(zus.items()))
    embed=discord.Embed(title='Zus reaction table', description='Zus is ' + zus_choice[1], color=0xb44141)
    embed.set_image(url=zus_choice[0])
    await ctx.send(embed=embed)

@client.command()
async def tracks(ctx):
    embed=discord.Embed(title='Tracks', description='Work in progress.', color=0xb44141)
    await ctx.send(embed=embed)

@client.command()
async def clear(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"Deleted {len(deleted)} messages")

@client.command()
async def advance(ctx, type: str, init: int, goal: int, talent: str=None):

    # if not help:
    image = 'https://cdn.discordapp.com/attachments/868802153014263851/870615749083926638/WHFRP_4ED_Rozwoj_cech_um.png'

    ability_map = {5:10, 10:15, 15:20, 20:30, 25:40, 30:60, 35:80, 40:110, 45:140, 50:180}
    attribute_map = {5:25, 10:30, 15:40, 20:50, 25:70, 30:90, 35:120, 40:150, 45:190, 50:230}

    if type == 'c':
        chosen_map = attribute_map
        choice = 'cechy'
    elif type == 'u':
        chosen_map = ability_map
        choice = 'umiejętności'

    current = init
    cost_sum = 0

    dif = goal - init
    for key, value in chosen_map.items():
        while current < key and dif != 0:
            cost_sum += value
            current += 1
            dif -= 1

    description = \
        'Twoja początkowa wartość **' + choice + '** to: **' + str(init) + '**\n'\
        'Twoja docelowa wartość **' + choice + '** to: **' + str(goal) + '**\n\n'
    if talent == 't':
        description += 'Jeden z Twoich talentów obniża koszt o **5 PD** za każde rozwinięcie.\n\n'\
        'Finalny koszt rozwinięcia to: **' + str(cost_sum - 5 * (goal - init)) + ' PD**'
    else:
        description += 'Koszt rozwinięcia to: **' + str(cost_sum) + ' PD**'

    embed=discord.Embed(title='Rozwinięcie ' + choice, description=description, color=0x007bff)
    embed.set_image(url=image)

    # else:
    #     description = \
    #     'Poniżej krótka instrukcja dotycząca użytkowania polecenia **advance**:\n\n'\
    #     'Format polecenia: \n\n'\
    #     '**>advance** [c lub u] [wartość_początkowa] [wartość_docelowa] [talent*]\n\n\n'\
    #     'c lub u ->  wybór pomiędzy rozwojem cechy lub umiejętności\n\n'\
    #     'wartość_początkowa ->  początkowa wartość umiejętności lub cechy\n\n'\
    #     'wartość_docelowa ->  docelowa wartość umiejętności lub cechy\n\n'\
    #     'talent (opcjonalne) ->  jeśli któryś z talentów postaci obniża koszt rozwoju o 5 PD\n\n'\
    #     'Przykłady:\n\n>advance c 5 12\n\n>advance u 12 16 t'
    #     embed=discord.Embed(title='Advance: instrukcja ', description=description, color=0x007bff)

    await ctx.send(embed=embed)
    
    
@client.command()
async def talent(ctx, *, talent_name: str):
    
    talent_name = talent_name.replace(' ','_').lower()
    
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
    await ctx.channel.purge(limit=1)
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
        vid_name = info.get('title', None)
        vid_id = info.get('id', None)
        vid_thumbnail = info.get('thumbnail', None)
        embed = displayEmbedVideoInfo(vid_name, vid_id, vid_thumbnail)
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