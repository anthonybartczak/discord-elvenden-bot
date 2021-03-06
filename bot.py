import asyncio
import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from json import load
import random
import content.tables as tab
import content.pictures as pic
from os import environ
from youtube_dl import YoutubeDL
from cogs.music import Music

# Main colors used for the bot's embeded messages formating.
MAIN_COLOR = 0x8b54cf
ERROR_COLOR = 0xff0000
SUCCESS_COLOR = 0x16bd00

# Bot token imported from Heroku env.
BOT_TOKEN = environ.get('BOT_TOKEN')

# Footer text (version + update date) for every single command.
FOOTER_TEXT = 'Elvie v0.90 - WFRP 4ED\nOstatnia aktualizacja: 9/19/2021'


# Discord intents declarations -> can be modified at https://discord.com/developers/
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(intents=intents, command_prefix='.')
client.remove_command('help')


@client.event
async def on_ready():
    activity = discord.Game(name=".help")
    await client.change_presence(status=discord.Status.online, activity=activity)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed=discord.Embed(title='⚠️Błąd polecenia⚠️', description='Nie znalazłem polecenia o tej nazwie. Może polecenie **.help** odpowie na Twoje pytanie?', color=ERROR_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed=discord.Embed(title='⚠️Brakujący argument⚠️', description='We wpisanym poleceniu brakuje jednego z argumentów. Sprawdź **.help** w celu weryfikacji składni polecenia.', color=ERROR_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        await ctx.send(embed=embed)
    raise error


@client.command()
async def servers(ctx):
    servers = list(client.guilds)
    description = 'Połączony z **' + str(len(servers)) + '** serwerami\n\n'
    for i, server in enumerate(servers, start=1):
        description += '**' + str(i) + '.** ' + server.name + '\n'
    embed=discord.Embed(title='Lista serwerów', description=description, color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.send(embed=embed)

@client.command()
async def help(ctx):
    description = \
        'Poniżej znajdziesz listę obecnie dostępnych poleceń. Argumenty oznaczone `*` są opcjonalne:\n\n'\
        '**.advance <c/u> <start> <cel> <t*>**\nOblicz koszt rozwoju od `start` do `cel` cechy lub umiejętności (`c` lub `u`). Argument `t` obniża koszt rozwinięcia o 5 PD. Przykładowo:\n`.advance c 12 15` albo `.advance u 5 14 t`\n\n'\
        '**.advance_table <m*>**\nWyświetl tabelę *Koszt rozwoju cech i umiejętności w PD*. Argument `m` wyświetla tabelę w wersji na urządzenia mobilne. Przykładowo:\n`.advance_table` albo `.advance_table m`\n\n'\
        '**.talent <nazwa>**\nWyświetl opis talentu `nazwa`. Nazwa musi zostać podana z uwzględnieniem polskich znaków oraz bez użycia nawiasów. Przykładowo:\n`.talent bardzo szybki` albo `.talent magia tajemna`\n\n'\
        '**.ability <nazwa>**\nWyświetl opis umiejętności `nazwa`. Nazwa musi zostać podana z uwzględnieniem polskich znaków oraz bez użycia nawiasów. Przykładowo:\n`.ability rzemiosło` albo `.ability mocna głowa`\n\nPodziękowania dla Kazyleusz#2024.\n\n'\
        '**.miscast <w*>**\nWylosuj mniejszą lub większą (parametr `w`) manifestację. Przykładowo:\n`.miscast` albo `.miscast w`\n\n'\
        '**.corruption <p*>**\nWylosuj spaczenie fizyczne lub zepsucie psychiczne (parametr `p`). Przykładowo:\n`.corruption` albo `.corruption p`\n\n'\
        '**.music** \nWyświetl instrukcję dotyczącą odtwarzania muzyki z portalu YouTube\n\n'\
        '**.fortune**\nWylosuj 4 karty, wybierz jedną i sprawdź czy `Ranald` wysłucha Twej modlitwy.\n\n'\
        '**.clear <wartość>**\nWyczyść `wartość` wiadomości. Może się przydać w trzymaniu porządku na kanale z rzutami. Użycie polecenia wymaga uprawnień administratora.\n\n'\
        '**.contact <wiadomość>**\nWyślij `wiadomość` bezpośrednio do autora bota. Wszelkie wykryte błędy, zażalenia i pytania są mile widziane.\n\n'\
        '**.invite**\nWygeneruj `URL`, dzięki któremu będziesz mógł zaprosić Elviego na własny serwer.\n\n'\
    
    embed=discord.Embed(title='Krótka instrukcja bota Elvie', description=description, color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.send(embed=embed)
    
@client.command()
async def music(ctx):
    description = \
        'Poniżej znajdziesz listę obecnie dostępnych poleceń związanych z odtwarzaniem muzyki:\n\n'\
        '**.play <URL/fraza>**\nOdtwórz utwór z platformy YouTube. Możesz wpisać URL lub wyszukać daną frazę. Przykładowo:\n`.play <adres_url>` albo `.play the city must survive`\n\nAlternatywne nazwy:\n`.p` `.sing`\n\n'\
        '**.pause**\nZapauzuj utwór bez czyszczenia kolejki. Bot pozostanie na kanale.\n\n'\
        '**.stop**\nZatrzymaj utwór i wyczyść kolejkę. Bot odłączy się z kanału.\n\n'\
        '**.skip**\nPomiń aktualny utwór. Może nastąpić mała przerwa między utworami.\n\n'\
        '**.volume <w>**\nZmień głośność odtwarzanego utworu na `w` procent. Przykładowo:\n`.volume 20` albo `.volume 80`\n\nAlternatywne nazwy:\n`.vol`\n\n'\
        '**.now_playing**\nWyświetl informacje o aktualnie odtwarzanym utworze.\n\nAlternatywne nazwy:\n`.np` `.current` `.currentsong` `.playing`\n\n'\
        '**.queue**\nWyświetl zakolejkowane utwory. Kolejka nie uwzględnia aktualnie odtwarzanego utworu.\n\nAlternatywne nazwy:\n`.q`, `.playlist`\n\n'\
    
    embed=discord.Embed(title='Krótka instrukcja muzycznego modułu bota Elvie', description=description, color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    
    await ctx.send(embed=embed)
    
@client.command()
async def reaction(ctx):
    zus = {
        pic.ZUS_PIC_NOT_AMUSED:'shocked!',
        pic.ZUS_PIC_BORED:'bored!',
        pic.ZUS_PIC_HUNGRY:'hungry!',
        pic.ZUS_PIC_THIRSTY:'thirsty!',
        pic.ZUS_PIC_FANCY:'feeling fancy!'}
    zus_choice = random.choice(list(zus.items()))
    embed=discord.Embed(title='Zus reaction table', description='Zus is ' + zus_choice[1], color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    embed.set_image(url=zus_choice[0])
    await ctx.send(embed=embed)

@client.command()
async def tracks(ctx):
    embed=discord.Embed(title='Tracks', description='Work in progress.', color=MAIN_COLOR)
    await ctx.send(embed=embed)

@client.command()
async def clear(ctx, amount: int):
    if ctx.author.guild_permissions.administrator:
        deleted = await ctx.channel.purge(limit=amount)
        embed=discord.Embed(title='Usunięto wiadomości', description='Usunięto **' + str(len(deleted)) + '** wiadomości.', color=MAIN_COLOR)
    else:
        embed=discord.Embed(title='⚠️Błąd uprawnień⚠️', description='Nie jesteś administratorem.', color=ERROR_COLOR)

    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.send(embed=embed)
    
@client.command()
async def invite(ctx):
    embed=discord.Embed(title='Link do zaproszenia', description='https://discord.com/oauth2/authorize?client_id=864205486056669244&permissions=8&scope=bot', color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.send(embed=embed)

@client.command()
async def advance(ctx, type: str, init: int, goal: int, talent: str=None):

    ability_map = {5:10, 10:15, 15:20, 20:30, 25:40, 30:60, 35:80, 40:110, 45:140, 50:180, 55:220, 60:270, 65:320, 70:380, 9999:440}
    attribute_map = {5:25, 10:30, 15:40, 20:50, 25:70, 30:90, 35:120, 40:150, 45:190, 50:230, 55:280, 60:330, 65:390, 70:450, 9999:520}

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

    embed=discord.Embed(title='Rozwinięcie ' + choice, description=description, color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    
    await ctx.send(embed=embed)

@client.command()
async def miscast(ctx, type: str='m'):
    roll = random.randint(1,100)
    
    if type == 'w':
        table = tab.MISCAST_MAJOR
        name = 'Większa'
    else:
        table = tab.MISCAST_MINOR
        name = 'Mniejsza'
    
    for i, r in enumerate(range(5, 101, 5)):
        if roll <= r:
            miscast = table[i]
            break
            
    embed=discord.Embed(title=name + ' manifestacja!', description='Wyrzuciłeś **' + str(roll) + '**...\n\n' + miscast, color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.send(embed=embed)
            
@client.command()
async def corruption(ctx, type: str='f'):
    roll = random.randint(1,100)
    
    if type == 'p':
        table = tab.CORRUPTION_MENTAL
        name = 'zepsucie psychiczne!'
    else:
        table = tab.CORRUPTION_PHYSICAL
        name = 'spaczenie fizyczne!'
    
    for i, r in enumerate(range(5, 101, 5)):
        if roll <= r:
            corruption = table[i]
            break
            
    embed=discord.Embed(title='Wylosowano ' + name, description='Wyrzuciłeś **' + str(roll) + '**...\n\n' + corruption, color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.send(embed=embed)

@client.command()
async def fortune(ctx):
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
    author = ctx.message.author
    winner = random.choice(reactions)
    index = reactions.index(winner)
    win_card = pic.WIN_CARDS[index]

    embed=discord.Embed(title='Punkt szczęścia użyty!', description='Czyli Twoja dobra passa się skończyła i nagle chcesz, by sam **Ranald** Ci dopomógł?\n\nDobrze, wybierz kartę śmiertelniku...\n\n', color=MAIN_COLOR)
    embed.set_image(url=pic.CARD_REVERSE)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    message = await ctx.send(embed=embed)
    for emoji in reactions:
        await message.add_reaction(emoji)

    try:
        reaction, user = await client.wait_for('reaction_add', timeout=45.0, check= lambda reaction, user: user == ctx.message.author and str(reaction.emoji) in reactions)

    except asyncio.TimeoutError:
        embed=discord.Embed(title='Za późno...', description=author.mention + ', Twój czas się skończył.', color=ERROR_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        await ctx.send(embed=embed)
    else:
        if str(reaction.emoji) == winner:
            embed=discord.Embed(title='🤞 Twój wybór...', description='Świetnie ' + author.mention + ', dziś Ranald wysłuchał Twej prośby!', color=SUCCESS_COLOR)
            embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
            embed.set_image(url=win_card)
        else:
            lose_card = pic.LOSE_CARDS[reactions.index(str(reaction.emoji))]
            embed=discord.Embed(title='🤞 Twój wybór...', description=author.mention + ', to był bardzo zły wybór...\n\nSzczęśliwą kartą była karta nr ' + str(winner), color=ERROR_COLOR)
            embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
            embed.set_image(url=lose_card)

        await ctx.send(embed=embed)
            

@client.command()
async def advance_table(ctx, version: str='pc'):
    if version == 'm':
        image = pic.ADVANCE_TABLE_PIC
        embed=discord.Embed(title='Koszt rozwoju cech i umiejętności w PD', description='', color=MAIN_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        embed.set_image(url=image)
    else:
        description = tab.ADV_TABLE
        embed=discord.Embed(title='Koszt rozwoju cech i umiejętności w PD', description=description, color=MAIN_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await ctx.send(embed=embed)
    
@client.command()
async def talent(ctx, *, talent_name: str):
    
    talent_name = talent_name.replace(' ','_').lower()
    
    with open('content/talents.json', encoding="utf8") as jf:
        json_data = load(jf)
        
    if talent_name in json_data:
        talent = json_data[talent_name]
        await ctx.send('Talent name found!')
        embed=discord.Embed(title=talent['name'], description=talent['description'], color=MAIN_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        embed.add_field(name="Maksimum", value=talent['max'], inline=True)
        embed.add_field(name="Testy", value=talent['tests'], inline=True)
    else:
        embed=discord.Embed(title='⚠️Nie znalazłem talentu⚠️', description='Pamiętaj o składni podanej w poleceniu **.help**.', color=ERROR_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        
    await ctx.send(embed=embed)
    
@client.command()
async def ability(ctx, *, ability_name: str):
    
    ability_name = ability_name.replace(' ','_').lower()
    
    with open('content/abilities.json', encoding="utf8") as jf:
        json_data = load(jf)
        
    if ability_name in json_data:
        ability = json_data[ability_name]
        await ctx.send('Ability name found!')
        embed=discord.Embed(title=ability['name'], description=ability['description'], color=MAIN_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        embed.add_field(name="Typ", value=ability['type'], inline=False)
        embed.add_field(name="Cecha", value=ability['attribute'], inline=False)
        embed.add_field(name="Talenty", value=ability['talents'], inline=False)
    else:
        embed=discord.Embed(title='⚠️Nie znalazłem umiejętności⚠️', description='Pamiętaj o składni podanej w poleceniu **.help**.', color=ERROR_COLOR)
        embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
        
    await ctx.send(embed=embed)

@client.command()
async def contact(ctx, *, message):
    user = client.get_user(288608916525547520)
    author = ctx.message.author
    content = '"' + message + '"' + ' by ' + str(author)
    embed=discord.Embed(title='Wiadomość wysłana', description='Treść wiadomości: *' + message + '*', color=MAIN_COLOR)
    embed.set_footer(text = FOOTER_TEXT, icon_url = pic.BOT_AVATAR)
    await user.send(content)
    await ctx.send(embed=embed)


client.add_cog(Music(client))
client.run(BOT_TOKEN)